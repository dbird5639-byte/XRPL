// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title XRPLYieldAggregator
 * @dev Automated yield farming optimization for XRPL ecosystem
 * @author XRPL Ecosystem
 */
contract XRPLYieldAggregator is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;
    using Counters for Counters.Counter;

    struct Vault {
        uint256 id;
        string name;
        address token;
        address strategy;
        uint256 totalDeposited;
        uint256 totalRewards;
        uint256 apy; // Annual percentage yield
        uint256 feeRate; // Management fee rate
        bool active;
        uint256 lastHarvest;
        uint256 performanceFee;
    }

    struct UserPosition {
        uint256 vaultId;
        uint256 amount;
        uint256 shares;
        uint256 lastDeposit;
        uint256 lastWithdraw;
        uint256 pendingRewards;
        bool active;
    }

    struct Strategy {
        address contractAddress;
        string name;
        address[] supportedTokens;
        uint256 minDeposit;
        uint256 maxDeposit;
        bool active;
        uint256 totalValueLocked;
        uint256 performanceFee;
    }

    struct Harvest {
        uint256 vaultId;
        uint256 amount;
        uint256 timestamp;
        uint256 gasUsed;
    }

    // Events
    event VaultCreated(uint256 indexed vaultId, string name, address token, address strategy);
    event Deposit(uint256 indexed vaultId, address user, uint256 amount, uint256 shares);
    event Withdraw(uint256 indexed vaultId, address user, uint256 amount, uint256 shares);
    event Harvest(uint256 indexed vaultId, uint256 amount, uint256 gasUsed);
    event StrategyAdded(address indexed strategy, string name);
    event VaultUpdated(uint256 indexed vaultId, uint256 newApy);
    event RewardsClaimed(uint256 indexed vaultId, address user, uint256 amount);

    // State variables
    mapping(uint256 => Vault) public vaults;
    mapping(address => mapping(uint256 => UserPosition)) public userPositions;
    mapping(address => uint256[]) public userVaults;
    mapping(address => Strategy) public strategies;
    mapping(address => bool) public authorizedTokens;
    mapping(address => bool) public authorizedStrategies;
    mapping(uint256 => Harvest[]) public vaultHarvests;
    
    Counters.Counter private _vaultIdCounter;
    
    uint256 public constant MAX_FEE_RATE = 1000; // 10%
    uint256 public constant PLATFORM_FEE_RATE = 50; // 0.5%
    uint256 public constant PERFORMANCE_FEE_RATE = 200; // 2%
    uint256 public constant MIN_DEPOSIT = 1000; // Minimum deposit amount
    
    address public feeCollector;
    uint256 public totalPlatformFees;
    uint256 public totalValueLocked;

    // Modifiers
    modifier onlyAuthorizedToken(address token) {
        require(authorizedTokens[token], "Token not authorized");
        _;
    }

    modifier onlyAuthorizedStrategy(address strategy) {
        require(authorizedStrategies[strategy], "Strategy not authorized");
        _;
    }

    modifier validVault(uint256 vaultId) {
        require(vaultId > 0 && vaultId <= _vaultIdCounter.current(), "Invalid vault ID");
        require(vaults[vaultId].active, "Vault not active");
        _;
    }

    constructor(address _feeCollector) {
        feeCollector = _feeCollector;
    }

    /**
     * @dev Create a new yield vault
     */
    function createVault(
        string memory name,
        address token,
        address strategy,
        uint256 feeRate
    ) external onlyOwner onlyAuthorizedToken(token) onlyAuthorizedStrategy(strategy) returns (uint256 vaultId) {
        require(feeRate <= MAX_FEE_RATE, "Fee rate too high");
        require(bytes(name).length > 0, "Name required");

        _vaultIdCounter.increment();
        vaultId = _vaultIdCounter.current();

        vaults[vaultId] = Vault({
            id: vaultId,
            name: name,
            token: token,
            strategy: strategy,
            totalDeposited: 0,
            totalRewards: 0,
            apy: 0, // Will be updated by strategy
            feeRate: feeRate,
            active: true,
            lastHarvest: block.timestamp,
            performanceFee: PERFORMANCE_FEE_RATE
        });

        emit VaultCreated(vaultId, name, token, strategy);
    }

    /**
     * @dev Deposit tokens into a vault
     */
    function deposit(uint256 vaultId, uint256 amount) external nonReentrant validVault(vaultId) {
        require(amount >= MIN_DEPOSIT, "Amount too small");
        
        Vault storage vault = vaults[vaultId];
        UserPosition storage position = userPositions[msg.sender][vaultId];
        
        // Calculate shares based on current vault value
        uint256 shares = calculateShares(vaultId, amount);
        
        // Transfer tokens from user to contract
        IERC20(vault.token).safeTransferFrom(msg.sender, address(this), amount);
        
        // Update position
        if (position.active) {
            position.amount = position.amount.add(amount);
            position.shares = position.shares.add(shares);
        } else {
            position.vaultId = vaultId;
            position.amount = amount;
            position.shares = shares;
            position.lastDeposit = block.timestamp;
            position.active = true;
            userVaults[msg.sender].push(vaultId);
        }
        
        // Update vault
        vault.totalDeposited = vault.totalDeposited.add(amount);
        totalValueLocked = totalValueLocked.add(amount);
        
        // Deposit to strategy
        IERC20(vault.token).safeTransfer(vault.strategy, amount);
        
        emit Deposit(vaultId, msg.sender, amount, shares);
    }

    /**
     * @dev Withdraw tokens from a vault
     */
    function withdraw(uint256 vaultId, uint256 shares) external nonReentrant validVault(vaultId) {
        UserPosition storage position = userPositions[msg.sender][vaultId];
        require(position.active, "No position");
        require(shares <= position.shares, "Insufficient shares");
        
        Vault storage vault = vaults[vaultId];
        
        // Calculate withdrawal amount
        uint256 amount = calculateWithdrawalAmount(vaultId, shares);
        
        // Update position
        position.amount = position.amount.sub(amount);
        position.shares = position.shares.sub(shares);
        position.lastWithdraw = block.timestamp;
        
        if (position.shares == 0) {
            position.active = false;
        }
        
        // Update vault
        vault.totalDeposited = vault.totalDeposited.sub(amount);
        totalValueLocked = totalValueLocked.sub(amount);
        
        // Withdraw from strategy
        IERC20(vault.token).safeTransferFrom(vault.strategy, address(this), amount);
        
        // Transfer to user
        IERC20(vault.token).safeTransfer(msg.sender, amount);
        
        emit Withdraw(vaultId, msg.sender, amount, shares);
    }

    /**
     * @dev Harvest rewards from a vault
     */
    function harvest(uint256 vaultId) external nonReentrant validVault(vaultId) {
        Vault storage vault = vaults[vaultId];
        uint256 gasStart = gasleft();
        
        // Call strategy harvest function
        (bool success, bytes memory data) = vault.strategy.call(
            abi.encodeWithSignature("harvest()")
        );
        require(success, "Harvest failed");
        
        uint256 harvestedAmount = abi.decode(data, (uint256));
        uint256 gasUsed = gasStart - gasleft();
        
        if (harvestedAmount > 0) {
            // Calculate fees
            uint256 platformFee = harvestedAmount.mul(PLATFORM_FEE_RATE).div(10000);
            uint256 performanceFee = harvestedAmount.mul(vault.performanceFee).div(10000);
            uint256 netRewards = harvestedAmount.sub(platformFee).sub(performanceFee);
            
            // Update vault
            vault.totalRewards = vault.totalRewards.add(netRewards);
            vault.lastHarvest = block.timestamp;
            
            // Update platform fees
            totalPlatformFees = totalPlatformFees.add(platformFee);
            
            // Transfer fees
            IERC20(vault.token).safeTransfer(feeCollector, platformFee);
            IERC20(vault.token).safeTransfer(owner(), performanceFee);
            
            // Record harvest
            vaultHarvests[vaultId].push(Harvest({
                vaultId: vaultId,
                amount: harvestedAmount,
                timestamp: block.timestamp,
                gasUsed: gasUsed
            }));
            
            emit Harvest(vaultId, harvestedAmount, gasUsed);
        }
    }

    /**
     * @dev Claim user rewards
     */
    function claimRewards(uint256 vaultId) external nonReentrant validVault(vaultId) {
        UserPosition storage position = userPositions[msg.sender][vaultId];
        require(position.active, "No position");
        
        uint256 rewards = calculateUserRewards(vaultId, msg.sender);
        require(rewards > 0, "No rewards to claim");
        
        // Update position
        position.pendingRewards = 0;
        
        // Transfer rewards to user
        IERC20(vaults[vaultId].token).safeTransfer(msg.sender, rewards);
        
        emit RewardsClaimed(vaultId, msg.sender, rewards);
    }

    /**
     * @dev Add a new strategy
     */
    function addStrategy(
        address strategyAddress,
        string memory name,
        address[] memory supportedTokens,
        uint256 minDeposit,
        uint256 maxDeposit
    ) external onlyOwner {
        require(strategyAddress != address(0), "Invalid strategy address");
        require(bytes(name).length > 0, "Name required");
        
        strategies[strategyAddress] = Strategy({
            contractAddress: strategyAddress,
            name: name,
            supportedTokens: supportedTokens,
            minDeposit: minDeposit,
            maxDeposit: maxDeposit,
            active: true,
            totalValueLocked: 0,
            performanceFee: PERFORMANCE_FEE_RATE
        });
        
        authorizedStrategies[strategyAddress] = true;
        
        emit StrategyAdded(strategyAddress, name);
    }

    /**
     * @dev Update vault APY
     */
    function updateVaultApy(uint256 vaultId, uint256 newApy) external onlyOwner validVault(vaultId) {
        vaults[vaultId].apy = newApy;
        emit VaultUpdated(vaultId, newApy);
    }

    /**
     * @dev Calculate shares for deposit
     */
    function calculateShares(uint256 vaultId, uint256 amount) public view returns (uint256) {
        Vault memory vault = vaults[vaultId];
        if (vault.totalDeposited == 0) {
            return amount; // 1:1 ratio for first deposit
        }
        
        // Calculate shares based on current vault value
        uint256 totalValue = getVaultTotalValue(vaultId);
        return amount.mul(vault.totalDeposited).div(totalValue);
    }

    /**
     * @dev Calculate withdrawal amount for shares
     */
    function calculateWithdrawalAmount(uint256 vaultId, uint256 shares) public view returns (uint256) {
        Vault memory vault = vaults[vaultId];
        uint256 totalValue = getVaultTotalValue(vaultId);
        return shares.mul(totalValue).div(vault.totalDeposited);
    }

    /**
     * @dev Calculate user rewards
     */
    function calculateUserRewards(uint256 vaultId, address user) public view returns (uint256) {
        UserPosition memory position = userPositions[user][vaultId];
        if (!position.active || position.shares == 0) return 0;
        
        Vault memory vault = vaults[vaultId];
        uint256 totalRewards = vault.totalRewards;
        uint256 userShare = position.shares.mul(totalRewards).div(vault.totalDeposited);
        
        return userShare.sub(position.pendingRewards);
    }

    /**
     * @dev Get vault total value
     */
    function getVaultTotalValue(uint256 vaultId) public view returns (uint256) {
        Vault memory vault = vaults[vaultId];
        uint256 strategyValue = getStrategyValue(vault.strategy);
        return vault.totalDeposited.add(strategyValue);
    }

    /**
     * @dev Get strategy value
     */
    function getStrategyValue(address strategy) public view returns (uint256) {
        (bool success, bytes memory data) = strategy.staticcall(
            abi.encodeWithSignature("getTotalValue()")
        );
        if (success) {
            return abi.decode(data, (uint256));
        }
        return 0;
    }

    /**
     * @dev Get user position
     */
    function getUserPosition(uint256 vaultId, address user) external view returns (UserPosition memory) {
        return userPositions[user][vaultId];
    }

    /**
     * @dev Get user vaults
     */
    function getUserVaults(address user) external view returns (uint256[] memory) {
        return userVaults[user];
    }

    /**
     * @dev Get vault details
     */
    function getVault(uint256 vaultId) external view validVault(vaultId) returns (Vault memory) {
        return vaults[vaultId];
    }

    /**
     * @dev Get strategy details
     */
    function getStrategy(address strategy) external view returns (Strategy memory) {
        return strategies[strategy];
    }

    /**
     * @dev Get vault harvests
     */
    function getVaultHarvests(uint256 vaultId) external view returns (Harvest[] memory) {
        return vaultHarvests[vaultId];
    }

    /**
     * @dev Authorize a token
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
        uint256 totalVaults,
        uint256 totalValue,
        uint256 totalFees,
        uint256 activeUsers
    ) {
        totalVaults = _vaultIdCounter.current();
        totalValue = totalValueLocked;
        totalFees = totalPlatformFees;
        activeUsers = 0; // Would need to iterate through users in production
    }
}
