// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title NFTMarketplace
 * @dev Comprehensive NFT marketplace with minting, trading, auctions, and energy-based NFTs
 * @author XRPL EVM Sidechain
 */
contract NFTMarketplace is 
    ERC721, 
    ERC721Enumerable, 
    ERC721URIStorage, 
    ReentrancyGuard, 
    Pausable, 
    Ownable 
{
    using SafeERC20 for IERC20;
    using SafeMath for uint256;
    using Counters for Counters.Counter;

    // Structs
    struct NFTListing {
        address seller;
        address token;
        uint256 price;
        bool active;
        uint256 timestamp;
        uint256 energyLevel;
        uint256 rarity;
    }

    struct Auction {
        address seller;
        address token;
        uint256 startingPrice;
        uint256 currentBid;
        address currentBidder;
        uint256 endTime;
        bool active;
        uint256 energyLevel;
        uint256 rarity;
    }

    struct EnergyNFT {
        uint256 energyLevel;
        uint256 maxEnergy;
        uint256 lastRecharge;
        uint256 rechargeRate;
        uint256 rarity;
        string energyType;
        bool isActive;
    }

    struct Collection {
        string name;
        string symbol;
        string baseURI;
        address creator;
        uint256 maxSupply;
        uint256 currentSupply;
        bool active;
        uint256 mintPrice;
        uint256 royaltyRate;
    }

    // Events
    event NFTListed(uint256 indexed tokenId, address seller, address token, uint256 price, uint256 energyLevel);
    event NFTSold(uint256 indexed tokenId, address seller, address buyer, uint256 price);
    event AuctionCreated(uint256 indexed tokenId, address seller, uint256 startingPrice, uint256 endTime);
    event BidPlaced(uint256 indexed tokenId, address bidder, uint256 bid);
    event AuctionEnded(uint256 indexed tokenId, address winner, uint256 finalBid);
    event NFTMinted(uint256 indexed tokenId, address to, uint256 energyLevel, uint256 rarity);
    event EnergyRecharged(uint256 indexed tokenId, uint256 newEnergyLevel);
    event CollectionCreated(uint256 indexed collectionId, string name, address creator);
    event RoyaltyPaid(uint256 indexed tokenId, address creator, uint256 amount);

    // State variables
    Counters.Counter private _tokenIdCounter;
    Counters.Counter private _collectionIdCounter;
    
    mapping(uint256 => NFTListing) public listings;
    mapping(uint256 => Auction) public auctions;
    mapping(uint256 => EnergyNFT) public energyNFTs;
    mapping(uint256 => Collection) public collections;
    mapping(address => uint256) public userBalances;
    mapping(address => bool) public authorizedTokens;
    mapping(address => bool) public authorizedMinters;
    mapping(uint256 => uint256) public tokenToCollection;
    
    uint256 public constant MAX_ENERGY = 100;
    uint256 public constant MIN_ENERGY = 0;
    uint256 public constant RECHARGE_RATE = 1; // Energy per hour
    uint256 public constant MARKETPLACE_FEE_RATE = 250; // 2.5%
    uint256 public constant MAX_ROYALTY_RATE = 1000; // 10%
    
    address public feeCollector;
    address public energyToken;
    uint256 public totalVolume;
    uint256 public totalFees;

    // Modifiers
    modifier onlyAuthorizedToken(address token) {
        require(authorizedTokens[token], "Token not authorized");
        _;
    }

    modifier onlyAuthorizedMinter() {
        require(authorizedMinters[msg.sender] || msg.sender == owner(), "Not authorized to mint");
        _;
    }

    modifier validToken(uint256 tokenId) {
        require(_exists(tokenId), "Token does not exist");
        _;
    }

    constructor(
        string memory name,
        string memory symbol,
        address _feeCollector,
        address _energyToken
    ) ERC721(name, symbol) {
        feeCollector = _feeCollector;
        energyToken = _energyToken;
    }

    /**
     * @dev Mint a new NFT with energy properties
     */
    function mintNFT(
        address to,
        string memory uri,
        uint256 collectionId,
        uint256 energyLevel,
        uint256 rarity,
        string memory energyType
    ) external onlyAuthorizedMinter returns (uint256) {
        require(collections[collectionId].active, "Collection not active");
        require(collections[collectionId].currentSupply < collections[collectionId].maxSupply, "Max supply reached");
        require(energyLevel <= MAX_ENERGY, "Energy level too high");
        require(energyLevel >= MIN_ENERGY, "Energy level too low");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);

        energyNFTs[tokenId] = EnergyNFT({
            energyLevel: energyLevel,
            maxEnergy: MAX_ENERGY,
            lastRecharge: block.timestamp,
            rechargeRate: RECHARGE_RATE,
            rarity: rarity,
            energyType: energyType,
            isActive: true
        });

        tokenToCollection[tokenId] = collectionId;
        collections[collectionId].currentSupply++;

        emit NFTMinted(tokenId, to, energyLevel, rarity);
        return tokenId;
    }

    /**
     * @dev List an NFT for sale
     */
    function listNFT(
        uint256 tokenId,
        address token,
        uint256 price
    ) external nonReentrant validToken(tokenId) onlyAuthorizedToken(token) {
        require(ownerOf(tokenId) == msg.sender, "Not the owner");
        require(!listings[tokenId].active, "Already listed");
        require(!auctions[tokenId].active, "Currently in auction");
        require(price > 0, "Price must be positive");

        listings[tokenId] = NFTListing({
            seller: msg.sender,
            token: token,
            price: price,
            active: true,
            timestamp: block.timestamp,
            energyLevel: energyNFTs[tokenId].energyLevel,
            rarity: energyNFTs[tokenId].rarity
        });

        emit NFTListed(tokenId, msg.sender, token, price, energyNFTs[tokenId].energyLevel);
    }

    /**
     * @dev Buy a listed NFT
     */
    function buyNFT(uint256 tokenId) external nonReentrant validToken(tokenId) {
        NFTListing storage listing = listings[tokenId];
        require(listing.active, "Not for sale");
        require(msg.sender != listing.seller, "Cannot buy own NFT");

        uint256 fee = listing.price.mul(MARKETPLACE_FEE_RATE).div(10000);
        uint256 royalty = calculateRoyalty(tokenId, listing.price);
        uint256 sellerAmount = listing.price.sub(fee).sub(royalty);

        IERC20(listing.token).safeTransferFrom(msg.sender, address(this), listing.price);
        IERC20(listing.token).safeTransfer(listing.seller, sellerAmount);
        IERC20(listing.token).safeTransfer(feeCollector, fee);

        if (royalty > 0) {
            IERC20(listing.token).safeTransfer(collections[tokenToCollection[tokenId]].creator, royalty);
            emit RoyaltyPaid(tokenId, collections[tokenToCollection[tokenId]].creator, royalty);
        }

        _transfer(listing.seller, msg.sender, tokenId);
        listing.active = false;

        totalVolume = totalVolume.add(listing.price);
        totalFees = totalFees.add(fee);

        emit NFTSold(tokenId, listing.seller, msg.sender, listing.price);
    }

    /**
     * @dev Create an auction for an NFT
     */
    function createAuction(
        uint256 tokenId,
        address token,
        uint256 startingPrice,
        uint256 duration
    ) external nonReentrant validToken(tokenId) onlyAuthorizedToken(token) {
        require(ownerOf(tokenId) == msg.sender, "Not the owner");
        require(!listings[tokenId].active, "Currently listed");
        require(!auctions[tokenId].active, "Already in auction");
        require(startingPrice > 0, "Starting price must be positive");
        require(duration > 0, "Duration must be positive");

        auctions[tokenId] = Auction({
            seller: msg.sender,
            token: token,
            startingPrice: startingPrice,
            currentBid: 0,
            currentBidder: address(0),
            endTime: block.timestamp.add(duration),
            active: true,
            energyLevel: energyNFTs[tokenId].energyLevel,
            rarity: energyNFTs[tokenId].rarity
        });

        emit AuctionCreated(tokenId, msg.sender, startingPrice, block.timestamp.add(duration));
    }

    /**
     * @dev Place a bid on an auction
     */
    function placeBid(uint256 tokenId, uint256 bidAmount) external nonReentrant validToken(tokenId) {
        Auction storage auction = auctions[tokenId];
        require(auction.active, "Auction not active");
        require(block.timestamp < auction.endTime, "Auction ended");
        require(bidAmount > auction.currentBid, "Bid too low");
        require(msg.sender != auction.seller, "Cannot bid on own auction");

        if (auction.currentBidder != address(0)) {
            IERC20(auction.token).safeTransfer(auction.currentBidder, auction.currentBid);
        }

        IERC20(auction.token).safeTransferFrom(msg.sender, address(this), bidAmount);
        auction.currentBid = bidAmount;
        auction.currentBidder = msg.sender;

        emit BidPlaced(tokenId, msg.sender, bidAmount);
    }

    /**
     * @dev End an auction
     */
    function endAuction(uint256 tokenId) external nonReentrant validToken(tokenId) {
        Auction storage auction = auctions[tokenId];
        require(auction.active, "Auction not active");
        require(block.timestamp >= auction.endTime, "Auction not ended");

        if (auction.currentBidder != address(0)) {
            uint256 fee = auction.currentBid.mul(MARKETPLACE_FEE_RATE).div(10000);
            uint256 royalty = calculateRoyalty(tokenId, auction.currentBid);
            uint256 sellerAmount = auction.currentBid.sub(fee).sub(royalty);

            IERC20(auction.token).safeTransfer(auction.seller, sellerAmount);
            IERC20(auction.token).safeTransfer(feeCollector, fee);

            if (royalty > 0) {
                IERC20(auction.token).safeTransfer(collections[tokenToCollection[tokenId]].creator, royalty);
                emit RoyaltyPaid(tokenId, collections[tokenToCollection[tokenId]].creator, royalty);
            }

            _transfer(auction.seller, auction.currentBidder, tokenId);
            totalVolume = totalVolume.add(auction.currentBid);
            totalFees = totalFees.add(fee);

            emit AuctionEnded(tokenId, auction.currentBidder, auction.currentBid);
        }

        auction.active = false;
    }

    /**
     * @dev Recharge NFT energy
     */
    function rechargeEnergy(uint256 tokenId) external validToken(tokenId) {
        EnergyNFT storage nft = energyNFTs[tokenId];
        require(nft.isActive, "NFT not active");
        require(nft.energyLevel < nft.maxEnergy, "Energy already full");

        uint256 timeElapsed = block.timestamp.sub(nft.lastRecharge);
        uint256 energyGained = timeElapsed.div(3600).mul(nft.rechargeRate); // 1 hour = 3600 seconds
        
        if (energyGained > 0) {
            nft.energyLevel = min(nft.maxEnergy, nft.energyLevel.add(energyGained));
            nft.lastRecharge = block.timestamp;
            
            emit EnergyRecharged(tokenId, nft.energyLevel);
        }
    }

    /**
     * @dev Create a new collection
     */
    function createCollection(
        string memory name,
        string memory symbol,
        string memory baseURI,
        uint256 maxSupply,
        uint256 mintPrice,
        uint256 royaltyRate
    ) external returns (uint256) {
        require(royaltyRate <= MAX_ROYALTY_RATE, "Royalty rate too high");
        require(maxSupply > 0, "Max supply must be positive");

        uint256 collectionId = _collectionIdCounter.current();
        _collectionIdCounter.increment();

        collections[collectionId] = Collection({
            name: name,
            symbol: symbol,
            baseURI: baseURI,
            creator: msg.sender,
            maxSupply: maxSupply,
            currentSupply: 0,
            active: true,
            mintPrice: mintPrice,
            royaltyRate: royaltyRate
        });

        emit CollectionCreated(collectionId, name, msg.sender);
        return collectionId;
    }

    /**
     * @dev Calculate royalty for a token
     */
    function calculateRoyalty(uint256 tokenId, uint256 salePrice) public view returns (uint256) {
        uint256 collectionId = tokenToCollection[tokenId];
        return salePrice.mul(collections[collectionId].royaltyRate).div(10000);
    }

    /**
     * @dev Get current energy level of an NFT
     */
    function getCurrentEnergy(uint256 tokenId) external view validToken(tokenId) returns (uint256) {
        EnergyNFT memory nft = energyNFTs[tokenId];
        if (!nft.isActive) return 0;

        uint256 timeElapsed = block.timestamp.sub(nft.lastRecharge);
        uint256 energyGained = timeElapsed.div(3600).mul(nft.rechargeRate); // 1 hour = 3600 seconds
        
        return min(nft.maxEnergy, nft.energyLevel.add(energyGained));
    }

    /**
     * @dev Authorize a token for use in the marketplace
     */
    function authorizeToken(address token) external onlyOwner {
        authorizedTokens[token] = true;
    }

    /**
     * @dev Deauthorize a token
     */
    function deauthorizeToken(address token) external onlyOwner {
        authorizedTokens[token] = false;
    }

    /**
     * @dev Authorize a minter
     */
    function authorizeMinter(address minter) external onlyOwner {
        authorizedMinters[minter] = true;
    }

    /**
     * @dev Deauthorize a minter
     */
    function deauthorizeMinter(address minter) external onlyOwner {
        authorizedMinters[minter] = false;
    }

    /**
     * @dev Set fee collector address
     */
    function setFeeCollector(address _feeCollector) external onlyOwner {
        require(_feeCollector != address(0), "Invalid address");
        feeCollector = _feeCollector;
    }

    /**
     * @dev Set energy token address
     */
    function setEnergyToken(address _energyToken) external onlyOwner {
        require(_energyToken != address(0), "Invalid address");
        energyToken = _energyToken;
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

    // Override required functions
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721Enumerable) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    // Helper functions
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}