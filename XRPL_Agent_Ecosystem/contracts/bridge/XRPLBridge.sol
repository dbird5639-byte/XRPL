// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title XRPLBridge
 * @dev Advanced bridge contract for seamless asset and data transfer between XRPL and EVM sidechain
 * @author XRPL Agent Ecosystem
 */
contract XRPLBridge is ReentrancyGuard, Pausable, Ownable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Bridge operation types
    enum BridgeOperation {
        Lock,
        Unlock,
        Mint,
        Burn,
        DataTransfer,
        AgentMigration
    }

    // Bridge transaction structure
    struct BridgeTransaction {
        bytes32 xrplTxHash;
        address evmAddress;
        address token;
        uint256 amount;
        BridgeOperation operation;
        uint256 timestamp;
        bool processed;
        bool verified;
        string metadata;
    }

    // XRPL account structure
    struct XRPLAccount {
        string address;
        uint256 balance;
        bool isActive;
        uint256 lastUpdate;
        mapping(string => uint256) tokenBalances;
    }

    // Agent migration structure
    struct AgentMigration {
        uint256 agentId;
        string xrplAgentId;
        address evmOwner;
        string xrplOwner;
        uint256 migrationTime;
        bool completed;
        string migrationData;
    }

    // Events
    event AssetLocked(
        bytes32 indexed xrplTxHash,
        address indexed evmAddress,
        address indexed token,
        uint256 amount,
        string xrplAddress
    );
    event AssetUnlocked(
        bytes32 indexed evmTxHash,
        string indexed xrplAddress,
        address indexed token,
        uint256 amount
    );
    event AssetMinted(
        bytes32 indexed xrplTxHash,
        address indexed evmAddress,
        address indexed token,
        uint256 amount
    );
    event AssetBurned(
        address indexed evmAddress,
        string indexed xrplAddress,
        address indexed token,
        uint256 amount
    );
    event DataTransferred(
        bytes32 indexed transferId,
        string indexed xrplAddress,
        address indexed evmAddress,
        bytes data
    );
    event AgentMigrated(
        uint256 indexed agentId,
        string indexed xrplAgentId,
        address indexed evmOwner,
        bool success
    );
    event BridgeTransactionProcessed(
        bytes32 indexed xrplTxHash,
        bool success,
        string errorMessage
    );

    // State variables
    mapping(bytes32 => BridgeTransaction) public bridgeTransactions;
    mapping(string => XRPLAccount) public xrplAccounts;
    mapping(address => string) public evmToXrplAddress;
    mapping(string => address) public xrplToEvmAddress;
    mapping(uint256 => AgentMigration) public agentMigrations;
    mapping(address => bool) public authorizedValidators;
    mapping(address => bool) public supportedTokens;
    
    uint256 public nextMigrationId = 1;
    uint256 public totalTransactions = 0;
    uint256 public totalVolume = 0;
    
    // Configuration
    uint256 public bridgeFeeRate = 10; // 0.1%
    uint256 public minBridgeAmount = 1000; // Minimum amount for bridging
    uint256 public maxBridgeAmount = 1000000 * 1e18; // Maximum amount for bridging
    uint256 public confirmationBlocks = 12; // Blocks to wait for confirmation
    uint256 public validatorThreshold = 3; // Minimum validators required
    
    address public feeCollector;
    address public xrplValidator;
    IERC20 public nativeToken;

    // Modifiers
    modifier onlyAuthorizedValidator() {
        require(authorizedValidators[msg.sender] || msg.sender == owner(), "Not authorized validator");
        _;
    }

    modifier validToken(address token) {
        require(supportedTokens[token] || token == address(0), "Token not supported");
        _;
    }

    modifier validAmount(uint256 amount) {
        require(amount >= minBridgeAmount, "Amount too small");
        require(amount <= maxBridgeAmount, "Amount too large");
        _;
    }

    constructor(
        address _feeCollector,
        address _xrplValidator,
        address _nativeToken
    ) {
        feeCollector = _feeCollector;
        xrplValidator = _xrplValidator;
        nativeToken = IERC20(_nativeToken);
    }

    /**
     * @dev Lock assets on EVM sidechain to bridge to XRPL
     */
    function lockAssets(
        address token,
        uint256 amount,
        string memory xrplAddress
    ) external payable nonReentrant whenNotPaused validToken(token) validAmount(amount) {
        require(bytes(xrplAddress).length > 0, "XRPL address required");
        require(evmToXrplAddress[msg.sender] == "" || evmToXrplAddress[msg.sender] == xrplAddress, "Address mismatch");
        
        // Calculate bridge fee
        uint256 bridgeFee = amount.mul(bridgeFeeRate).div(10000);
        uint256 netAmount = amount.sub(bridgeFee);
        
        // Transfer tokens to bridge contract
        if (token == address(0)) {
            require(msg.value >= amount, "Insufficient ETH");
            // ETH is already in contract
        } else {
            IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        }
        
        // Transfer bridge fee
        if (bridgeFee > 0) {
            if (token == address(0)) {
                payable(feeCollector).transfer(bridgeFee);
            } else {
                IERC20(token).safeTransfer(feeCollector, bridgeFee);
            }
        }
        
        // Record bridge transaction
        bytes32 txHash = keccak256(abi.encodePacked(
            block.timestamp,
            msg.sender,
            token,
            amount,
            xrplAddress
        ));
        
        bridgeTransactions[txHash] = BridgeTransaction({
            xrplTxHash: bytes32(0),
            evmAddress: msg.sender,
            token: token,
            amount: netAmount,
            operation: BridgeOperation.Lock,
            timestamp: block.timestamp,
            processed: false,
            verified: false,
            metadata: xrplAddress
        });
        
        // Update mappings
        evmToXrplAddress[msg.sender] = xrplAddress;
        xrplToEvmAddress[xrplAddress] = msg.sender;
        
        totalTransactions++;
        totalVolume = totalVolume.add(amount);
        
        emit AssetLocked(txHash, msg.sender, token, netAmount, xrplAddress);
    }

    /**
     * @dev Unlock assets on EVM sidechain after XRPL burn
     */
    function unlockAssets(
        bytes32 xrplTxHash,
        address token,
        uint256 amount,
        address evmAddress
    ) external onlyAuthorizedValidator nonReentrant whenNotPaused {
        require(evmAddress != address(0), "Invalid EVM address");
        require(amount > 0, "Invalid amount");
        
        // Verify XRPL transaction (simplified - real implementation would verify with XRPL)
        require(_verifyXRPLTransaction(xrplTxHash), "XRPL transaction not verified");
        
        // Record bridge transaction
        bridgeTransactions[xrplTxHash] = BridgeTransaction({
            xrplTxHash: xrplTxHash,
            evmAddress: evmAddress,
            token: token,
            amount: amount,
            operation: BridgeOperation.Unlock,
            timestamp: block.timestamp,
            processed: true,
            verified: true,
            metadata: ""
        });
        
        // Transfer tokens to EVM address
        if (token == address(0)) {
            payable(evmAddress).transfer(amount);
        } else {
            IERC20(token).safeTransfer(evmAddress, amount);
        }
        
        emit AssetUnlocked(xrplTxHash, evmToXrplAddress[evmAddress], token, amount);
    }

    /**
     * @dev Mint tokens on EVM sidechain after XRPL lock
     */
    function mintTokens(
        bytes32 xrplTxHash,
        address token,
        uint256 amount,
        address evmAddress
    ) external onlyAuthorizedValidator nonReentrant whenNotPaused {
        require(evmAddress != address(0), "Invalid EVM address");
        require(amount > 0, "Invalid amount");
        
        // Verify XRPL transaction
        require(_verifyXRPLTransaction(xrplTxHash), "XRPL transaction not verified");
        
        // Record bridge transaction
        bridgeTransactions[xrplTxHash] = BridgeTransaction({
            xrplTxHash: xrplTxHash,
            evmAddress: evmAddress,
            token: token,
            amount: amount,
            operation: BridgeOperation.Mint,
            timestamp: block.timestamp,
            processed: true,
            verified: true,
            metadata: ""
        });
        
        // Mint tokens (assuming token contract supports minting)
        if (token != address(0)) {
            // This would require the token contract to have a mint function
            // For now, we'll transfer from bridge reserves
            IERC20(token).safeTransfer(evmAddress, amount);
        }
        
        emit AssetMinted(xrplTxHash, evmAddress, token, amount);
    }

    /**
     * @dev Burn tokens on EVM sidechain to unlock on XRPL
     */
    function burnTokens(
        address token,
        uint256 amount,
        string memory xrplAddress
    ) external nonReentrant whenNotPaused validToken(token) validAmount(amount) {
        require(bytes(xrplAddress).length > 0, "XRPL address required");
        
        // Calculate bridge fee
        uint256 bridgeFee = amount.mul(bridgeFeeRate).div(10000);
        uint256 netAmount = amount.sub(bridgeFee);
        
        // Transfer tokens from user
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        
        // Transfer bridge fee
        if (bridgeFee > 0) {
            IERC20(token).safeTransfer(feeCollector, bridgeFee);
        }
        
        // Record bridge transaction
        bytes32 txHash = keccak256(abi.encodePacked(
            block.timestamp,
            msg.sender,
            token,
            amount,
            xrplAddress
        ));
        
        bridgeTransactions[txHash] = BridgeTransaction({
            xrplTxHash: bytes32(0),
            evmAddress: msg.sender,
            token: token,
            amount: netAmount,
            operation: BridgeOperation.Burn,
            timestamp: block.timestamp,
            processed: false,
            verified: false,
            metadata: xrplAddress
        });
        
        totalTransactions++;
        totalVolume = totalVolume.add(amount);
        
        emit AssetBurned(msg.sender, xrplAddress, token, netAmount);
    }

    /**
     * @dev Transfer data between XRPL and EVM
     */
    function transferData(
        string memory xrplAddress,
        address evmAddress,
        bytes memory data
    ) external onlyAuthorizedValidator nonReentrant whenNotPaused {
        require(bytes(xrplAddress).length > 0, "XRPL address required");
        require(evmAddress != address(0), "Invalid EVM address");
        require(data.length > 0, "Data required");
        
        bytes32 transferId = keccak256(abi.encodePacked(
            block.timestamp,
            xrplAddress,
            evmAddress,
            data
        ));
        
        // Record data transfer
        bridgeTransactions[transferId] = BridgeTransaction({
            xrplTxHash: transferId,
            evmAddress: evmAddress,
            token: address(0),
            amount: 0,
            operation: BridgeOperation.DataTransfer,
            timestamp: block.timestamp,
            processed: true,
            verified: true,
            metadata: string(data)
        });
        
        emit DataTransferred(transferId, xrplAddress, evmAddress, data);
    }

    /**
     * @dev Migrate agent from XRPL to EVM
     */
    function migrateAgent(
        uint256 agentId,
        string memory xrplAgentId,
        string memory xrplOwner,
        string memory migrationData
    ) external nonReentrant whenNotPaused returns (uint256 migrationId) {
        require(agentId > 0, "Invalid agent ID");
        require(bytes(xrplAgentId).length > 0, "XRPL agent ID required");
        require(bytes(xrplOwner).length > 0, "XRPL owner required");
        
        migrationId = nextMigrationId++;
        
        agentMigrations[migrationId] = AgentMigration({
            agentId: agentId,
            xrplAgentId: xrplAgentId,
            evmOwner: msg.sender,
            xrplOwner: xrplOwner,
            migrationTime: block.timestamp,
            completed: false,
            migrationData: migrationData
        });
        
        emit AgentMigrated(agentId, xrplAgentId, msg.sender, false);
        
        return migrationId;
    }

    /**
     * @dev Complete agent migration
     */
    function completeAgentMigration(
        uint256 migrationId,
        bool success
    ) external onlyAuthorizedValidator nonReentrant whenNotPaused {
        require(migrationId > 0 && migrationId < nextMigrationId, "Invalid migration ID");
        
        AgentMigration storage migration = agentMigrations[migrationId];
        require(!migration.completed, "Migration already completed");
        
        migration.completed = true;
        
        emit AgentMigrated(migration.agentId, migration.xrplAgentId, migration.evmOwner, success);
    }

    /**
     * @dev Verify XRPL transaction (simplified implementation)
     */
    function _verifyXRPLTransaction(bytes32 xrplTxHash) internal view returns (bool) {
        // In a real implementation, this would:
        // 1. Query XRPL network for transaction
        // 2. Verify transaction signature
        // 3. Check transaction validity
        // 4. Confirm sufficient confirmations
        
        // For now, we'll simulate verification
        return xrplTxHash != bytes32(0);
    }

    /**
     * @dev Get bridge transaction
     */
    function getBridgeTransaction(bytes32 txHash) external view returns (BridgeTransaction memory) {
        return bridgeTransactions[txHash];
    }

    /**
     * @dev Get XRPL account info
     */
    function getXRPLAccount(string memory xrplAddress) external view returns (uint256 balance, bool isActive, uint256 lastUpdate) {
        XRPLAccount storage account = xrplAccounts[xrplAddress];
        return (account.balance, account.isActive, account.lastUpdate);
    }

    /**
     * @dev Get agent migration
     */
    function getAgentMigration(uint256 migrationId) external view returns (AgentMigration memory) {
        require(migrationId > 0 && migrationId < nextMigrationId, "Invalid migration ID");
        return agentMigrations[migrationId];
    }

    /**
     * @dev Add supported token
     */
    function addSupportedToken(address token) external onlyOwner {
        supportedTokens[token] = true;
    }

    /**
     * @dev Remove supported token
     */
    function removeSupportedToken(address token) external onlyOwner {
        supportedTokens[token] = false;
    }

    /**
     * @dev Authorize validator
     */
    function authorizeValidator(address validator) external onlyOwner {
        authorizedValidators[validator] = true;
    }

    /**
     * @dev Revoke validator authorization
     */
    function revokeValidator(address validator) external onlyOwner {
        authorizedValidators[validator] = false;
    }

    /**
     * @dev Set configuration parameters
     */
    function setConfig(
        uint256 _bridgeFeeRate,
        uint256 _minBridgeAmount,
        uint256 _maxBridgeAmount,
        uint256 _confirmationBlocks,
        uint256 _validatorThreshold
    ) external onlyOwner {
        bridgeFeeRate = _bridgeFeeRate;
        minBridgeAmount = _minBridgeAmount;
        maxBridgeAmount = _maxBridgeAmount;
        confirmationBlocks = _confirmationBlocks;
        validatorThreshold = _validatorThreshold;
    }

    /**
     * @dev Set fee collector
     */
    function setFeeCollector(address _feeCollector) external onlyOwner {
        require(_feeCollector != address(0), "Invalid address");
        feeCollector = _feeCollector;
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
        // Allow contract to receive ETH for bridging
    }
}
