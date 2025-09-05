// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import "../registry/AgentRegistry.sol";

/**
 * @title AgentMarketplace
 * @dev Advanced marketplace for buying, selling, and renting XRPL agents
 * @author XRPL Agent Ecosystem
 */
contract AgentMarketplace is ReentrancyGuard, Pausable, Ownable, ERC721Holder {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Listing types
    enum ListingType {
        Sale,
        Rent,
        Subscription,
        Auction
    }

    // Listing status
    enum ListingStatus {
        Active,
        Sold,
        Rented,
        Cancelled,
        Expired
    }

    // Agent listing structure
    struct AgentListing {
        uint256 listingId;
        uint256 agentId;
        address seller;
        ListingType listingType;
        ListingStatus status;
        uint256 price;
        uint256 rentPrice; // Per hour/day
        uint256 rentDuration; // In hours
        uint256 startTime;
        uint256 endTime;
        uint256 minBid; // For auctions
        uint256 currentBid;
        address currentBidder;
        bool isPublic;
        string description;
        string[] features;
        uint256[] supportedTokens;
        uint256 creationTime;
        uint256 lastUpdateTime;
    }

    // Rental agreement structure
    struct RentalAgreement {
        uint256 agreementId;
        uint256 listingId;
        address renter;
        address owner;
        uint256 startTime;
        uint256 endTime;
        uint256 totalCost;
        bool isActive;
        bool isCompleted;
        string terms;
    }

    // Subscription plan structure
    struct SubscriptionPlan {
        uint256 planId;
        uint256 agentId;
        address owner;
        uint256 monthlyPrice;
        uint256 maxExecutions;
        uint256 maxUsers;
        bool isActive;
        string planName;
        string description;
        string[] features;
    }

    // User subscription structure
    struct UserSubscription {
        uint256 subscriptionId;
        uint256 planId;
        address subscriber;
        uint256 startTime;
        uint256 endTime;
        uint256 executionsUsed;
        bool isActive;
        bool isCancelled;
    }

    // Events
    event AgentListed(
        uint256 indexed listingId,
        uint256 indexed agentId,
        address indexed seller,
        ListingType listingType,
        uint256 price
    );
    event AgentSold(
        uint256 indexed listingId,
        address indexed buyer,
        address indexed seller,
        uint256 price
    );
    event AgentRented(
        uint256 indexed listingId,
        uint256 indexed agreementId,
        address indexed renter,
        uint256 duration,
        uint256 totalCost
    );
    event BidPlaced(
        uint256 indexed listingId,
        address indexed bidder,
        uint256 bidAmount
    );
    event AuctionEnded(
        uint256 indexed listingId,
        address indexed winner,
        uint256 winningBid
    );
    event SubscriptionCreated(
        uint256 indexed planId,
        uint256 indexed agentId,
        address indexed owner,
        uint256 monthlyPrice
    );
    event SubscriptionPurchased(
        uint256 indexed subscriptionId,
        uint256 indexed planId,
        address indexed subscriber,
        uint256 duration
    );

    // State variables
    mapping(uint256 => AgentListing) public agentListings;
    mapping(uint256 => RentalAgreement) public rentalAgreements;
    mapping(uint256 => SubscriptionPlan) public subscriptionPlans;
    mapping(uint256 => UserSubscription) public userSubscriptions;
    mapping(address => uint256[]) public userListings;
    mapping(address => uint256[]) public userPurchases;
    mapping(address => uint256[]) public userRentals;
    mapping(address => uint256[]) public userSubscriptions;
    mapping(address => bool) public authorizedCurators;
    
    AgentRegistry public agentRegistry;
    IERC20 public nativeToken;
    IERC721 public agentNFT;
    
    uint256 public nextListingId = 1;
    uint256 public nextAgreementId = 1;
    uint256 public nextPlanId = 1;
    uint256 public nextSubscriptionId = 1;
    
    uint256 public totalListings = 0;
    uint256 public totalSales = 0;
    uint256 public totalVolume = 0;
    
    // Configuration
    uint256 public marketplaceFeeRate = 250; // 2.5%
    uint256 public curatorFeeRate = 100; // 1%
    uint256 public minListingPrice = 0.01 ether;
    uint256 public maxListingPrice = 1000 ether;
    uint256 public auctionDuration = 7 days;
    uint256 public rentalMaxDuration = 30 days;
    
    address public feeCollector;
    address public curatorRewardPool;

    // Modifiers
    modifier onlyAgentOwner(uint256 agentId) {
        require(agentRegistry.getAgent(agentId).owner == msg.sender, "Not agent owner");
        _;
    }

    modifier validListing(uint256 listingId) {
        require(listingId > 0 && listingId < nextListingId, "Invalid listing ID");
        _;
    }

    modifier onlyAuthorizedCurator() {
        require(authorizedCurators[msg.sender] || msg.sender == owner(), "Not authorized curator");
        _;
    }

    constructor(
        address _agentRegistry,
        address _nativeToken,
        address _agentNFT,
        address _feeCollector,
        address _curatorRewardPool
    ) {
        agentRegistry = AgentRegistry(_agentRegistry);
        nativeToken = IERC20(_nativeToken);
        agentNFT = IERC721(_agentNFT);
        feeCollector = _feeCollector;
        curatorRewardPool = _curatorRewardPool;
    }

    /**
     * @dev List an agent for sale
     */
    function listAgentForSale(
        uint256 agentId,
        uint256 price,
        bool isPublic,
        string memory description,
        string[] memory features,
        uint256[] memory supportedTokens
    ) external onlyAgentOwner(agentId) nonReentrant whenNotPaused returns (uint256 listingId) {
        require(price >= minListingPrice && price <= maxListingPrice, "Invalid price");
        require(bytes(description).length > 0, "Description required");
        
        listingId = nextListingId++;
        
        agentListings[listingId] = AgentListing({
            listingId: listingId,
            agentId: agentId,
            seller: msg.sender,
            listingType: ListingType.Sale,
            status: ListingStatus.Active,
            price: price,
            rentPrice: 0,
            rentDuration: 0,
            startTime: block.timestamp,
            endTime: 0,
            minBid: 0,
            currentBid: 0,
            currentBidder: address(0),
            isPublic: isPublic,
            description: description,
            features: features,
            supportedTokens: supportedTokens,
            creationTime: block.timestamp,
            lastUpdateTime: block.timestamp
        });
        
        userListings[msg.sender].push(listingId);
        totalListings++;
        
        emit AgentListed(listingId, agentId, msg.sender, ListingType.Sale, price);
    }

    /**
     * @dev List an agent for rent
     */
    function listAgentForRent(
        uint256 agentId,
        uint256 rentPrice,
        uint256 rentDuration,
        bool isPublic,
        string memory description,
        string[] memory features,
        uint256[] memory supportedTokens
    ) external onlyAgentOwner(agentId) nonReentrant whenNotPaused returns (uint256 listingId) {
        require(rentPrice > 0, "Invalid rent price");
        require(rentDuration > 0 && rentDuration <= rentalMaxDuration, "Invalid duration");
        require(bytes(description).length > 0, "Description required");
        
        listingId = nextListingId++;
        
        agentListings[listingId] = AgentListing({
            listingId: listingId,
            agentId: agentId,
            seller: msg.sender,
            listingType: ListingType.Rent,
            status: ListingStatus.Active,
            price: 0,
            rentPrice: rentPrice,
            rentDuration: rentDuration,
            startTime: block.timestamp,
            endTime: 0,
            minBid: 0,
            currentBid: 0,
            currentBidder: address(0),
            isPublic: isPublic,
            description: description,
            features: features,
            supportedTokens: supportedTokens,
            creationTime: block.timestamp,
            lastUpdateTime: block.timestamp
        });
        
        userListings[msg.sender].push(listingId);
        totalListings++;
        
        emit AgentListed(listingId, agentId, msg.sender, ListingType.Rent, rentPrice);
    }

    /**
     * @dev List an agent for auction
     */
    function listAgentForAuction(
        uint256 agentId,
        uint256 minBid,
        uint256 duration,
        bool isPublic,
        string memory description,
        string[] memory features,
        uint256[] memory supportedTokens
    ) external onlyAgentOwner(agentId) nonReentrant whenNotPaused returns (uint256 listingId) {
        require(minBid >= minListingPrice, "Invalid minimum bid");
        require(duration > 0 && duration <= auctionDuration, "Invalid duration");
        require(bytes(description).length > 0, "Description required");
        
        listingId = nextListingId++;
        
        agentListings[listingId] = AgentListing({
            listingId: listingId,
            agentId: agentId,
            seller: msg.sender,
            listingType: ListingType.Auction,
            status: ListingStatus.Active,
            price: 0,
            rentPrice: 0,
            rentDuration: 0,
            startTime: block.timestamp,
            endTime: block.timestamp + duration,
            minBid: minBid,
            currentBid: 0,
            currentBidder: address(0),
            isPublic: isPublic,
            description: description,
            features: features,
            supportedTokens: supportedTokens,
            creationTime: block.timestamp,
            lastUpdateTime: block.timestamp
        });
        
        userListings[msg.sender].push(listingId);
        totalListings++;
        
        emit AgentListed(listingId, agentId, msg.sender, ListingType.Auction, minBid);
    }

    /**
     * @dev Buy an agent
     */
    function buyAgent(uint256 listingId) external payable nonReentrant whenNotPaused {
        AgentListing storage listing = agentListings[listingId];
        
        require(listing.status == ListingStatus.Active, "Listing not active");
        require(listing.listingType == ListingType.Sale, "Not for sale");
        require(msg.value >= listing.price, "Insufficient payment");
        require(listing.isPublic || msg.sender == listing.seller, "Listing not public");
        
        listing.status = ListingStatus.Sold;
        listing.lastUpdateTime = block.timestamp;
        
        // Calculate fees
        uint256 marketplaceFee = listing.price.mul(marketplaceFeeRate).div(10000);
        uint256 curatorFee = listing.price.mul(curatorFeeRate).div(10000);
        uint256 sellerAmount = listing.price.sub(marketplaceFee).sub(curatorFee);
        
        // Transfer payments
        payable(listing.seller).transfer(sellerAmount);
        payable(feeCollector).transfer(marketplaceFee);
        payable(curatorRewardPool).transfer(curatorFee);
        
        // Transfer agent ownership (simplified - would need proper agent transfer logic)
        userPurchases[msg.sender].push(listingId);
        totalSales++;
        totalVolume = totalVolume.add(listing.price);
        
        emit AgentSold(listingId, msg.sender, listing.seller, listing.price);
    }

    /**
     * @dev Rent an agent
     */
    function rentAgent(
        uint256 listingId,
        uint256 duration,
        string memory terms
    ) external payable nonReentrant whenNotPaused returns (uint256 agreementId) {
        AgentListing storage listing = agentListings[listingId];
        
        require(listing.status == ListingStatus.Active, "Listing not active");
        require(listing.listingType == ListingType.Rent, "Not for rent");
        require(duration > 0 && duration <= listing.rentDuration, "Invalid duration");
        require(listing.isPublic || msg.sender == listing.seller, "Listing not public");
        
        uint256 totalCost = listing.rentPrice.mul(duration);
        require(msg.value >= totalCost, "Insufficient payment");
        
        agreementId = nextAgreementId++;
        
        rentalAgreements[agreementId] = RentalAgreement({
            agreementId: agreementId,
            listingId: listingId,
            renter: msg.sender,
            owner: listing.seller,
            startTime: block.timestamp,
            endTime: block.timestamp + duration,
            totalCost: totalCost,
            isActive: true,
            isCompleted: false,
            terms: terms
        });
        
        // Calculate fees
        uint256 marketplaceFee = totalCost.mul(marketplaceFeeRate).div(10000);
        uint256 curatorFee = totalCost.mul(curatorFeeRate).div(10000);
        uint256 ownerAmount = totalCost.sub(marketplaceFee).sub(curatorFee);
        
        // Transfer payments
        payable(listing.seller).transfer(ownerAmount);
        payable(feeCollector).transfer(marketplaceFee);
        payable(curatorRewardPool).transfer(curatorFee);
        
        userRentals[msg.sender].push(agreementId);
        totalVolume = totalVolume.add(totalCost);
        
        emit AgentRented(listingId, agreementId, msg.sender, duration, totalCost);
    }

    /**
     * @dev Place a bid on an auction
     */
    function placeBid(uint256 listingId) external payable nonReentrant whenNotPaused {
        AgentListing storage listing = agentListings[listingId];
        
        require(listing.status == ListingStatus.Active, "Listing not active");
        require(listing.listingType == ListingType.Auction, "Not an auction");
        require(block.timestamp < listing.endTime, "Auction ended");
        require(msg.value >= listing.minBid, "Bid too low");
        require(msg.value > listing.currentBid, "Bid too low");
        require(listing.isPublic || msg.sender == listing.seller, "Listing not public");
        
        // Refund previous bidder
        if (listing.currentBidder != address(0)) {
            payable(listing.currentBidder).transfer(listing.currentBid);
        }
        
        listing.currentBid = msg.value;
        listing.currentBidder = msg.sender;
        listing.lastUpdateTime = block.timestamp;
        
        emit BidPlaced(listingId, msg.sender, msg.value);
    }

    /**
     * @dev End an auction
     */
    function endAuction(uint256 listingId) external nonReentrant whenNotPaused {
        AgentListing storage listing = agentListings[listingId];
        
        require(listing.status == ListingStatus.Active, "Listing not active");
        require(listing.listingType == ListingType.Auction, "Not an auction");
        require(block.timestamp >= listing.endTime, "Auction not ended");
        require(msg.sender == listing.seller || msg.sender == owner(), "Not authorized");
        
        if (listing.currentBidder != address(0)) {
            listing.status = ListingStatus.Sold;
            
            // Calculate fees
            uint256 marketplaceFee = listing.currentBid.mul(marketplaceFeeRate).div(10000);
            uint256 curatorFee = listing.currentBid.mul(curatorFeeRate).div(10000);
            uint256 sellerAmount = listing.currentBid.sub(marketplaceFee).sub(curatorFee);
            
            // Transfer payments
            payable(listing.seller).transfer(sellerAmount);
            payable(feeCollector).transfer(marketplaceFee);
            payable(curatorRewardPool).transfer(curatorFee);
            
            userPurchases[listing.currentBidder].push(listingId);
            totalSales++;
            totalVolume = totalVolume.add(listing.currentBid);
            
            emit AuctionEnded(listingId, listing.currentBidder, listing.currentBid);
        } else {
            listing.status = ListingStatus.Expired;
        }
        
        listing.lastUpdateTime = block.timestamp;
    }

    /**
     * @dev Create a subscription plan
     */
    function createSubscriptionPlan(
        uint256 agentId,
        uint256 monthlyPrice,
        uint256 maxExecutions,
        uint256 maxUsers,
        string memory planName,
        string memory description,
        string[] memory features
    ) external onlyAgentOwner(agentId) nonReentrant whenNotPaused returns (uint256 planId) {
        require(monthlyPrice > 0, "Invalid price");
        require(maxExecutions > 0, "Invalid max executions");
        require(maxUsers > 0, "Invalid max users");
        require(bytes(planName).length > 0, "Plan name required");
        require(bytes(description).length > 0, "Description required");
        
        planId = nextPlanId++;
        
        subscriptionPlans[planId] = SubscriptionPlan({
            planId: planId,
            agentId: agentId,
            owner: msg.sender,
            monthlyPrice: monthlyPrice,
            maxExecutions: maxExecutions,
            maxUsers: maxUsers,
            isActive: true,
            planName: planName,
            description: description,
            features: features
        });
        
        emit SubscriptionCreated(planId, agentId, msg.sender, monthlyPrice);
    }

    /**
     * @dev Purchase a subscription
     */
    function purchaseSubscription(
        uint256 planId,
        uint256 duration // In months
    ) external payable nonReentrant whenNotPaused returns (uint256 subscriptionId) {
        SubscriptionPlan storage plan = subscriptionPlans[planId];
        
        require(plan.isActive, "Plan not active");
        require(duration > 0, "Invalid duration");
        
        uint256 totalCost = plan.monthlyPrice.mul(duration);
        require(msg.value >= totalCost, "Insufficient payment");
        
        subscriptionId = nextSubscriptionId++;
        
        userSubscriptions[subscriptionId] = UserSubscription({
            subscriptionId: subscriptionId,
            planId: planId,
            subscriber: msg.sender,
            startTime: block.timestamp,
            endTime: block.timestamp + (duration * 30 days),
            executionsUsed: 0,
            isActive: true,
            isCancelled: false
        });
        
        // Calculate fees
        uint256 marketplaceFee = totalCost.mul(marketplaceFeeRate).div(10000);
        uint256 curatorFee = totalCost.mul(curatorFeeRate).div(10000);
        uint256 ownerAmount = totalCost.sub(marketplaceFee).sub(curatorFee);
        
        // Transfer payments
        payable(plan.owner).transfer(ownerAmount);
        payable(feeCollector).transfer(marketplaceFee);
        payable(curatorRewardPool).transfer(curatorFee);
        
        userSubscriptions[msg.sender].push(subscriptionId);
        totalVolume = totalVolume.add(totalCost);
        
        emit SubscriptionPurchased(subscriptionId, planId, msg.sender, duration);
    }

    /**
     * @dev Cancel a listing
     */
    function cancelListing(uint256 listingId) external validListing(listingId) {
        AgentListing storage listing = agentListings[listingId];
        
        require(msg.sender == listing.seller || msg.sender == owner(), "Not authorized");
        require(listing.status == ListingStatus.Active, "Listing not active");
        
        // Refund current bidder if auction
        if (listing.listingType == ListingType.Auction && listing.currentBidder != address(0)) {
            payable(listing.currentBidder).transfer(listing.currentBid);
        }
        
        listing.status = ListingStatus.Cancelled;
        listing.lastUpdateTime = block.timestamp;
    }

    /**
     * @dev Complete a rental agreement
     */
    function completeRental(uint256 agreementId) external {
        RentalAgreement storage agreement = rentalAgreements[agreementId];
        
        require(msg.sender == agreement.renter || msg.sender == agreement.owner, "Not authorized");
        require(agreement.isActive, "Agreement not active");
        require(block.timestamp >= agreement.endTime, "Rental not ended");
        
        agreement.isActive = false;
        agreement.isCompleted = true;
    }

    /**
     * @dev Get listing details
     */
    function getListing(uint256 listingId) external view validListing(listingId) returns (AgentListing memory) {
        return agentListings[listingId];
    }

    /**
     * @dev Get rental agreement
     */
    function getRentalAgreement(uint256 agreementId) external view returns (RentalAgreement memory) {
        require(agreementId > 0 && agreementId < nextAgreementId, "Invalid agreement ID");
        return rentalAgreements[agreementId];
    }

    /**
     * @dev Get subscription plan
     */
    function getSubscriptionPlan(uint256 planId) external view returns (SubscriptionPlan memory) {
        require(planId > 0 && planId < nextPlanId, "Invalid plan ID");
        return subscriptionPlans[planId];
    }

    /**
     * @dev Get user subscription
     */
    function getUserSubscription(uint256 subscriptionId) external view returns (UserSubscription memory) {
        require(subscriptionId > 0 && subscriptionId < nextSubscriptionId, "Invalid subscription ID");
        return userSubscriptions[subscriptionId];
    }

    /**
     * @dev Search listings
     */
    function searchListings(
        string memory query,
        ListingType listingType,
        uint256 minPrice,
        uint256 maxPrice
    ) external view returns (uint256[] memory) {
        uint256[] memory results = new uint256[](totalListings);
        uint256 count = 0;
        
        for (uint256 i = 1; i < nextListingId; i++) {
            AgentListing memory listing = agentListings[i];
            
            if (listing.status == ListingStatus.Active) {
                if (listingType == ListingType.Sale || listing.listingType == listingType) {
                    if (listing.price >= minPrice && listing.price <= maxPrice) {
                        // Simple string matching - could be enhanced
                        if (bytes(listing.description).length > 0) {
                            results[count] = i;
                            count++;
                        }
                    }
                }
            }
        }
        
        // Resize array
        uint256[] memory finalResults = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            finalResults[i] = results[i];
        }
        
        return finalResults;
    }

    /**
     * @dev Authorize curator
     */
    function authorizeCurator(address curator) external onlyOwner {
        authorizedCurators[curator] = true;
    }

    /**
     * @dev Revoke curator authorization
     */
    function revokeCurator(address curator) external onlyOwner {
        authorizedCurators[curator] = false;
    }

    /**
     * @dev Set configuration parameters
     */
    function setConfig(
        uint256 _marketplaceFeeRate,
        uint256 _curatorFeeRate,
        uint256 _minListingPrice,
        uint256 _maxListingPrice,
        uint256 _auctionDuration,
        uint256 _rentalMaxDuration
    ) external onlyOwner {
        marketplaceFeeRate = _marketplaceFeeRate;
        curatorFeeRate = _curatorFeeRate;
        minListingPrice = _minListingPrice;
        maxListingPrice = _maxListingPrice;
        auctionDuration = _auctionDuration;
        rentalMaxDuration = _rentalMaxDuration;
    }

    /**
     * @dev Set fee collector
     */
    function setFeeCollector(address _feeCollector) external onlyOwner {
        require(_feeCollector != address(0), "Invalid address");
        feeCollector = _feeCollector;
    }

    /**
     * @dev Set curator reward pool
     */
    function setCuratorRewardPool(address _curatorRewardPool) external onlyOwner {
        require(_curatorRewardPool != address(0), "Invalid address");
        curatorRewardPool = _curatorRewardPool;
    }

    /**
     * @dev Pause contract
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Emergency withdraw
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        if (token == address(0)) {
            payable(owner()).transfer(amount);
        } else {
            IERC20(token).safeTransfer(owner(), amount);
        }
    }

    /**
     * @dev Receive ETH
     */
    receive() external payable {
        // Allow contract to receive ETH for payments
    }
}
