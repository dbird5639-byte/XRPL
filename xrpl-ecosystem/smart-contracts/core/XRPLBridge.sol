// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/**
 * @title XRPLBridge
 * @dev Bridge contract for transferring assets between XRPL and EVM sidechain
 */
contract XRPLBridge is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // Events
    event Deposit(
        address indexed user,
        address indexed token,
        uint256 amount,
        string xrplAddress,
        uint256 nonce,
        bytes32 indexed depositId
    );
    
    event Withdrawal(
        address indexed user,
        address indexed token,
        uint256 amount,
        string xrplAddress,
        uint256 nonce,
        bytes32 indexed withdrawalId
    );
    
    event ValidatorAdded(address indexed validator);
    event ValidatorRemoved(address indexed validator);
    event ValidatorThresholdUpdated(uint256 newThreshold);
    
    // Structs
    struct DepositRequest {
        address user;
        address token;
        uint256 amount;
        string xrplAddress;
        uint256 nonce;
        bool processed;
        uint256 timestamp;
    }
    
    struct WithdrawalRequest {
        address user;
        address token;
        uint256 amount;
        string xrplAddress;
        uint256 nonce;
        bool processed;
        uint256 timestamp;
    }
    
    // State variables
    mapping(bytes32 => DepositRequest) public deposits;
    mapping(bytes32 => WithdrawalRequest) public withdrawals;
    mapping(address => bool) public validators;
    mapping(address => uint256) public nonces;
    mapping(bytes32 => bool) public processedTransactions;
    
    uint256 public validatorThreshold = 3;
    uint256 public validatorCount = 0;
    uint256 public constant MAX_VALIDATORS = 21;
    
    IERC20 public xrpToken;
    address public feeRecipient;
    uint256 public bridgeFee = 0; // Fee in basis points (0.01%)
    
    // Modifiers
    modifier onlyValidator() {
        require(validators[msg.sender], "Not a validator");
        _;
    }
    
    modifier validAmount(uint256 amount) {
        require(amount > 0, "Amount must be greater than 0");
        _;
    }
    
    modifier notProcessed(bytes32 txId) {
        require(!processedTransactions[txId], "Transaction already processed");
        _;
    }
    
    constructor(address _xrpToken, address _feeRecipient) {
        xrpToken = IERC20(_xrpToken);
        feeRecipient = _feeRecipient;
    }
    
    /**
     * @dev Deposit tokens to bridge to XRPL
     * @param token Token contract address
     * @param amount Amount to deposit
     * @param xrplAddress XRPL destination address
     */
    function deposit(
        address token,
        uint256 amount,
        string calldata xrplAddress
    ) external nonReentrant whenNotPaused validAmount(amount) {
        require(bytes(xrplAddress).length > 0, "Invalid XRPL address");
        
        uint256 nonce = nonces[msg.sender]++;
        bytes32 depositId = keccak256(
            abi.encodePacked(msg.sender, token, amount, xrplAddress, nonce, block.timestamp)
        );
        
        // Calculate bridge fee
        uint256 fee = (amount * bridgeFee) / 10000;
        uint256 depositAmount = amount - fee;
        
        // Transfer tokens from user
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        
        // Transfer fee to fee recipient
        if (fee > 0) {
            IERC20(token).safeTransfer(feeRecipient, fee);
        }
        
        // Record deposit
        deposits[depositId] = DepositRequest({
            user: msg.sender,
            token: token,
            amount: depositAmount,
            xrplAddress: xrplAddress,
            nonce: nonce,
            processed: false,
            timestamp: block.timestamp
        });
        
        emit Deposit(msg.sender, token, depositAmount, xrplAddress, nonce, depositId);
    }
    
    /**
     * @dev Withdraw tokens from XRPL to EVM sidechain
     * @param user Recipient address
     * @param token Token contract address
     * @param amount Amount to withdraw
     * @param xrplAddress XRPL source address
     * @param nonce Transaction nonce
     * @param signatures Validator signatures
     */
    function withdraw(
        address user,
        address token,
        uint256 amount,
        string calldata xrplAddress,
        uint256 nonce,
        bytes[] calldata signatures
    ) external nonReentrant whenNotPaused validAmount(amount) {
        bytes32 withdrawalId = keccak256(
            abi.encodePacked(user, token, amount, xrplAddress, nonce, block.timestamp)
        );
        
        require(!processedTransactions[withdrawalId], "Withdrawal already processed");
        require(_verifySignatures(withdrawalId, signatures), "Invalid signatures");
        
        // Record withdrawal
        withdrawals[withdrawalId] = WithdrawalRequest({
            user: user,
            token: token,
            amount: amount,
            xrplAddress: xrplAddress,
            nonce: nonce,
            processed: true,
            timestamp: block.timestamp
        });
        
        processedTransactions[withdrawalId] = true;
        
        // Transfer tokens to user
        IERC20(token).safeTransfer(user, amount);
        
        emit Withdrawal(user, token, amount, xrplAddress, nonce, withdrawalId);
    }
    
    /**
     * @dev Add a validator (only owner)
     * @param validator Validator address
     */
    function addValidator(address validator) external onlyOwner {
        require(validator != address(0), "Invalid validator address");
        require(!validators[validator], "Validator already exists");
        require(validatorCount < MAX_VALIDATORS, "Too many validators");
        
        validators[validator] = true;
        validatorCount++;
        
        emit ValidatorAdded(validator);
    }
    
    /**
     * @dev Remove a validator (only owner)
     * @param validator Validator address
     */
    function removeValidator(address validator) external onlyOwner {
        require(validators[validator], "Validator does not exist");
        require(validatorCount > 1, "Cannot remove last validator");
        
        validators[validator] = false;
        validatorCount--;
        
        emit ValidatorRemoved(validator);
    }
    
    /**
     * @dev Update validator threshold (only owner)
     * @param newThreshold New threshold value
     */
    function updateValidatorThreshold(uint256 newThreshold) external onlyOwner {
        require(newThreshold > 0, "Threshold must be greater than 0");
        require(newThreshold <= validatorCount, "Threshold too high");
        
        validatorThreshold = newThreshold;
        
        emit ValidatorThresholdUpdated(newThreshold);
    }
    
    /**
     * @dev Update bridge fee (only owner)
     * @param newFee New fee in basis points
     */
    function updateBridgeFee(uint256 newFee) external onlyOwner {
        require(newFee <= 1000, "Fee too high"); // Max 10%
        bridgeFee = newFee;
    }
    
    /**
     * @dev Update fee recipient (only owner)
     * @param newFeeRecipient New fee recipient address
     */
    function updateFeeRecipient(address newFeeRecipient) external onlyOwner {
        require(newFeeRecipient != address(0), "Invalid address");
        feeRecipient = newFeeRecipient;
    }
    
    /**
     * @dev Pause the bridge
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause the bridge
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Emergency withdraw tokens (only owner)
     * @param token Token contract address
     * @param amount Amount to withdraw
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }
    
    /**
     * @dev Get deposit details
     * @param depositId Deposit ID
     * @return Deposit details
     */
    function getDeposit(bytes32 depositId) external view returns (DepositRequest memory) {
        return deposits[depositId];
    }
    
    /**
     * @dev Get withdrawal details
     * @param withdrawalId Withdrawal ID
     * @return Withdrawal details
     */
    function getWithdrawal(bytes32 withdrawalId) external view returns (WithdrawalRequest memory) {
        return withdrawals[withdrawalId];
    }
    
    /**
     * @dev Check if address is validator
     * @param validator Validator address
     * @return True if validator
     */
    function isValidator(address validator) external view returns (bool) {
        return validators[validator];
    }
    
    /**
     * @dev Get user nonce
     * @param user User address
     * @return Current nonce
     */
    function getUserNonce(address user) external view returns (uint256) {
        return nonces[user];
    }
    
    // Internal functions
    function _verifySignatures(bytes32 messageHash, bytes[] calldata signatures) internal view returns (bool) {
        require(signatures.length >= validatorThreshold, "Insufficient signatures");
        
        bytes32 ethSignedMessageHash = messageHash.toEthSignedMessageHash();
        address[] memory signers = new address[](signatures.length);
        
        for (uint256 i = 0; i < signatures.length; i++) {
            address signer = ethSignedMessageHash.recover(signatures[i]);
            require(validators[signer], "Invalid signer");
            
            // Check for duplicate signatures
            for (uint256 j = 0; j < i; j++) {
                require(signers[j] != signer, "Duplicate signature");
            }
            
            signers[i] = signer;
        }
        
        return true;
    }
}