// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title FengShuiNFT
 * @dev NFT contract for Feng Shui digital assets and spiritual items
 */
contract FengShuiNFT is ERC721, ERC721Enumerable, ERC721URIStorage, ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using Counters for Counters.Counter;

    // Events
    event NFTMinted(
        uint256 indexed tokenId,
        address indexed owner,
        string category,
        string element,
        uint256 energyLevel,
        uint256 timestamp
    );
    
    event NFTListed(
        uint256 indexed tokenId,
        address indexed seller,
        uint256 price,
        uint256 timestamp
    );
    
    event NFTSold(
        uint256 indexed tokenId,
        address indexed seller,
        address indexed buyer,
        uint256 price,
        uint256 timestamp
    );
    
    event EnergyTransferred(
        uint256 indexed fromTokenId,
        uint256 indexed toTokenId,
        uint256 energyAmount,
        address indexed owner
    );
    
    event ConsultationBooked(
        address indexed client,
        address indexed consultant,
        uint256 consultationId,
        uint256 fee,
        uint256 timestamp
    );
    
    event BlessingPerformed(
        uint256 indexed tokenId,
        address indexed owner,
        string blessingType,
        uint256 energyIncrease,
        uint256 timestamp
    );

    // Structs
    struct FengShuiAsset {
        uint256 tokenId;
        string category; // "crystal", "statue", "painting", "furniture", "plant", "water_feature"
        string element; // "wood", "fire", "earth", "metal", "water"
        uint256 energyLevel; // 1-100
        uint256 rarity; // 1-5 (common, uncommon, rare, epic, legendary)
        string description;
        string[] properties; // ["wealth", "health", "love", "career", "wisdom"]
        uint256 creationTime;
        bool blessed;
        uint256 blessingCount;
    }
    
    struct Listing {
        uint256 tokenId;
        address seller;
        uint256 price;
        bool active;
        uint256 timestamp;
    }
    
    struct Consultation {
        uint256 consultationId;
        address client;
        address consultant;
        uint256 fee;
        string consultationType; // "home_analysis", "business_consultation", "personal_reading"
        bool completed;
        uint256 timestamp;
    }
    
    struct Blessing {
        string blessingType; // "wealth", "health", "love", "protection", "wisdom"
        uint256 energyIncrease;
        uint256 cost;
        bool available;
    }

    // State variables
    mapping(uint256 => FengShuiAsset) public fengShuiAssets;
    mapping(uint256 => Listing) public listings;
    mapping(uint256 => Consultation) public consultations;
    mapping(string => Blessing) public blessings;
    mapping(address => bool) public authorizedConsultants;
    mapping(address => uint256[]) public userAssets;
    mapping(address => uint256[]) public userConsultations;
    
    Counters.Counter private _tokenIdCounter;
    Counters.Counter private _consultationIdCounter;
    
    IERC20 public paymentToken;
    address public feeRecipient;
    
    uint256 public mintingFee = 1000; // 10 XRP in drops
    uint256 public listingFee = 100; // 1 XRP in drops
    uint256 public platformFee = 250; // 2.5% in basis points
    uint256 public blessingFee = 500; // 5 XRP in drops
    
    string[] public categories = [
        "crystal", "statue", "painting", "furniture", 
        "plant", "water_feature", "wind_chime", "mirror"
    ];
    
    string[] public elements = ["wood", "fire", "earth", "metal", "water"];
    string[] public properties = ["wealth", "health", "love", "career", "wisdom", "protection", "harmony"];

    // Modifiers
    modifier onlyConsultant() {
        require(authorizedConsultants[msg.sender], "Not an authorized consultant");
        _;
    }
    
    modifier validEnergyLevel(uint256 energyLevel) {
        require(energyLevel >= 1 && energyLevel <= 100, "Invalid energy level");
        _;
    }
    
    modifier validRarity(uint256 rarity) {
        require(rarity >= 1 && rarity <= 5, "Invalid rarity");
        _;
    }

    constructor(
        string memory name,
        string memory symbol,
        address _paymentToken,
        address _feeRecipient
    ) ERC721(name, symbol) {
        paymentToken = IERC20(_paymentToken);
        feeRecipient = _feeRecipient;
        
        // Initialize blessings
        _initializeBlessings();
    }

    /**
     * @dev Mint a new Feng Shui NFT
     * @param category Category of the asset
     * @param element Element type
     * @param energyLevel Energy level (1-100)
     * @param rarity Rarity level (1-5)
     * @param description Description of the asset
     * @param properties Array of properties
     * @param tokenURI Metadata URI
     */
    function mintFengShuiNFT(
        string calldata category,
        string calldata element,
        uint256 energyLevel,
        uint256 rarity,
        string calldata description,
        string[] calldata properties,
        string calldata tokenURI
    ) external payable validEnergyLevel(energyLevel) validRarity(rarity) {
        require(msg.value >= mintingFee, "Insufficient minting fee");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, tokenURI);
        
        fengShuiAssets[tokenId] = FengShuiAsset({
            tokenId: tokenId,
            category: category,
            element: element,
            energyLevel: energyLevel,
            rarity: rarity,
            description: description,
            properties: properties,
            creationTime: block.timestamp,
            blessed: false,
            blessingCount: 0
        });
        
        userAssets[msg.sender].push(tokenId);
        
        // Transfer minting fee to fee recipient
        if (msg.value > 0) {
            payable(feeRecipient).transfer(msg.value);
        }
        
        emit NFTMinted(tokenId, msg.sender, category, element, energyLevel, block.timestamp);
    }

    /**
     * @dev List an NFT for sale
     * @param tokenId Token ID to list
     * @param price Sale price
     */
    function listNFT(uint256 tokenId, uint256 price) external payable {
        require(ownerOf(tokenId) == msg.sender, "Not the owner");
        require(price > 0, "Invalid price");
        require(!listings[tokenId].active, "Already listed");
        require(msg.value >= listingFee, "Insufficient listing fee");
        
        listings[tokenId] = Listing({
            tokenId: tokenId,
            seller: msg.sender,
            price: price,
            active: true,
            timestamp: block.timestamp
        });
        
        // Transfer listing fee
        if (msg.value > 0) {
            payable(feeRecipient).transfer(msg.value);
        }
        
        emit NFTListed(tokenId, msg.sender, price, block.timestamp);
    }

    /**
     * @dev Buy a listed NFT
     * @param tokenId Token ID to buy
     */
    function buyNFT(uint256 tokenId) external nonReentrant {
        Listing storage listing = listings[tokenId];
        require(listing.active, "Not for sale");
        require(listing.seller != msg.sender, "Cannot buy own NFT");
        
        uint256 price = listing.price;
        uint256 fee = (price * platformFee) / 10000;
        uint256 netAmount = price - fee;
        
        // Transfer payment
        paymentToken.safeTransferFrom(msg.sender, address(this), price);
        
        // Transfer fee to platform
        if (fee > 0) {
            paymentToken.safeTransfer(feeRecipient, fee);
        }
        
        // Transfer net amount to seller
        paymentToken.safeTransfer(listing.seller, netAmount);
        
        // Transfer NFT
        _transfer(listing.seller, msg.sender, tokenId);
        
        // Update listings
        listing.active = false;
        
        // Update user assets
        _removeFromUserAssets(listing.seller, tokenId);
        userAssets[msg.sender].push(tokenId);
        
        emit NFTSold(tokenId, listing.seller, msg.sender, price, block.timestamp);
    }

    /**
     * @dev Cancel a listing
     * @param tokenId Token ID to delist
     */
    function cancelListing(uint256 tokenId) external {
        require(listings[tokenId].seller == msg.sender, "Not the seller");
        require(listings[tokenId].active, "Not listed");
        
        listings[tokenId].active = false;
    }

    /**
     * @dev Transfer energy between NFTs
     * @param fromTokenId Source token ID
     * @param toTokenId Destination token ID
     * @param energyAmount Amount of energy to transfer
     */
    function transferEnergy(
        uint256 fromTokenId,
        uint256 toTokenId,
        uint256 energyAmount
    ) external {
        require(ownerOf(fromTokenId) == msg.sender, "Not owner of source NFT");
        require(ownerOf(toTokenId) == msg.sender, "Not owner of destination NFT");
        require(energyAmount > 0, "Invalid energy amount");
        require(
            fengShuiAssets[fromTokenId].energyLevel >= energyAmount,
            "Insufficient energy"
        );
        
        fengShuiAssets[fromTokenId].energyLevel -= energyAmount;
        fengShuiAssets[toTokenId].energyLevel += energyAmount;
        
        emit EnergyTransferred(fromTokenId, toTokenId, energyAmount, msg.sender);
    }

    /**
     * @dev Book a Feng Shui consultation
     * @param consultant Consultant's address
     * @param consultationType Type of consultation
     * @param fee Consultation fee
     */
    function bookConsultation(
        address consultant,
        string calldata consultationType,
        uint256 fee
    ) external nonReentrant {
        require(authorizedConsultants[consultant], "Not an authorized consultant");
        require(fee > 0, "Invalid fee");
        
        uint256 consultationId = _consultationIdCounter.current();
        _consultationIdCounter.increment();
        
        // Transfer consultation fee
        paymentToken.safeTransferFrom(msg.sender, address(this), fee);
        
        consultations[consultationId] = Consultation({
            consultationId: consultationId,
            client: msg.sender,
            consultant: consultant,
            fee: fee,
            consultationType: consultationType,
            completed: false,
            timestamp: block.timestamp
        });
        
        userConsultations[msg.sender].push(consultationId);
        
        emit ConsultationBooked(msg.sender, consultant, consultationId, fee, block.timestamp);
    }

    /**
     * @dev Complete a consultation (only consultant)
     * @param consultationId Consultation ID
     */
    function completeConsultation(uint256 consultationId) external onlyConsultant {
        require(consultations[consultationId].consultant == msg.sender, "Not your consultation");
        require(!consultations[consultationId].completed, "Already completed");
        
        consultations[consultationId].completed = true;
        
        // Transfer fee to consultant
        paymentToken.safeTransfer(msg.sender, consultations[consultationId].fee);
    }

    /**
     * @dev Perform a blessing on an NFT
     * @param tokenId Token ID to bless
     * @param blessingType Type of blessing
     */
    function performBlessing(
        uint256 tokenId,
        string calldata blessingType
    ) external payable {
        require(ownerOf(tokenId) == msg.sender, "Not the owner");
        require(blessings[blessingType].available, "Blessing not available");
        require(msg.value >= blessingFee, "Insufficient blessing fee");
        
        Blessing storage blessing = blessings[blessingType];
        
        fengShuiAssets[tokenId].energyLevel += blessing.energyIncrease;
        fengShuiAssets[tokenId].blessed = true;
        fengShuiAssets[tokenId].blessingCount++;
        
        // Transfer blessing fee
        if (msg.value > 0) {
            payable(feeRecipient).transfer(msg.value);
        }
        
        emit BlessingPerformed(tokenId, msg.sender, blessingType, blessing.energyIncrease, block.timestamp);
    }

    /**
     * @dev Get user's assets
     * @param user User address
     * @return Array of token IDs
     */
    function getUserAssets(address user) external view returns (uint256[] memory) {
        return userAssets[user];
    }

    /**
     * @dev Get user's consultations
     * @param user User address
     * @return Array of consultation IDs
     */
    function getUserConsultations(address user) external view returns (uint256[] memory) {
        return userConsultations[user];
    }

    /**
     * @dev Get Feng Shui asset details
     * @param tokenId Token ID
     * @return Asset details
     */
    function getFengShuiAsset(uint256 tokenId) external view returns (FengShuiAsset memory) {
        return fengShuiAssets[tokenId];
    }

    /**
     * @dev Get listing details
     * @param tokenId Token ID
     * @return Listing details
     */
    function getListing(uint256 tokenId) external view returns (Listing memory) {
        return listings[tokenId];
    }

    /**
     * @dev Get consultation details
     * @param consultationId Consultation ID
     * @return Consultation details
     */
    function getConsultation(uint256 consultationId) external view returns (Consultation memory) {
        return consultations[consultationId];
    }

    // Admin functions
    function addConsultant(address consultant) external onlyOwner {
        authorizedConsultants[consultant] = true;
    }
    
    function removeConsultant(address consultant) external onlyOwner {
        authorizedConsultants[consultant] = false;
    }
    
    function updateBlessing(
        string calldata blessingType,
        uint256 energyIncrease,
        uint256 cost,
        bool available
    ) external onlyOwner {
        blessings[blessingType] = Blessing({
            blessingType: blessingType,
            energyIncrease: energyIncrease,
            cost: cost,
            available: available
        });
    }
    
    function updateFees(
        uint256 newMintingFee,
        uint256 newListingFee,
        uint256 newPlatformFee,
        uint256 newBlessingFee
    ) external onlyOwner {
        mintingFee = newMintingFee;
        listingFee = newListingFee;
        platformFee = newPlatformFee;
        blessingFee = newBlessingFee;
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }

    // Internal functions
    function _initializeBlessings() internal {
        blessings["wealth"] = Blessing({
            blessingType: "wealth",
            energyIncrease: 10,
            cost: 500,
            available: true
        });
        
        blessings["health"] = Blessing({
            blessingType: "health",
            energyIncrease: 15,
            cost: 500,
            available: true
        });
        
        blessings["love"] = Blessing({
            blessingType: "love",
            energyIncrease: 12,
            cost: 500,
            available: true
        });
        
        blessings["protection"] = Blessing({
            blessingType: "protection",
            energyIncrease: 20,
            cost: 500,
            available: true
        });
        
        blessings["wisdom"] = Blessing({
            blessingType: "wisdom",
            energyIncrease: 8,
            cost: 500,
            available: true
        });
    }
    
    function _removeFromUserAssets(address user, uint256 tokenId) internal {
        uint256[] storage assets = userAssets[user];
        for (uint256 i = 0; i < assets.length; i++) {
            if (assets[i] == tokenId) {
                assets[i] = assets[assets.length - 1];
                assets.pop();
                break;
            }
        }
    }

    // Required overrides
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

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
