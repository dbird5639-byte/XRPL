// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title InheritanceEscrow
 * @dev Smart contract for managing digital asset inheritance and gifting
 */
contract InheritanceEscrow is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;
    using Counters for Counters.Counter;

    // Events
    event WillCreated(
        address indexed testator,
        bytes32 indexed willId,
        uint256 timestamp
    );
    
    event BeneficiaryAdded(
        bytes32 indexed willId,
        address indexed beneficiary,
        uint256 percentage,
        string relationship
    );
    
    event AssetDeposited(
        bytes32 indexed willId,
        address indexed asset,
        uint256 assetType, // 0: ERC20, 1: ERC721, 2: ERC1155, 3: Native
        uint256 tokenId,
        uint256 amount,
        uint256 timestamp
    );
    
    event WillActivated(
        bytes32 indexed willId,
        address indexed testator,
        uint256 timestamp
    );
    
    event AssetDistributed(
        bytes32 indexed willId,
        address indexed beneficiary,
        address indexed asset,
        uint256 amount,
        uint256 timestamp
    );
    
    event GiftCreated(
        address indexed giver,
        address indexed recipient,
        bytes32 indexed giftId,
        uint256 releaseTime,
        uint256 timestamp
    );
    
    event GiftReleased(
        bytes32 indexed giftId,
        address indexed recipient,
        uint256 timestamp
    );
    
    event ExecutorAdded(
        bytes32 indexed willId,
        address indexed executor,
        uint256 timestamp
    );
    
    event ExecutorRemoved(
        bytes32 indexed willId,
        address indexed executor,
        uint256 timestamp
    );

    // Structs
    struct Will {
        bytes32 willId;
        address testator;
        address[] beneficiaries;
        mapping(address => uint256) beneficiaryPercentages;
        mapping(address => string) beneficiaryRelationships;
        address[] executors;
        mapping(address => bool) executorApprovals;
        address[] assets;
        mapping(address => uint256) assetTypes; // 0: ERC20, 1: ERC721, 2: ERC1155, 3: Native
        mapping(address => uint256) assetAmounts;
        mapping(address => uint256) assetTokenIds; // For ERC721/ERC1155
        bool active;
        bool executed;
        uint256 creationTime;
        uint256 activationTime;
        uint256 totalAssets;
    }
    
    struct Gift {
        bytes32 giftId;
        address giver;
        address recipient;
        address asset;
        uint256 assetType;
        uint256 tokenId;
        uint256 amount;
        uint256 releaseTime;
        bool released;
        string message;
        uint256 creationTime;
    }
    
    struct HealthCheck {
        address testator;
        uint256 lastCheckTime;
        uint256 checkInterval;
        bool active;
        address[] guardians;
        mapping(address => bool) guardianApprovals;
    }

    // State variables
    mapping(bytes32 => Will) public wills;
    mapping(bytes32 => Gift) public gifts;
    mapping(address => HealthCheck) public healthChecks;
    mapping(address => bytes32[]) public userWills;
    mapping(address => bytes32[]) public userGifts;
    mapping(address => bool) public authorizedExecutors;
    
    Counters.Counter private _willIdCounter;
    Counters.Counter private _giftIdCounter;
    
    uint256 public executorFee = 1000; // 10 XRP in drops
    uint256 public willCreationFee = 500; // 5 XRP in drops
    uint256 public giftCreationFee = 200; // 2 XRP in drops
    uint256 public platformFee = 50; // 0.5% in basis points
    
    address public feeRecipient;
    uint256 public minWillDuration = 30 days; // Minimum time before will can be activated
    uint256 public maxBeneficiaries = 20;
    uint256 public maxExecutors = 5;

    // Modifiers
    modifier onlyTestator(bytes32 willId) {
        require(wills[willId].testator == msg.sender, "Not the testator");
        _;
    }
    
    modifier onlyExecutor(bytes32 willId) {
        require(
            wills[willId].executorApprovals[msg.sender] || 
            authorizedExecutors[msg.sender],
            "Not an executor"
        );
        _;
    }
    
    modifier willExists(bytes32 willId) {
        require(wills[willId].willId != bytes32(0), "Will does not exist");
        _;
    }
    
    modifier willActive(bytes32 willId) {
        require(wills[willId].active, "Will not active");
        _;
    }
    
    modifier willNotExecuted(bytes32 willId) {
        require(!wills[willId].executed, "Will already executed");
        _;
    }

    constructor(address _feeRecipient) {
        feeRecipient = _feeRecipient;
    }

    /**
     * @dev Create a new will
     * @param beneficiaries Array of beneficiary addresses
     * @param percentages Array of percentage allocations (must sum to 10000 = 100%)
     * @param relationships Array of relationships to beneficiaries
     * @param executors Array of executor addresses
     */
    function createWill(
        address[] calldata beneficiaries,
        uint256[] calldata percentages,
        string[] calldata relationships,
        address[] calldata executors
    ) external payable {
        require(beneficiaries.length > 0, "No beneficiaries");
        require(beneficiaries.length == percentages.length, "Mismatched arrays");
        require(beneficiaries.length == relationships.length, "Mismatched arrays");
        require(executors.length <= maxExecutors, "Too many executors");
        require(msg.value >= willCreationFee, "Insufficient creation fee");
        
        // Verify percentages sum to 100%
        uint256 totalPercentage = 0;
        for (uint256 i = 0; i < percentages.length; i++) {
            totalPercentage += percentages[i];
        }
        require(totalPercentage == 10000, "Percentages must sum to 100%");
        
        bytes32 willId = keccak256(abi.encodePacked(
            msg.sender,
            block.timestamp,
            _willIdCounter.current()
        ));
        _willIdCounter.increment();
        
        Will storage will = wills[willId];
        will.willId = willId;
        will.testator = msg.sender;
        will.active = false;
        will.executed = false;
        will.creationTime = block.timestamp;
        will.activationTime = 0;
        will.totalAssets = 0;
        
        // Add beneficiaries
        for (uint256 i = 0; i < beneficiaries.length; i++) {
            will.beneficiaries.push(beneficiaries[i]);
            will.beneficiaryPercentages[beneficiaries[i]] = percentages[i];
            will.beneficiaryRelationships[beneficiaries[i]] = relationships[i];
        }
        
        // Add executors
        for (uint256 i = 0; i < executors.length; i++) {
            will.executors.push(executors[i]);
            will.executorApprovals[executors[i]] = true;
        }
        
        userWills[msg.sender].push(willId);
        
        // Transfer creation fee
        if (msg.value > 0) {
            payable(feeRecipient).transfer(msg.value);
        }
        
        emit WillCreated(msg.sender, willId, block.timestamp);
        
        for (uint256 i = 0; i < beneficiaries.length; i++) {
            emit BeneficiaryAdded(willId, beneficiaries[i], percentages[i], relationships[i]);
        }
        
        for (uint256 i = 0; i < executors.length; i++) {
            emit ExecutorAdded(willId, executors[i], block.timestamp);
        }
    }

    /**
     * @dev Deposit assets into a will
     * @param willId Will ID
     * @param asset Asset contract address (address(0) for native ETH)
     * @param assetType Asset type (0: ERC20, 1: ERC721, 2: ERC1155, 3: Native)
     * @param tokenId Token ID (0 for ERC20/Native)
     * @param amount Amount to deposit
     */
    function depositAsset(
        bytes32 willId,
        address asset,
        uint256 assetType,
        uint256 tokenId,
        uint256 amount
    ) external payable onlyTestator(willId) willExists(willId) willNotExecuted(willId) {
        require(amount > 0, "Invalid amount");
        require(assetType <= 3, "Invalid asset type");
        
        Will storage will = wills[willId];
        
        if (assetType == 0) { // ERC20
            IERC20(asset).safeTransferFrom(msg.sender, address(this), amount);
        } else if (assetType == 1) { // ERC721
            IERC721(asset).transferFrom(msg.sender, address(this), tokenId);
            amount = 1; // NFTs are always quantity 1
        } else if (assetType == 2) { // ERC1155
            IERC1155(asset).safeTransferFrom(msg.sender, address(this), tokenId, amount, "");
        } else if (assetType == 3) { // Native ETH
            require(msg.value >= amount, "Insufficient ETH");
        }
        
        // Check if asset already exists in will
        bool assetExists = false;
        for (uint256 i = 0; i < will.assets.length; i++) {
            if (will.assets[i] == asset && will.assetTokenIds[asset] == tokenId) {
                will.assetAmounts[asset] += amount;
                assetExists = true;
                break;
            }
        }
        
        if (!assetExists) {
            will.assets.push(asset);
            will.assetTypes[asset] = assetType;
            will.assetAmounts[asset] = amount;
            will.assetTokenIds[asset] = tokenId;
        }
        
        will.totalAssets += amount;
        
        emit AssetDeposited(willId, asset, assetType, tokenId, amount, block.timestamp);
    }

    /**
     * @dev Activate a will (testator must be alive and confirm)
     * @param willId Will ID
     */
    function activateWill(bytes32 willId) external onlyTestator(willId) willExists(willId) {
        Will storage will = wills[willId];
        require(!will.active, "Will already active");
        require(
            block.timestamp >= will.creationTime + minWillDuration,
            "Minimum duration not met"
        );
        
        will.active = true;
        will.activationTime = block.timestamp;
        
        emit WillActivated(willId, msg.sender, block.timestamp);
    }

    /**
     * @dev Execute a will (only executors after testator's death)
     * @param willId Will ID
     * @param deathCertificateHash Hash of death certificate
     */
    function executeWill(
        bytes32 willId,
        bytes32 deathCertificateHash
    ) external onlyExecutor(willId) willExists(willId) willActive(willId) willNotExecuted(willId) {
        Will storage will = wills[willId];
        require(!will.executed, "Will already executed");
        
        // In production, this would require multiple executor confirmations
        // and verification of death certificate
        
        will.executed = true;
        
        // Distribute assets to beneficiaries
        for (uint256 i = 0; i < will.assets.length; i++) {
            address asset = will.assets[i];
            uint256 assetType = will.assetTypes[asset];
            uint256 totalAmount = will.assetAmounts[asset];
            uint256 tokenId = will.assetTokenIds[asset];
            
            for (uint256 j = 0; j < will.beneficiaries.length; j++) {
                address beneficiary = will.beneficiaries[j];
                uint256 percentage = will.beneficiaryPercentages[beneficiary];
                uint256 amount = (totalAmount * percentage) / 10000;
                
                if (amount > 0) {
                    _transferAsset(asset, assetType, tokenId, amount, beneficiary);
                    emit AssetDistributed(willId, beneficiary, asset, amount, block.timestamp);
                }
            }
        }
    }

    /**
     * @dev Create a time-locked gift
     * @param recipient Gift recipient
     * @param asset Asset contract address
     * @param assetType Asset type
     * @param tokenId Token ID
     * @param amount Amount to gift
     * @param releaseTime When the gift can be claimed
     * @param message Personal message
     */
    function createGift(
        address recipient,
        address asset,
        uint256 assetType,
        uint256 tokenId,
        uint256 amount,
        uint256 releaseTime,
        string calldata message
    ) external payable {
        require(recipient != address(0), "Invalid recipient");
        require(amount > 0, "Invalid amount");
        require(releaseTime > block.timestamp, "Invalid release time");
        require(msg.value >= giftCreationFee, "Insufficient creation fee");
        
        bytes32 giftId = keccak256(abi.encodePacked(
            msg.sender,
            recipient,
            asset,
            block.timestamp,
            _giftIdCounter.current()
        ));
        _giftIdCounter.increment();
        
        // Transfer asset to contract
        if (assetType == 0) { // ERC20
            IERC20(asset).safeTransferFrom(msg.sender, address(this), amount);
        } else if (assetType == 1) { // ERC721
            IERC721(asset).transferFrom(msg.sender, address(this), tokenId);
            amount = 1;
        } else if (assetType == 2) { // ERC1155
            IERC1155(asset).safeTransferFrom(msg.sender, address(this), tokenId, amount, "");
        } else if (assetType == 3) { // Native ETH
            require(msg.value >= amount + giftCreationFee, "Insufficient ETH");
        }
        
        gifts[giftId] = Gift({
            giftId: giftId,
            giver: msg.sender,
            recipient: recipient,
            asset: asset,
            assetType: assetType,
            tokenId: tokenId,
            amount: amount,
            releaseTime: releaseTime,
            released: false,
            message: message,
            creationTime: block.timestamp
        });
        
        userGifts[msg.sender].push(giftId);
        userGifts[recipient].push(giftId);
        
        // Transfer creation fee
        if (msg.value > giftCreationFee) {
            payable(feeRecipient).transfer(giftCreationFee);
        }
        
        emit GiftCreated(msg.sender, recipient, giftId, releaseTime, block.timestamp);
    }

    /**
     * @dev Claim a time-locked gift
     * @param giftId Gift ID
     */
    function claimGift(bytes32 giftId) external nonReentrant {
        Gift storage gift = gifts[giftId];
        require(gift.recipient == msg.sender, "Not the recipient");
        require(!gift.released, "Gift already released");
        require(block.timestamp >= gift.releaseTime, "Gift not yet available");
        
        gift.released = true;
        
        _transferAsset(gift.asset, gift.assetType, gift.tokenId, gift.amount, msg.sender);
        
        emit GiftReleased(giftId, msg.sender, block.timestamp);
    }

    /**
     * @dev Set up health check monitoring
     * @param checkInterval Interval between health checks
     * @param guardians Array of guardian addresses
     */
    function setupHealthCheck(
        uint256 checkInterval,
        address[] calldata guardians
    ) external {
        require(checkInterval > 0, "Invalid interval");
        require(guardians.length > 0, "No guardians");
        
        healthChecks[msg.sender] = HealthCheck({
            testator: msg.sender,
            lastCheckTime: block.timestamp,
            checkInterval: checkInterval,
            active: true,
            guardians: guardians
        });
        
        for (uint256 i = 0; i < guardians.length; i++) {
            healthChecks[msg.sender].guardianApprovals[guardians[i]] = true;
        }
    }

    /**
     * @dev Confirm testator is alive (guardian function)
     * @param testator Testator address
     */
    function confirmAlive(address testator) external {
        HealthCheck storage healthCheck = healthChecks[testator];
        require(healthCheck.active, "Health check not active");
        require(healthCheck.guardianApprovals[msg.sender], "Not a guardian");
        
        healthCheck.lastCheckTime = block.timestamp;
    }

    // View functions
    function getWill(bytes32 willId) external view returns (
        address testator,
        address[] memory beneficiaries,
        address[] memory executors,
        address[] memory assets,
        bool active,
        bool executed,
        uint256 creationTime,
        uint256 totalAssets
    ) {
        Will storage will = wills[willId];
        return (
            will.testator,
            will.beneficiaries,
            will.executors,
            will.assets,
            will.active,
            will.executed,
            will.creationTime,
            will.totalAssets
        );
    }
    
    function getBeneficiaryPercentage(bytes32 willId, address beneficiary) external view returns (uint256) {
        return wills[willId].beneficiaryPercentages[beneficiary];
    }
    
    function getAssetDetails(bytes32 willId, address asset) external view returns (
        uint256 assetType,
        uint256 amount,
        uint256 tokenId
    ) {
        Will storage will = wills[willId];
        return (
            will.assetTypes[asset],
            will.assetAmounts[asset],
            will.assetTokenIds[asset]
        );
    }
    
    function getGift(bytes32 giftId) external view returns (Gift memory) {
        return gifts[giftId];
    }
    
    function getUserWills(address user) external view returns (bytes32[] memory) {
        return userWills[user];
    }
    
    function getUserGifts(address user) external view returns (bytes32[] memory) {
        return userGifts[user];
    }

    // Internal functions
    function _transferAsset(
        address asset,
        uint256 assetType,
        uint256 tokenId,
        uint256 amount,
        address to
    ) internal {
        if (assetType == 0) { // ERC20
            IERC20(asset).safeTransfer(to, amount);
        } else if (assetType == 1) { // ERC721
            IERC721(asset).transferFrom(address(this), to, tokenId);
        } else if (assetType == 2) { // ERC1155
            IERC1155(asset).safeTransferFrom(address(this), to, tokenId, amount, "");
        } else if (assetType == 3) { // Native ETH
            payable(to).transfer(amount);
        }
    }

    // Admin functions
    function addAuthorizedExecutor(address executor) external onlyOwner {
        authorizedExecutors[executor] = true;
    }
    
    function removeAuthorizedExecutor(address executor) external onlyOwner {
        authorizedExecutors[executor] = false;
    }
    
    function updateFees(
        uint256 newWillCreationFee,
        uint256 newGiftCreationFee,
        uint256 newExecutorFee,
        uint256 newPlatformFee
    ) external onlyOwner {
        willCreationFee = newWillCreationFee;
        giftCreationFee = newGiftCreationFee;
        executorFee = newExecutorFee;
        platformFee = newPlatformFee;
    }
    
    function updateLimits(
        uint256 newMinWillDuration,
        uint256 newMaxBeneficiaries,
        uint256 newMaxExecutors
    ) external onlyOwner {
        minWillDuration = newMinWillDuration;
        maxBeneficiaries = newMaxBeneficiaries;
        maxExecutors = newMaxExecutors;
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        if (token == address(0)) {
            payable(owner()).transfer(amount);
        } else {
            IERC20(token).safeTransfer(owner(), amount);
        }
    }
}
