// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title XRPLLending
 * @dev Peer-to-peer lending platform with XRP collateral
 * @author XRPL Ecosystem
 */
contract XRPLLending is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    struct Loan {
        uint256 id;
        address borrower;
        address lender;
        address collateralToken; // XRP or other supported tokens
        address loanToken; // Token being borrowed
        uint256 collateralAmount;
        uint256 loanAmount;
        uint256 interestRate; // Annual percentage rate (APR)
        uint256 duration; // Loan duration in seconds
        uint256 startTime;
        uint256 dueTime;
        uint256 liquidationThreshold; // Collateral value threshold for liquidation
        LoanStatus status;
        uint256 feesPaid;
    }

    struct CollateralPool {
        address token;
        uint256 totalDeposited;
        uint256 utilizationRate; // Percentage of pool being used
        uint256 baseInterestRate; // Base rate for this collateral type
        uint256 liquidationPenalty; // Penalty for liquidations
        bool active;
    }

    enum LoanStatus {
        Active,
        Repaid,
        Liquidated,
        Defaulted
    }

    // Events
    event LoanCreated(uint256 indexed loanId, address borrower, address lender, uint256 amount);
    event LoanRepaid(uint256 indexed loanId, uint256 principal, uint256 interest);
    event LoanLiquidated(uint256 indexed loanId, address liquidator, uint256 penalty);
    event CollateralDeposited(address indexed user, address token, uint256 amount);
    event CollateralWithdrawn(address indexed user, address token, uint256 amount);
    event InterestAccrued(uint256 indexed loanId, uint256 interest);

    // State variables
    mapping(uint256 => Loan) public loans;
    mapping(address => CollateralPool) public collateralPools;
    mapping(address => uint256) public userCollateral;
    mapping(address => uint256[]) public userLoans;
    mapping(address => bool) public authorizedTokens;
    mapping(address => uint256) public platformFees;
    
    uint256 public nextLoanId = 1;
    uint256 public constant MAX_INTEREST_RATE = 5000; // 50% APR max
    uint256 public constant MIN_COLLATERAL_RATIO = 150; // 150% minimum
    uint256 public constant LIQUIDATION_THRESHOLD = 120; // 120% liquidation threshold
    uint256 public constant PLATFORM_FEE_RATE = 25; // 0.25% platform fee
    
    address public feeCollector;
    uint256 public totalPlatformFees;

    // Modifiers
    modifier onlyAuthorizedToken(address token) {
        require(authorizedTokens[token], "Token not authorized");
        _;
    }

    modifier validLoan(uint256 loanId) {
        require(loanId > 0 && loanId < nextLoanId, "Invalid loan ID");
        _;
    }

    constructor(address _feeCollector) {
        feeCollector = _feeCollector;
    }

    /**
     * @dev Create a new loan request
     */
    function createLoan(
        address collateralToken,
        address loanToken,
        uint256 collateralAmount,
        uint256 loanAmount,
        uint256 interestRate,
        uint256 duration
    ) external nonReentrant onlyAuthorizedToken(collateralToken) onlyAuthorizedToken(loanToken) returns (uint256 loanId) {
        require(interestRate <= MAX_INTEREST_RATE, "Interest rate too high");
        require(duration >= 86400, "Duration too short"); // Minimum 1 day
        require(collateralAmount > 0 && loanAmount > 0, "Invalid amounts");
        
        // Calculate collateral ratio
        uint256 collateralRatio = calculateCollateralRatio(collateralToken, loanToken, collateralAmount, loanAmount);
        require(collateralRatio >= MIN_COLLATERAL_RATIO, "Insufficient collateral");

        loanId = nextLoanId++;
        
        loans[loanId] = Loan({
            id: loanId,
            borrower: msg.sender,
            lender: address(0),
            collateralToken: collateralToken,
            loanToken: loanToken,
            collateralAmount: collateralAmount,
            loanAmount: loanAmount,
            interestRate: interestRate,
            duration: duration,
            startTime: 0,
            dueTime: 0,
            liquidationThreshold: LIQUIDATION_THRESHOLD,
            status: LoanStatus.Active,
            feesPaid: 0
        });

        // Transfer collateral to contract
        IERC20(collateralToken).safeTransferFrom(msg.sender, address(this), collateralAmount);
        userCollateral[msg.sender] = userCollateral[msg.sender].add(collateralAmount);
        userLoans[msg.sender].push(loanId);

        emit LoanCreated(loanId, msg.sender, address(0), loanAmount);
    }

    /**
     * @dev Fund a loan (become the lender)
     */
    function fundLoan(uint256 loanId) external nonReentrant validLoan(loanId) {
        Loan storage loan = loans[loanId];
        require(loan.status == LoanStatus.Active, "Loan not available");
        require(loan.lender == address(0), "Loan already funded");
        require(msg.sender != loan.borrower, "Cannot fund own loan");

        // Calculate platform fee
        uint256 platformFee = loan.loanAmount.mul(PLATFORM_FEE_RATE).div(10000);
        uint256 netLoanAmount = loan.loanAmount.sub(platformFee);

        // Transfer loan tokens to borrower
        IERC20(loan.loanToken).safeTransferFrom(msg.sender, loan.borrower, netLoanAmount);
        
        // Transfer platform fee to fee collector
        IERC20(loan.loanToken).safeTransferFrom(msg.sender, feeCollector, platformFee);
        
        // Update loan details
        loan.lender = msg.sender;
        loan.startTime = block.timestamp;
        loan.dueTime = block.timestamp.add(loan.duration);
        loan.feesPaid = platformFee;

        // Update platform fees
        platformFees[loan.loanToken] = platformFees[loan.loanToken].add(platformFee);
        totalPlatformFees = totalPlatformFees.add(platformFee);

        emit LoanCreated(loanId, loan.borrower, msg.sender, loan.loanAmount);
    }

    /**
     * @dev Repay a loan
     */
    function repayLoan(uint256 loanId) external nonReentrant validLoan(loanId) {
        Loan storage loan = loans[loanId];
        require(loan.status == LoanStatus.Active, "Loan not active");
        require(msg.sender == loan.borrower, "Not the borrower");
        require(block.timestamp <= loan.dueTime, "Loan overdue");

        uint256 interest = calculateInterest(loanId);
        uint256 totalRepayment = loan.loanAmount.add(interest);

        // Transfer repayment to lender
        IERC20(loan.loanToken).safeTransferFrom(msg.sender, loan.lender, totalRepayment);
        
        // Return collateral to borrower
        IERC20(loan.collateralToken).safeTransfer(msg.sender, loan.collateralAmount);
        
        // Update loan status
        loan.status = LoanStatus.Repaid;
        userCollateral[msg.sender] = userCollateral[msg.sender].sub(loan.collateralAmount);

        emit LoanRepaid(loanId, loan.loanAmount, interest);
    }

    /**
     * @dev Liquidate an undercollateralized loan
     */
    function liquidateLoan(uint256 loanId) external nonReentrant validLoan(loanId) {
        Loan storage loan = loans[loanId];
        require(loan.status == LoanStatus.Active, "Loan not active");
        require(block.timestamp > loan.dueTime || isUndercollateralized(loanId), "Loan not liquidatable");

        uint256 currentCollateralRatio = calculateCurrentCollateralRatio(loanId);
        require(currentCollateralRatio < loan.liquidationThreshold, "Collateral ratio sufficient");

        // Calculate liquidation penalty
        uint256 penalty = loan.collateralAmount.mul(collateralPools[loan.collateralToken].liquidationPenalty).div(10000);
        uint256 collateralToLiquidator = loan.collateralAmount.sub(penalty);

        // Transfer collateral to liquidator
        IERC20(loan.collateralToken).safeTransfer(msg.sender, collateralToLiquidator);
        
        // Transfer remaining collateral to lender
        IERC20(loan.collateralToken).safeTransfer(loan.lender, penalty);

        // Update loan status
        loan.status = LoanStatus.Liquidated;
        userCollateral[loan.borrower] = userCollateral[loan.borrower].sub(loan.collateralAmount);

        emit LoanLiquidated(loanId, msg.sender, penalty);
    }

    /**
     * @dev Calculate interest for a loan
     */
    function calculateInterest(uint256 loanId) public view validLoan(loanId) returns (uint256) {
        Loan memory loan = loans[loanId];
        if (loan.startTime == 0) return 0;

        uint256 timeElapsed = block.timestamp.sub(loan.startTime);
        uint256 annualInterest = loan.loanAmount.mul(loan.interestRate).div(10000);
        
        return annualInterest.mul(timeElapsed).div(365 days);
    }

    /**
     * @dev Calculate collateral ratio
     */
    function calculateCollateralRatio(
        address collateralToken,
        address loanToken,
        uint256 collateralAmount,
        uint256 loanAmount
    ) public view returns (uint256) {
        // Simplified price calculation - in production, use oracle
        uint256 collateralValue = collateralAmount; // Assume 1:1 for simplicity
        uint256 loanValue = loanAmount;
        
        return collateralValue.mul(100).div(loanValue);
    }

    /**
     * @dev Check if loan is undercollateralized
     */
    function isUndercollateralized(uint256 loanId) public view validLoan(loanId) returns (bool) {
        uint256 currentRatio = calculateCurrentCollateralRatio(loanId);
        return currentRatio < loans[loanId].liquidationThreshold;
    }

    /**
     * @dev Calculate current collateral ratio
     */
    function calculateCurrentCollateralRatio(uint256 loanId) public view validLoan(loanId) returns (uint256) {
        Loan memory loan = loans[loanId];
        return calculateCollateralRatio(loan.collateralToken, loan.loanToken, loan.collateralAmount, loan.loanAmount);
    }

    /**
     * @dev Get user's active loans
     */
    function getUserLoans(address user) external view returns (uint256[] memory) {
        return userLoans[user];
    }

    /**
     * @dev Get loan details
     */
    function getLoan(uint256 loanId) external view validLoan(loanId) returns (Loan memory) {
        return loans[loanId];
    }

    /**
     * @dev Authorize a token for use in the platform
     */
    function authorizeToken(address token) external onlyOwner {
        authorizedTokens[token] = true;
    }

    /**
     * @dev Set collateral pool parameters
     */
    function setCollateralPool(
        address token,
        uint256 baseInterestRate,
        uint256 liquidationPenalty
    ) external onlyOwner {
        collateralPools[token] = CollateralPool({
            token: token,
            totalDeposited: 0,
            utilizationRate: 0,
            baseInterestRate: baseInterestRate,
            liquidationPenalty: liquidationPenalty,
            active: true
        });
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
}
