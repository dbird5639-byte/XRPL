// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title XRPLNFTMarketplace
 * @dev NFT marketplace for XRPL with trading fees and auction functionality
 * @author XRPL Ecosystem
 */
contract XRPLNFTMarketplace is ReentrancyGuard, Pausable, Ownable, IERC721Receiver {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;
    using Counters for Counters.Counter;

    struct Listing {
        uint256 id;
        address nftContract;
        uint256 tokenId;
        address seller;
        address paymentToken;
        uint256 price;
        uint256 startTime;
        uint256 endTime;
        bool active;
        bool isAuction;
        address highestBidder;
        uint256 highestBid;
        uint256 reservePrice;
    }

    struct Offer {
        uint256 id;
        address nftContract;
        uint256 tokenId;
        address offerer;
        address paymentToken;
        uint256 amount;
        uint256 expirationTime;
        bool active;
    }

    struct Collection {
        address nftContract;
        string name;
        string symbol;
        address creator;
        uint256 royaltyFee; // Basis points
        bool verified;
        uint256 totalVolume;
        uint256 totalSales;
    }

    // Events
    event NFTListed(uint256 indexed listingId, address nftContract, uint256 tokenId, address seller, uint256 price);
    event NFTSold(uint256 indexed listingId, address buyer, uint256 price, uint256 fee);
    event NFTAuctionStarted(uint256 indexed listingId, uint256 reservePrice, uint256 endTime);
    event BidPlaced(uint256 indexed listingId, address bidder, uint256 amount);
    event AuctionEnded(uint256 indexed listingId, address winner, uint256 winningBid);
    event OfferMade(uint256 indexed offerId, address offerer, uint256 amount);
    event OfferAccepted(uint256 indexed offerId, address seller);
    event CollectionRegistered(address indexed nftContract, string name, address creator);
    event RoyaltyPaid(address indexed creator, uint256 amount);

    // State variables
    mapping(uint256 => Listing) public listings;
    mapping(uint256 => Offer) public offers;
    mapping(address => Collection) public collections;
    mapping(address => bool) public authorizedNFTs;
    mapping(address => bool) public authorizedTokens;
    mapping(address => uint256) public userListings;
    mapping(address => uint256) public userOffers;
    mapping(address => uint256) public userSales;
    mapping(address => uint256) public userPurchases;
    
    Counters.Counter private _listingIdCounter;
    Counters.Counter private _offerIdCounter;
    
    uint256 public constant MAX_ROYALTY_FEE = 1000; // 10%
    uint256 public constant PLATFORM_FEE_RATE = 250; // 2.5%
    uint256 public constant MIN_AUCTION_DURATION = 1 hours;
    uint256 public constant MAX_AUCTION_DURATION = 7 days;
    
    address public feeCollector;
    uint256 public totalPlatformFees;
    uint256 public totalVolume;

    // Modifiers
    modifier onlyAuthorizedNFT(address nftContract) {
        require(authorizedNFTs[nftContract], "NFT contract not authorized");
        _;
    }

    modifier onlyAuthorizedToken(address token) {
        require(authorizedTokens[token], "Token not authorized");
        _;
    }

    modifier validListing(uint256 listingId) {
        require(listingId > 0 && listingId <= _listingIdCounter.current(), "Invalid listing ID");
        _;
    }

    modifier validOffer(uint256 offerId) {
        require(offerId > 0 && offerId <= _offerIdCounter.current(), "Invalid offer ID");
        _;
    }

    constructor(address _feeCollector) {
        feeCollector = _feeCollector;
    }

    /**
     * @dev List an NFT for sale
     */
    function listNFT(
        address nftContract,
        uint256 tokenId,
        address paymentToken,
        uint256 price
    ) external nonReentrant onlyAuthorizedNFT(nftContract) onlyAuthorizedToken(paymentToken) returns (uint256 listingId) {
        require(price > 0, "Price must be greater than 0");
        require(IERC721(nftContract).ownerOf(tokenId) == msg.sender, "Not the owner");
        require(IERC721(nftContract).getApproved(tokenId) == address(this) || 
                IERC721(nftContract).isApprovedForAll(msg.sender, address(this)), "Not approved");

        _listingIdCounter.increment();
        listingId = _listingIdCounter.current();

        listings[listingId] = Listing({
            id: listingId,
            nftContract: nftContract,
            tokenId: tokenId,
            seller: msg.sender,
            paymentToken: paymentToken,
            price: price,
            startTime: block.timestamp,
            endTime: 0,
            active: true,
            isAuction: false,
            highestBidder: address(0),
            highestBid: 0,
            reservePrice: 0
        });

        // Transfer NFT to contract
        IERC721(nftContract).safeTransferFrom(msg.sender, address(this), tokenId);

        userListings[msg.sender] = userListings[msg.sender].add(1);

        emit NFTListed(listingId, nftContract, tokenId, msg.sender, price);
    }

    /**
     * @dev Start an auction for an NFT
     */
    function startAuction(
        address nftContract,
        uint256 tokenId,
        address paymentToken,
        uint256 reservePrice,
        uint256 duration
    ) external nonReentrant onlyAuthorizedNFT(nftContract) onlyAuthorizedToken(paymentToken) returns (uint256 listingId) {
        require(reservePrice > 0, "Reserve price must be greater than 0");
        require(duration >= MIN_AUCTION_DURATION && duration <= MAX_AUCTION_DURATION, "Invalid duration");
        require(IERC721(nftContract).ownerOf(tokenId) == msg.sender, "Not the owner");
        require(IERC721(nftContract).getApproved(tokenId) == address(this) || 
                IERC721(nftContract).isApprovedForAll(msg.sender, address(this)), "Not approved");

        _listingIdCounter.increment();
        listingId = _listingIdCounter.current();

        listings[listingId] = Listing({
            id: listingId,
            nftContract: nftContract,
            tokenId: tokenId,
            seller: msg.sender,
            paymentToken: paymentToken,
            price: 0,
            startTime: block.timestamp,
            endTime: block.timestamp.add(duration),
            active: true,
            isAuction: true,
            highestBidder: address(0),
            highestBid: 0,
            reservePrice: reservePrice
        });

        // Transfer NFT to contract
        IERC721(nftContract).safeTransferFrom(msg.sender, address(this), tokenId);

        userListings[msg.sender] = userListings[msg.sender].add(1);

        emit NFTAuctionStarted(listingId, reservePrice, block.timestamp.add(duration));
    }

    /**
     * @dev Buy an NFT
     */
    function buyNFT(uint256 listingId) external nonReentrant validListing(listingId) {
        Listing storage listing = listings[listingId];
        require(listing.active, "Listing not active");
        require(!listing.isAuction, "This is an auction");
        require(msg.sender != listing.seller, "Cannot buy your own NFT");

        uint256 totalPrice = listing.price;
        uint256 platformFee = totalPrice.mul(PLATFORM_FEE_RATE).div(10000);
        uint256 royaltyFee = 0;
        uint256 sellerAmount = totalPrice.sub(platformFee);

        // Calculate royalty fee if collection is registered
        if (collections[listing.nftContract].creator != address(0)) {
            royaltyFee = totalPrice.mul(collections[listing.nftContract].royaltyFee).div(10000);
            sellerAmount = sellerAmount.sub(royaltyFee);
        }

        // Transfer payment token from buyer to contract
        IERC20(listing.paymentToken).safeTransferFrom(msg.sender, address(this), totalPrice);

        // Transfer NFT to buyer
        IERC721(listing.nftContract).safeTransferFrom(address(this), msg.sender, listing.tokenId);

        // Distribute funds
        IERC20(listing.paymentToken).safeTransfer(listing.seller, sellerAmount);
        IERC20(listing.paymentToken).safeTransfer(feeCollector, platformFee);
        
        if (royaltyFee > 0) {
            IERC20(listing.paymentToken).safeTransfer(collections[listing.nftContract].creator, royaltyFee);
            emit RoyaltyPaid(collections[listing.nftContract].creator, royaltyFee);
        }

        // Update listing
        listing.active = false;

        // Update statistics
        totalVolume = totalVolume.add(totalPrice);
        totalPlatformFees = totalPlatformFees.add(platformFee);
        userSales[listing.seller] = userSales[listing.seller].add(1);
        userPurchases[msg.sender] = userPurchases[msg.sender].add(1);
        collections[listing.nftContract].totalVolume = collections[listing.nftContract].totalVolume.add(totalPrice);
        collections[listing.nftContract].totalSales = collections[listing.nftContract].totalSales.add(1);

        emit NFTSold(listingId, msg.sender, totalPrice, platformFee);
    }

    /**
     * @dev Place a bid on an auction
     */
    function placeBid(uint256 listingId, uint256 amount) external nonReentrant validListing(listingId) {
        Listing storage listing = listings[listingId];
        require(listing.active, "Listing not active");
        require(listing.isAuction, "This is not an auction");
        require(block.timestamp < listing.endTime, "Auction ended");
        require(msg.sender != listing.seller, "Cannot bid on your own NFT");
        require(amount > listing.highestBid, "Bid too low");
        require(amount >= listing.reservePrice, "Bid below reserve price");

        // Refund previous highest bidder
        if (listing.highestBidder != address(0)) {
            IERC20(listing.paymentToken).safeTransfer(listing.highestBidder, listing.highestBid);
        }

        // Transfer new bid to contract
        IERC20(listing.paymentToken).safeTransferFrom(msg.sender, address(this), amount);

        // Update highest bid
        listing.highestBidder = msg.sender;
        listing.highestBid = amount;

        emit BidPlaced(listingId, msg.sender, amount);
    }

    /**
     * @dev End an auction
     */
    function endAuction(uint256 listingId) external nonReentrant validListing(listingId) {
        Listing storage listing = listings[listingId];
        require(listing.active, "Listing not active");
        require(listing.isAuction, "This is not an auction");
        require(block.timestamp >= listing.endTime, "Auction not ended");
        require(listing.highestBidder != address(0), "No bids placed");

        uint256 totalPrice = listing.highestBid;
        uint256 platformFee = totalPrice.mul(PLATFORM_FEE_RATE).div(10000);
        uint256 royaltyFee = 0;
        uint256 sellerAmount = totalPrice.sub(platformFee);

        // Calculate royalty fee if collection is registered
        if (collections[listing.nftContract].creator != address(0)) {
            royaltyFee = totalPrice.mul(collections[listing.nftContract].royaltyFee).div(10000);
            sellerAmount = sellerAmount.sub(royaltyFee);
        }

        // Transfer NFT to winner
        IERC721(listing.nftContract).safeTransferFrom(address(this), listing.highestBidder, listing.tokenId);

        // Distribute funds
        IERC20(listing.paymentToken).safeTransfer(listing.seller, sellerAmount);
        IERC20(listing.paymentToken).safeTransfer(feeCollector, platformFee);
        
        if (royaltyFee > 0) {
            IERC20(listing.paymentToken).safeTransfer(collections[listing.nftContract].creator, royaltyFee);
            emit RoyaltyPaid(collections[listing.nftContract].creator, royaltyFee);
        }

        // Update listing
        listing.active = false;

        // Update statistics
        totalVolume = totalVolume.add(totalPrice);
        totalPlatformFees = totalPlatformFees.add(platformFee);
        userSales[listing.seller] = userSales[listing.seller].add(1);
        userPurchases[listing.highestBidder] = userPurchases[listing.highestBidder].add(1);
        collections[listing.nftContract].totalVolume = collections[listing.nftContract].totalVolume.add(totalPrice);
        collections[listing.nftContract].totalSales = collections[listing.nftContract].totalSales.add(1);

        emit AuctionEnded(listingId, listing.highestBidder, listing.highestBid);
    }

    /**
     * @dev Make an offer on an NFT
     */
    function makeOffer(
        address nftContract,
        uint256 tokenId,
        address paymentToken,
        uint256 amount,
        uint256 expirationTime
    ) external nonReentrant onlyAuthorizedNFT(nftContract) onlyAuthorizedToken(paymentToken) returns (uint256 offerId) {
        require(amount > 0, "Amount must be greater than 0");
        require(expirationTime > block.timestamp, "Invalid expiration time");
        require(IERC721(nftContract).ownerOf(tokenId) != msg.sender, "Cannot offer on your own NFT");

        _offerIdCounter.increment();
        offerId = _offerIdCounter.current();

        offers[offerId] = Offer({
            id: offerId,
            nftContract: nftContract,
            tokenId: tokenId,
            offerer: msg.sender,
            paymentToken: paymentToken,
            amount: amount,
            expirationTime: expirationTime,
            active: true
        });

        // Transfer offer amount to contract
        IERC20(paymentToken).safeTransferFrom(msg.sender, address(this), amount);

        userOffers[msg.sender] = userOffers[msg.sender].add(1);

        emit OfferMade(offerId, msg.sender, amount);
    }

    /**
     * @dev Accept an offer
     */
    function acceptOffer(uint256 offerId) external nonReentrant validOffer(offerId) {
        Offer storage offer = offers[offerId];
        require(offer.active, "Offer not active");
        require(block.timestamp < offer.expirationTime, "Offer expired");
        require(IERC721(offer.nftContract).ownerOf(offer.tokenId) == msg.sender, "Not the owner");
        require(IERC721(offer.nftContract).getApproved(offer.tokenId) == address(this) || 
                IERC721(offer.nftContract).isApprovedForAll(msg.sender, address(this)), "Not approved");

        uint256 totalPrice = offer.amount;
        uint256 platformFee = totalPrice.mul(PLATFORM_FEE_RATE).div(10000);
        uint256 royaltyFee = 0;
        uint256 sellerAmount = totalPrice.sub(platformFee);

        // Calculate royalty fee if collection is registered
        if (collections[offer.nftContract].creator != address(0)) {
            royaltyFee = totalPrice.mul(collections[offer.nftContract].royaltyFee).div(10000);
            sellerAmount = sellerAmount.sub(royaltyFee);
        }

        // Transfer NFT to offerer
        IERC721(offer.nftContract).safeTransferFrom(msg.sender, offer.offerer, offer.tokenId);

        // Distribute funds
        IERC20(offer.paymentToken).safeTransfer(msg.sender, sellerAmount);
        IERC20(offer.paymentToken).safeTransfer(feeCollector, platformFee);
        
        if (royaltyFee > 0) {
            IERC20(offer.paymentToken).safeTransfer(collections[offer.nftContract].creator, royaltyFee);
            emit RoyaltyPaid(collections[offer.nftContract].creator, royaltyFee);
        }

        // Update offer
        offer.active = false;

        // Update statistics
        totalVolume = totalVolume.add(totalPrice);
        totalPlatformFees = totalPlatformFees.add(platformFee);
        userSales[msg.sender] = userSales[msg.sender].add(1);
        userPurchases[offer.offerer] = userPurchases[offer.offerer].add(1);
        collections[offer.nftContract].totalVolume = collections[offer.nftContract].totalVolume.add(totalPrice);
        collections[offer.nftContract].totalSales = collections[offer.nftContract].totalSales.add(1);

        emit OfferAccepted(offerId, msg.sender);
    }

    /**
     * @dev Cancel a listing
     */
    function cancelListing(uint256 listingId) external nonReentrant validListing(listingId) {
        Listing storage listing = listings[listingId];
        require(listing.active, "Listing not active");
        require(listing.seller == msg.sender, "Not the seller");
        require(!listing.isAuction || listing.highestBidder == address(0), "Auction has bids");

        // Transfer NFT back to seller
        IERC721(listing.nftContract).safeTransferFrom(address(this), listing.seller, listing.tokenId);

        // Refund highest bidder if auction
        if (listing.isAuction && listing.highestBidder != address(0)) {
            IERC20(listing.paymentToken).safeTransfer(listing.highestBidder, listing.highestBid);
        }

        // Update listing
        listing.active = false;
    }

    /**
     * @dev Cancel an offer
     */
    function cancelOffer(uint256 offerId) external nonReentrant validOffer(offerId) {
        Offer storage offer = offers[offerId];
        require(offer.active, "Offer not active");
        require(offer.offerer == msg.sender, "Not the offerer");

        // Refund offerer
        IERC20(offer.paymentToken).safeTransfer(offer.offerer, offer.amount);

        // Update offer
        offer.active = false;
    }

    /**
     * @dev Register a collection
     */
    function registerCollection(
        address nftContract,
        string memory name,
        string memory symbol,
        uint256 royaltyFee
    ) external onlyOwner {
        require(royaltyFee <= MAX_ROYALTY_FEE, "Royalty fee too high");
        require(collections[nftContract].creator == address(0), "Collection already registered");

        collections[nftContract] = Collection({
            nftContract: nftContract,
            name: name,
            symbol: symbol,
            creator: msg.sender,
            royaltyFee: royaltyFee,
            verified: true,
            totalVolume: 0,
            totalSales: 0
        });

        emit CollectionRegistered(nftContract, name, msg.sender);
    }

    /**
     * @dev Get listing details
     */
    function getListing(uint256 listingId) external view validListing(listingId) returns (Listing memory) {
        return listings[listingId];
    }

    /**
     * @dev Get offer details
     */
    function getOffer(uint256 offerId) external view validOffer(offerId) returns (Offer memory) {
        return offers[offerId];
    }

    /**
     * @dev Get collection details
     */
    function getCollection(address nftContract) external view returns (Collection memory) {
        return collections[nftContract];
    }

    /**
     * @dev Authorize an NFT contract
     */
    function authorizeNFT(address nftContract) external onlyOwner {
        authorizedNFTs[nftContract] = true;
    }

    /**
     * @dev Authorize a payment token
     */
    function authorizeToken(address token) external onlyOwner {
        authorizedTokens[token] = true;
    }

    /**
     * @dev Set fee collector address
     */
    function setFeeCollector(address _feeCollector) external onlyOwner {
        require(_feeCollector != address(0), "Invalid address");
        feeCollector = _feeCollector;
    }

    /**
     * @dev Pause the contract
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause the contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Emergency withdraw
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }

    /**
     * @dev Required for receiving NFTs
     */
    function onERC721Received(
        address,
        address,
        uint256,
        bytes memory
    ) public virtual override returns (bytes4) {
        return this.onERC721Received.selector;
    }
}
