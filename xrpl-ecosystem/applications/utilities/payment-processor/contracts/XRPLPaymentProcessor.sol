// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * @title XRPLPaymentProcessor
 * @dev Merchant payment gateway for XRPL with transaction fees
 * @author XRPL Ecosystem
 */
contract XRPLPaymentProcessor is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;
    using ECDSA for bytes32;

    struct Payment {
        uint256 id;
        address merchant;
        address customer;
        address token;
        uint256 amount;
        uint256 fee;
        uint256 timestamp;
        PaymentStatus status;
        string orderId;
        bytes32 paymentHash;
    }

    struct Merchant {
        address wallet;
        string name;
        string description;
        uint256 totalVolume;
        uint256 totalFees;
        uint256 feeRate; // Basis points
        bool active;
        uint256 registrationTime;
    }

    struct Refund {
        uint256 paymentId;
        uint256 amount;
        uint256 timestamp;
        string reason;
        bool processed;
    }

    enum PaymentStatus {
        Pending,
        Completed,
        Refunded,
        Failed,
        Cancelled
    }

    // Events
    event PaymentInitiated(uint256 indexed paymentId, address merchant, address customer, uint256 amount);
    event PaymentCompleted(uint256 indexed paymentId, uint256 fee);
    event PaymentRefunded(uint256 indexed paymentId, uint256 amount);
    event MerchantRegistered(address indexed merchant, string name, uint256 feeRate);
    event MerchantUpdated(address indexed merchant, uint256 newFeeRate);
    event FeeCollected(address indexed merchant, uint256 amount);

    // State variables
    mapping(uint256 => Payment) public payments;
    mapping(address => Merchant) public merchants;
    mapping(address => uint256[]) public merchantPayments;
    mapping(address => uint256[]) public customerPayments;
    mapping(uint256 => Refund) public refunds;
    mapping(address => bool) public authorizedTokens;
    mapping(bytes32 => bool) public usedPaymentHashes;
    
    uint256 public nextPaymentId = 1;
    uint256 public constant MIN_FEE_RATE = 10; // 0.1%
    uint256 public constant MAX_FEE_RATE = 500; // 5%
    uint256 public constant PLATFORM_FEE_RATE = 25; // 0.25%
    uint256 public constant MIN_PAYMENT_AMOUNT = 1000; // Minimum payment amount
    
    address public feeCollector;
    uint256 public totalPlatformFees;
    uint256 public totalProcessedVolume;

    // Modifiers
    modifier onlyMerchant() {
        require(merchants[msg.sender].active, "Not a registered merchant");
        _;
    }

    modifier onlyAuthorizedToken(address token) {
        require(authorizedTokens[token], "Token not authorized");
        _;
    }

    modifier validPayment(uint256 paymentId) {
        require(paymentId > 0 && paymentId < nextPaymentId, "Invalid payment ID");
        _;
    }

    constructor(address _feeCollector) {
        feeCollector = _feeCollector;
    }

    /**
     * @dev Register a new merchant
     */
    function registerMerchant(
        string memory name,
        string memory description,
        uint256 feeRate
    ) external returns (bool) {
        require(!merchants[msg.sender].active, "Merchant already registered");
        require(feeRate >= MIN_FEE_RATE && feeRate <= MAX_FEE_RATE, "Invalid fee rate");
        require(bytes(name).length > 0, "Name required");

        merchants[msg.sender] = Merchant({
            wallet: msg.sender,
            name: name,
            description: description,
            totalVolume: 0,
            totalFees: 0,
            feeRate: feeRate,
            active: true,
            registrationTime: block.timestamp
        });

        emit MerchantRegistered(msg.sender, name, feeRate);
        return true;
    }

    /**
     * @dev Initiate a payment
     */
    function initiatePayment(
        address merchant,
        address token,
        uint256 amount,
        string memory orderId
    ) external nonReentrant onlyAuthorizedToken(token) returns (uint256 paymentId) {
        require(merchants[merchant].active, "Merchant not active");
        require(amount >= MIN_PAYMENT_AMOUNT, "Amount too small");
        require(msg.sender != merchant, "Cannot pay yourself");

        // Calculate fees
        uint256 merchantFee = amount.mul(merchants[merchant].feeRate).div(10000);
        uint256 platformFee = amount.mul(PLATFORM_FEE_RATE).div(10000);
        uint256 totalFee = merchantFee.add(platformFee);
        uint256 netAmount = amount.sub(totalFee);

        // Create payment hash for security
        bytes32 paymentHash = keccak256(abi.encodePacked(
            msg.sender,
            merchant,
            token,
            amount,
            orderId,
            block.timestamp
        ));
        require(!usedPaymentHashes[paymentHash], "Duplicate payment");

        paymentId = nextPaymentId++;
        payments[paymentId] = Payment({
            id: paymentId,
            merchant: merchant,
            customer: msg.sender,
            token: token,
            amount: amount,
            fee: totalFee,
            timestamp: block.timestamp,
            status: PaymentStatus.Pending,
            orderId: orderId,
            paymentHash: paymentHash
        });

        // Transfer payment to contract
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        // Update merchant data
        merchants[merchant].totalVolume = merchants[merchant].totalVolume.add(amount);
        merchants[merchant].totalFees = merchants[merchant].totalFees.add(merchantFee);

        // Update global data
        totalProcessedVolume = totalProcessedVolume.add(amount);
        totalPlatformFees = totalPlatformFees.add(platformFee);

        // Store payment references
        merchantPayments[merchant].push(paymentId);
        customerPayments[msg.sender].push(paymentId);
        usedPaymentHashes[paymentHash] = true;

        emit PaymentInitiated(paymentId, merchant, msg.sender, amount);
    }

    /**
     * @dev Complete a payment (merchant confirms receipt)
     */
    function completePayment(uint256 paymentId) external nonReentrant validPayment(paymentId) {
        Payment storage payment = payments[paymentId];
        require(payment.merchant == msg.sender, "Not the merchant");
        require(payment.status == PaymentStatus.Pending, "Payment not pending");

        // Calculate fee distribution
        uint256 merchantFee = payment.amount.mul(merchants[payment.merchant].feeRate).div(10000);
        uint256 platformFee = payment.amount.mul(PLATFORM_FEE_RATE).div(10000);
        uint256 netAmount = payment.amount.sub(merchantFee).sub(platformFee);

        // Transfer funds to merchant
        IERC20(payment.token).safeTransfer(payment.merchant, netAmount);
        
        // Transfer platform fee to fee collector
        IERC20(payment.token).safeTransfer(feeCollector, platformFee);

        // Update payment status
        payment.status = PaymentStatus.Completed;

        emit PaymentCompleted(paymentId, payment.fee);
        emit FeeCollected(payment.merchant, merchantFee);
    }

    /**
     * @dev Process a refund
     */
    function processRefund(
        uint256 paymentId,
        uint256 refundAmount,
        string memory reason
    ) external nonReentrant validPayment(paymentId) {
        Payment storage payment = payments[paymentId];
        require(payment.merchant == msg.sender, "Not the merchant");
        require(payment.status == PaymentStatus.Completed, "Payment not completed");
        require(refundAmount <= payment.amount, "Refund amount too high");

        // Create refund record
        refunds[paymentId] = Refund({
            paymentId: paymentId,
            amount: refundAmount,
            timestamp: block.timestamp,
            reason: reason,
            processed: true
        });

        // Transfer refund to customer
        IERC20(payment.token).safeTransfer(payment.customer, refundAmount);

        // Update payment status
        payment.status = PaymentStatus.Refunded;

        // Update merchant volume (subtract refund)
        merchants[payment.merchant].totalVolume = merchants[payment.merchant].totalVolume.sub(refundAmount);

        emit PaymentRefunded(paymentId, refundAmount);
    }

    /**
     * @dev Cancel a pending payment
     */
    function cancelPayment(uint256 paymentId) external nonReentrant validPayment(paymentId) {
        Payment storage payment = payments[paymentId];
        require(payment.customer == msg.sender, "Not the customer");
        require(payment.status == PaymentStatus.Pending, "Payment not pending");

        // Refund the customer
        IERC20(payment.token).safeTransfer(payment.customer, payment.amount);

        // Update payment status
        payment.status = PaymentStatus.Cancelled;

        // Update merchant volume (subtract cancelled payment)
        merchants[payment.merchant].totalVolume = merchants[payment.merchant].totalVolume.sub(payment.amount);

        emit PaymentRefunded(paymentId, payment.amount);
    }

    /**
     * @dev Get payment details
     */
    function getPayment(uint256 paymentId) external view validPayment(paymentId) returns (Payment memory) {
        return payments[paymentId];
    }

    /**
     * @dev Get merchant information
     */
    function getMerchant(address merchant) external view returns (Merchant memory) {
        return merchants[merchant];
    }

    /**
     * @dev Get merchant's payments
     */
    function getMerchantPayments(address merchant) external view returns (uint256[] memory) {
        return merchantPayments[merchant];
    }

    /**
     * @dev Get customer's payments
     */
    function getCustomerPayments(address customer) external view returns (uint256[] memory) {
        return customerPayments[customer];
    }

    /**
     * @dev Get refund information
     */
    function getRefund(uint256 paymentId) external view returns (Refund memory) {
        return refunds[paymentId];
    }

    /**
     * @dev Update merchant fee rate
     */
    function updateMerchantFeeRate(uint256 newFeeRate) external onlyMerchant {
        require(newFeeRate >= MIN_FEE_RATE && newFeeRate <= MAX_FEE_RATE, "Invalid fee rate");
        merchants[msg.sender].feeRate = newFeeRate;
        emit MerchantUpdated(msg.sender, newFeeRate);
    }

    /**
     * @dev Authorize a token for payments
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
     * @dev Set fee collector address
     */
    function setFeeCollector(address _feeCollector) external onlyOwner {
        require(_feeCollector != address(0), "Invalid address");
        feeCollector = _feeCollector;
    }

    /**
     * @dev Deactivate a merchant
     */
    function deactivateMerchant(address merchant) external onlyOwner {
        merchants[merchant].active = false;
    }

    /**
     * @dev Activate a merchant
     */
    function activateMerchant(address merchant) external onlyOwner {
        merchants[merchant].active = true;
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
     * @dev Get platform statistics
     */
    function getPlatformStats() external view returns (
        uint256 totalVolume,
        uint256 totalFees,
        uint256 totalPayments,
        uint256 activeMerchants
    ) {
        totalVolume = totalProcessedVolume;
        totalFees = totalPlatformFees;
        totalPayments = nextPaymentId - 1;
        
        // Count active merchants (simplified)
        activeMerchants = 0; // Would need to iterate through merchants in production
    }
}
