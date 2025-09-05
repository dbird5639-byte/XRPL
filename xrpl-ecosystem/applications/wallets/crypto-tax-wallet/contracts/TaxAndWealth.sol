// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title TaxAndWealth
 * @dev Smart contract for crypto tax calculation and wealth building guidance
 */
contract TaxAndWealth is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;
    using Counters for Counters.Counter;

    // Events
    event BetaKeyGenerated(
        string indexed betaKey,
        address indexed generator,
        uint256 timestamp
    );
    
    event BetaKeyRedeemed(
        string indexed betaKey,
        address indexed user,
        uint256 timestamp
    );
    
    event TransactionRecorded(
        address indexed user,
        bytes32 indexed transactionId,
        string transactionType,
        uint256 amount,
        uint256 timestamp
    );
    
    event TaxCalculationCompleted(
        address indexed user,
        uint256 taxYear,
        uint256 totalGains,
        uint256 totalLosses,
        uint256 taxOwed,
        uint256 timestamp
    );
    
    event WealthGoalSet(
        address indexed user,
        uint256 indexed goalId,
        string goalType,
        uint256 targetAmount,
        uint256 targetDate,
        uint256 timestamp
    );
    
    event InvestmentAdviceGenerated(
        address indexed user,
        uint256 indexed adviceId,
        string adviceType,
        uint256 confidence,
        uint256 timestamp
    );
    
    event PortfolioAnalyzed(
        address indexed user,
        uint256 totalValue,
        uint256 riskScore,
        uint256 diversificationScore,
        uint256 timestamp
    );
    
    event TaxOptimizationSuggested(
        address indexed user,
        string strategy,
        uint256 potentialSavings,
        uint256 timestamp
    );

    // Structs
    struct BetaKey {
        string key;
        address generator;
        bool redeemed;
        address redeemer;
        uint256 generationTime;
        uint256 redemptionTime;
        uint256 tier; // 1: Basic, 2: Premium, 3: Pro
    }
    
    struct Transaction {
        bytes32 transactionId;
        address user;
        string transactionType; // "buy", "sell", "swap", "stake", "unstake", "reward"
        address token;
        uint256 amount;
        uint256 price;
        uint256 timestamp;
        string description;
        bool taxable;
    }
    
    struct TaxCalculation {
        address user;
        uint256 taxYear;
        uint256 totalGains;
        uint256 totalLosses;
        uint256 netGains;
        uint256 taxOwed;
        uint256 taxRate;
        bool calculated;
        uint256 timestamp;
    }
    
    struct WealthGoal {
        uint256 goalId;
        address user;
        string goalType; // "retirement", "house", "education", "emergency", "investment"
        uint256 targetAmount;
        uint256 currentAmount;
        uint256 targetDate;
        uint256 monthlyContribution;
        bool achieved;
        uint256 creationTime;
    }
    
    struct InvestmentAdvice {
        uint256 adviceId;
        address user;
        string adviceType; // "buy", "sell", "hold", "diversify", "rebalance"
        string asset;
        uint256 amount;
        uint256 confidence; // 1-100
        string reasoning;
        uint256 timestamp;
    }
    
    struct PortfolioAnalysis {
        address user;
        uint256 totalValue;
        uint256 riskScore; // 1-100
        uint256 diversificationScore; // 1-100
        uint256 performanceScore; // 1-100
        string[] recommendations;
        uint256 timestamp;
    }
    
    struct TaxOptimization {
        string strategy;
        string description;
        uint256 potentialSavings;
        uint256 riskLevel; // 1-5
        bool applicable;
    }

    // State variables
    mapping(string => BetaKey) public betaKeys;
    mapping(address => Transaction[]) public userTransactions;
    mapping(address => mapping(uint256 => TaxCalculation)) public taxCalculations;
    mapping(address => WealthGoal[]) public userGoals;
    mapping(address => InvestmentAdvice[]) public userAdvice;
    mapping(address => PortfolioAnalysis) public portfolioAnalyses;
    mapping(address => bool) public betaUsers;
    mapping(address => uint256) public userTier; // 1: Basic, 2: Premium, 3: Pro
    
    Counters.Counter private _goalIdCounter;
    Counters.Counter private _adviceIdCounter;
    Counters.Counter private _betaKeyCounter;
    
    IERC20 public paymentToken;
    address public feeRecipient;
    
    uint256 public basicFee = 1000; // 10 XRP in drops
    uint256 public premiumFee = 5000; // 50 XRP in drops
    uint256 public proFee = 10000; // 100 XRP in drops
    uint256 public taxCalculationFee = 2000; // 20 XRP in drops
    uint256 public portfolioAnalysisFee = 1500; // 15 XRP in drops
    
    uint256 public constant MAX_BETA_KEYS = 1000;
    uint256 public constant BETA_KEY_LENGTH = 16;
    
    string[] public supportedTokens = [
        "XRP", "BTC", "ETH", "USDC", "USDT", "ADA", "DOT", "LINK", "UNI", "AAVE"
    ];
    
    mapping(string => uint256) public tokenPrices; // Mock price feed
    mapping(string => TaxOptimization) public taxStrategies;

    // Modifiers
    modifier onlyBetaUser() {
        require(betaUsers[msg.sender], "Beta access required");
        _;
    }
    
    modifier validTier(uint256 tier) {
        require(tier >= 1 && tier <= 3, "Invalid tier");
        _;
    }
    
    modifier validAmount(uint256 amount) {
        require(amount > 0, "Amount must be greater than 0");
        _;
    }

    constructor(address _paymentToken, address _feeRecipient) {
        paymentToken = IERC20(_paymentToken);
        feeRecipient = _feeRecipient;
        
        _initializeTaxStrategies();
        _initializeTokenPrices();
    }

    /**
     * @dev Generate beta keys (only owner)
     * @param count Number of beta keys to generate
     * @param tier Tier level for the keys
     */
    function generateBetaKeys(uint256 count, uint256 tier) external onlyOwner validTier(tier) {
        require(_betaKeyCounter.current() + count <= MAX_BETA_KEYS, "Exceeds max beta keys");
        
        for (uint256 i = 0; i < count; i++) {
            string memory betaKey = _generateRandomKey();
            
            betaKeys[betaKey] = BetaKey({
                key: betaKey,
                generator: msg.sender,
                redeemed: false,
                redeemer: address(0),
                generationTime: block.timestamp,
                redemptionTime: 0,
                tier: tier
            });
            
            _betaKeyCounter.increment();
            
            emit BetaKeyGenerated(betaKey, msg.sender, block.timestamp);
        }
    }

    /**
     * @dev Redeem a beta key
     * @param betaKey Beta key to redeem
     */
    function redeemBetaKey(string calldata betaKey) external {
        require(!betaUsers[msg.sender], "Already a beta user");
        require(bytes(betaKey).length == BETA_KEY_LENGTH, "Invalid beta key format");
        require(betaKeys[betaKey].key != "", "Beta key does not exist");
        require(!betaKeys[betaKey].redeemed, "Beta key already redeemed");
        
        betaKeys[betaKey].redeemed = true;
        betaKeys[betaKey].redeemer = msg.sender;
        betaKeys[betaKey].redemptionTime = block.timestamp;
        
        betaUsers[msg.sender] = true;
        userTier[msg.sender] = betaKeys[betaKey].tier;
        
        emit BetaKeyRedeemed(betaKey, msg.sender, block.timestamp);
    }

    /**
     * @dev Record a transaction
     * @param transactionType Type of transaction
     * @param token Token address or symbol
     * @param amount Transaction amount
     * @param price Price at time of transaction
     * @param description Transaction description
     * @param taxable Whether transaction is taxable
     */
    function recordTransaction(
        string calldata transactionType,
        address token,
        uint256 amount,
        uint256 price,
        string calldata description,
        bool taxable
    ) external onlyBetaUser validAmount(amount) {
        bytes32 transactionId = keccak256(abi.encodePacked(
            msg.sender,
            transactionType,
            token,
            amount,
            block.timestamp
        ));
        
        Transaction memory newTransaction = Transaction({
            transactionId: transactionId,
            user: msg.sender,
            transactionType: transactionType,
            token: token,
            amount: amount,
            price: price,
            timestamp: block.timestamp,
            description: description,
            taxable: taxable
        });
        
        userTransactions[msg.sender].push(newTransaction);
        
        emit TransactionRecorded(msg.sender, transactionId, transactionType, amount, block.timestamp);
    }

    /**
     * @dev Calculate taxes for a year
     * @param taxYear Tax year to calculate
     */
    function calculateTaxes(uint256 taxYear) external onlyBetaUser nonReentrant {
        require(taxYear >= 2020 && taxYear <= 2030, "Invalid tax year");
        require(!taxCalculations[msg.sender][taxYear].calculated, "Already calculated");
        
        Transaction[] memory transactions = userTransactions[msg.sender];
        uint256 totalGains = 0;
        uint256 totalLosses = 0;
        
        // Calculate gains and losses from transactions
        for (uint256 i = 0; i < transactions.length; i++) {
            if (transactions[i].taxable && 
                transactions[i].timestamp >= taxYear * 365 days && 
                transactions[i].timestamp < (taxYear + 1) * 365 days) {
                
                if (keccak256(bytes(transactions[i].transactionType)) == keccak256(bytes("sell"))) {
                    // Simplified gain/loss calculation
                    uint256 costBasis = transactions[i].amount * transactions[i].price;
                    uint256 proceeds = transactions[i].amount * tokenPrices["XRP"]; // Mock current price
                    
                    if (proceeds > costBasis) {
                        totalGains += proceeds - costBasis;
                    } else {
                        totalLosses += costBasis - proceeds;
                    }
                }
            }
        }
        
        uint256 netGains = totalGains > totalLosses ? totalGains - totalLosses : 0;
        uint256 taxOwed = _calculateTaxOwed(netGains);
        uint256 taxRate = netGains > 0 ? (taxOwed * 10000) / netGains : 0;
        
        taxCalculations[msg.sender][taxYear] = TaxCalculation({
            user: msg.sender,
            taxYear: taxYear,
            totalGains: totalGains,
            totalLosses: totalLosses,
            netGains: netGains,
            taxOwed: taxOwed,
            taxRate: taxRate,
            calculated: true,
            timestamp: block.timestamp
        });
        
        emit TaxCalculationCompleted(msg.sender, taxYear, totalGains, totalLosses, taxOwed, block.timestamp);
    }

    /**
     * @dev Set a wealth building goal
     * @param goalType Type of goal
     * @param targetAmount Target amount
     * @param targetDate Target date (timestamp)
     * @param monthlyContribution Monthly contribution amount
     */
    function setWealthGoal(
        string calldata goalType,
        uint256 targetAmount,
        uint256 targetDate,
        uint256 monthlyContribution
    ) external onlyBetaUser validAmount(targetAmount) {
        require(targetDate > block.timestamp, "Invalid target date");
        require(monthlyContribution > 0, "Invalid monthly contribution");
        
        uint256 goalId = _goalIdCounter.current();
        _goalIdCounter.increment();
        
        WealthGoal memory newGoal = WealthGoal({
            goalId: goalId,
            user: msg.sender,
            goalType: goalType,
            targetAmount: targetAmount,
            currentAmount: 0,
            targetDate: targetDate,
            monthlyContribution: monthlyContribution,
            achieved: false,
            creationTime: block.timestamp
        });
        
        userGoals[msg.sender].push(newGoal);
        
        emit WealthGoalSet(msg.sender, goalId, goalType, targetAmount, targetDate, block.timestamp);
    }

    /**
     * @dev Update goal progress
     * @param goalId Goal ID
     * @param additionalAmount Additional amount to add
     */
    function updateGoalProgress(uint256 goalId, uint256 additionalAmount) external onlyBetaUser {
        WealthGoal[] storage goals = userGoals[msg.sender];
        
        for (uint256 i = 0; i < goals.length; i++) {
            if (goals[i].goalId == goalId) {
                goals[i].currentAmount += additionalAmount;
                
                if (goals[i].currentAmount >= goals[i].targetAmount) {
                    goals[i].achieved = true;
                }
                break;
            }
        }
    }

    /**
     * @dev Generate investment advice
     * @param adviceType Type of advice
     * @param asset Asset to advise on
     * @param amount Amount to consider
     * @param reasoning Reasoning for the advice
     */
    function generateInvestmentAdvice(
        string calldata adviceType,
        string calldata asset,
        uint256 amount,
        string calldata reasoning
    ) external onlyBetaUser {
        require(userTier[msg.sender] >= 2, "Premium tier required");
        
        uint256 adviceId = _adviceIdCounter.current();
        _adviceIdCounter.increment();
        
        uint256 confidence = _calculateAdviceConfidence(adviceType, asset, amount);
        
        InvestmentAdvice memory newAdvice = InvestmentAdvice({
            adviceId: adviceId,
            user: msg.sender,
            adviceType: adviceType,
            asset: asset,
            amount: amount,
            confidence: confidence,
            reasoning: reasoning,
            timestamp: block.timestamp
        });
        
        userAdvice[msg.sender].push(newAdvice);
        
        emit InvestmentAdviceGenerated(msg.sender, adviceId, adviceType, confidence, block.timestamp);
    }

    /**
     * @dev Analyze portfolio
     */
    function analyzePortfolio() external onlyBetaUser {
        require(userTier[msg.sender] >= 2, "Premium tier required");
        
        Transaction[] memory transactions = userTransactions[msg.sender];
        uint256 totalValue = 0;
        uint256 riskScore = _calculateRiskScore(transactions);
        uint256 diversificationScore = _calculateDiversificationScore(transactions);
        uint256 performanceScore = _calculatePerformanceScore(transactions);
        
        // Calculate total portfolio value
        for (uint256 i = 0; i < transactions.length; i++) {
            if (keccak256(bytes(transactions[i].transactionType)) == keccak256(bytes("buy"))) {
                totalValue += transactions[i].amount * tokenPrices["XRP"]; // Mock calculation
            }
        }
        
        string[] memory recommendations = _generateRecommendations(riskScore, diversificationScore, performanceScore);
        
        portfolioAnalyses[msg.sender] = PortfolioAnalysis({
            user: msg.sender,
            totalValue: totalValue,
            riskScore: riskScore,
            diversificationScore: diversificationScore,
            performanceScore: performanceScore,
            recommendations: recommendations,
            timestamp: block.timestamp
        });
        
        emit PortfolioAnalyzed(msg.sender, totalValue, riskScore, diversificationScore, block.timestamp);
    }

    /**
     * @dev Get tax optimization suggestions
     */
    function getTaxOptimizationSuggestions() external onlyBetaUser {
        require(userTier[msg.sender] >= 3, "Pro tier required");
        
        // Generate tax optimization suggestions based on user's transactions
        string memory strategy = "tax_loss_harvesting";
        uint256 potentialSavings = _calculatePotentialSavings(msg.sender);
        
        emit TaxOptimizationSuggested(msg.sender, strategy, potentialSavings, block.timestamp);
    }

    // View functions
    function getBetaKey(string calldata betaKey) external view returns (BetaKey memory) {
        return betaKeys[betaKey];
    }
    
    function getUserTransactions(address user) external view returns (Transaction[] memory) {
        return userTransactions[user];
    }
    
    function getTaxCalculation(address user, uint256 taxYear) external view returns (TaxCalculation memory) {
        return taxCalculations[user][taxYear];
    }
    
    function getUserGoals(address user) external view returns (WealthGoal[] memory) {
        return userGoals[user];
    }
    
    function getUserAdvice(address user) external view returns (InvestmentAdvice[] memory) {
        return userAdvice[user];
    }
    
    function getPortfolioAnalysis(address user) external view returns (PortfolioAnalysis memory) {
        return portfolioAnalyses[user];
    }
    
    function getTokenPrice(string calldata token) external view returns (uint256) {
        return tokenPrices[token];
    }
    
    function getTaxStrategy(string calldata strategy) external view returns (TaxOptimization memory) {
        return taxStrategies[strategy];
    }
    
    function getBetaKeyCount() external view returns (uint256) {
        return _betaKeyCounter.current();
    }
    
    function isBetaUser(address user) external view returns (bool) {
        return betaUsers[user];
    }
    
    function getUserTier(address user) external view returns (uint256) {
        return userTier[user];
    }

    // Internal functions
    function _generateRandomKey() internal view returns (string memory) {
        bytes memory chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        bytes memory key = new bytes(BETA_KEY_LENGTH);
        
        for (uint256 i = 0; i < BETA_KEY_LENGTH; i++) {
            key[i] = chars[uint256(keccak256(abi.encodePacked(block.timestamp, i))) % chars.length];
        }
        
        return string(key);
    }
    
    function _calculateTaxOwed(uint256 netGains) internal pure returns (uint256) {
        // Simplified tax calculation - in production, use actual tax brackets
        if (netGains <= 10000) {
            return (netGains * 1000) / 10000; // 10%
        } else if (netGains <= 50000) {
            return 1000 + ((netGains - 10000) * 1500) / 10000; // 15%
        } else {
            return 7000 + ((netGains - 50000) * 2000) / 10000; // 20%
        }
    }
    
    function _calculateAdviceConfidence(
        string memory adviceType,
        string memory asset,
        uint256 amount
    ) internal pure returns (uint256) {
        // Simplified confidence calculation
        uint256 baseConfidence = 70;
        
        if (keccak256(bytes(adviceType)) == keccak256(bytes("buy"))) {
            baseConfidence += 10;
        } else if (keccak256(bytes(adviceType)) == keccak256(bytes("sell"))) {
            baseConfidence += 5;
        }
        
        if (amount > 10000) {
            baseConfidence += 5;
        }
        
        return baseConfidence > 100 ? 100 : baseConfidence;
    }
    
    function _calculateRiskScore(Transaction[] memory transactions) internal pure returns (uint256) {
        // Simplified risk calculation based on transaction patterns
        uint256 riskScore = 50; // Base risk score
        
        for (uint256 i = 0; i < transactions.length; i++) {
            if (keccak256(bytes(transactions[i].transactionType)) == keccak256(bytes("sell"))) {
                riskScore += 5;
            }
        }
        
        return riskScore > 100 ? 100 : riskScore;
    }
    
    function _calculateDiversificationScore(Transaction[] memory transactions) internal pure returns (uint256) {
        // Simplified diversification calculation
        uint256 uniqueTokens = 0;
        mapping(address => bool) seenTokens;
        
        for (uint256 i = 0; i < transactions.length; i++) {
            if (!seenTokens[transactions[i].token]) {
                seenTokens[transactions[i].token] = true;
                uniqueTokens++;
            }
        }
        
        return uniqueTokens * 20; // Max 100 for 5+ tokens
    }
    
    function _calculatePerformanceScore(Transaction[] memory transactions) internal pure returns (uint256) {
        // Simplified performance calculation
        uint256 totalGains = 0;
        uint256 totalLosses = 0;
        
        for (uint256 i = 0; i < transactions.length; i++) {
            if (keccak256(bytes(transactions[i].transactionType)) == keccak256(bytes("sell"))) {
                // Mock performance calculation
                totalGains += transactions[i].amount * 10; // Simplified
            }
        }
        
        if (totalGains > totalLosses) {
            return 80; // Good performance
        } else {
            return 40; // Poor performance
        }
    }
    
    function _generateRecommendations(
        uint256 riskScore,
        uint256 diversificationScore,
        uint256 performanceScore
    ) internal pure returns (string[] memory) {
        string[] memory recommendations = new string[](3);
        
        if (riskScore > 70) {
            recommendations[0] = "Consider reducing portfolio risk";
        } else {
            recommendations[0] = "Portfolio risk is acceptable";
        }
        
        if (diversificationScore < 60) {
            recommendations[1] = "Increase portfolio diversification";
        } else {
            recommendations[1] = "Good diversification";
        }
        
        if (performanceScore < 60) {
            recommendations[2] = "Review investment strategy";
        } else {
            recommendations[2] = "Strong performance";
        }
        
        return recommendations;
    }
    
    function _calculatePotentialSavings(address user) internal view returns (uint256) {
        // Simplified savings calculation
        return 1000; // Mock 1000 XRP potential savings
    }
    
    function _initializeTaxStrategies() internal {
        taxStrategies["tax_loss_harvesting"] = TaxOptimization({
            strategy: "tax_loss_harvesting",
            description: "Sell losing positions to offset gains",
            potentialSavings: 5000,
            riskLevel: 2,
            applicable: true
        });
        
        taxStrategies["long_term_holding"] = TaxOptimization({
            strategy: "long_term_holding",
            description: "Hold assets for over 1 year for lower tax rates",
            potentialSavings: 3000,
            riskLevel: 1,
            applicable: true
        });
        
        taxStrategies["charitable_donations"] = TaxOptimization({
            strategy: "charitable_donations",
            description: "Donate appreciated assets to charity",
            potentialSavings: 2000,
            riskLevel: 1,
            applicable: true
        });
    }
    
    function _initializeTokenPrices() internal {
        tokenPrices["XRP"] = 1000000; // 1 XRP = 1,000,000 drops
        tokenPrices["BTC"] = 50000000000; // Mock BTC price
        tokenPrices["ETH"] = 3000000000; // Mock ETH price
        tokenPrices["USDC"] = 1000000; // 1 USDC = 1,000,000 (6 decimals)
        tokenPrices["USDT"] = 1000000; // 1 USDT = 1,000,000 (6 decimals)
    }

    // Admin functions
    function updateTokenPrice(string calldata token, uint256 price) external onlyOwner {
        tokenPrices[token] = price;
    }
    
    function updateFees(
        uint256 newBasicFee,
        uint256 newPremiumFee,
        uint256 newProFee,
        uint256 newTaxCalculationFee,
        uint256 newPortfolioAnalysisFee
    ) external onlyOwner {
        basicFee = newBasicFee;
        premiumFee = newPremiumFee;
        proFee = newProFee;
        taxCalculationFee = newTaxCalculationFee;
        portfolioAnalysisFee = newPortfolioAnalysisFee;
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
}
