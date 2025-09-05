// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title XRPLStaking
 * @dev Automated XRPL validator staking service with reward distribution
 * @author XRPL Ecosystem
 */
contract XRPLStaking is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    struct StakingPool {
        address validator;
        string validatorName;
        uint256 totalStaked;
        uint256 rewardRate; // Annual percentage rate
        uint256 minStakeAmount;
        uint256 maxStakeAmount;
        uint256 lockPeriod; // Minimum lock period in seconds
        bool active;
        uint256 totalRewards;
        uint256 lastRewardUpdate;
    }

    struct UserStake {
        uint256 poolId;
        uint256 amount;
        uint256 startTime;
        uint256 lockEndTime;
        uint256 lastRewardClaim;
        uint256 pendingRewards;
        bool active;
    }

    struct ValidatorPerformance {
        uint256 uptime; // Percentage
        uint256 slashingEvents;
        uint256 totalRewards;
        uint256 lastUpdate;
    }

    // Events
    event PoolCreated(uint256 indexed poolId, address validator, string name, uint256 rewardRate);
    event Staked(uint256 indexed poolId, address user, uint256 amount, uint256 lockEndTime);
    event Unstaked(uint256 indexed poolId, address user, uint256 amount);
    event RewardsClaimed(uint256 indexed poolId, address user, uint256 amount);
    event ValidatorRewards(uint256 indexed poolId, uint256 amount);
    event PoolUpdated(uint256 indexed poolId, uint256 newRewardRate);

    // State variables
    mapping(uint256 => StakingPool) public stakingPools;
    mapping(address => mapping(uint256 => UserStake)) public userStakes;
    mapping(address => uint256[]) public userPoolIds;
    mapping(address => uint256) public totalUserStaked;
    mapping(address => ValidatorPerformance) public validatorPerformance;
    mapping(address => bool) public authorizedValidators;
    
    uint256 public nextPoolId = 1;
    uint256 public constant MAX_REWARD_RATE = 2000; // 20% APR max
    uint256 public constant PLATFORM_FEE_RATE = 100; // 1% platform fee
    uint256 public constant MIN_LOCK_PERIOD = 7 days;
    uint256 public constant MAX_LOCK_PERIOD = 365 days;
    
    address public feeCollector;
    uint256 public totalPlatformFees;
    uint256 public totalStakedAcrossPools;

    // Modifiers
    modifier validPool(uint256 poolId) {
        require(poolId > 0 && poolId < nextPoolId, "Invalid pool ID");
        require(stakingPools[poolId].active, "Pool not active");
        _;
    }

    modifier validStake(uint256 poolId, address user) {
        require(userStakes[user][poolId].active, "No active stake");
        _;
    }

    constructor(address _feeCollector) {
        feeCollector = _feeCollector;
    }

    /**
     * @dev Create a new staking pool for a validator
     */
    function createStakingPool(
        address validator,
        string memory validatorName,
        uint256 rewardRate,
        uint256 minStakeAmount,
        uint256 maxStakeAmount,
        uint256 lockPeriod
    ) external onlyOwner returns (uint256 poolId) {
        require(authorizedValidators[validator], "Validator not authorized");
        require(rewardRate <= MAX_REWARD_RATE, "Reward rate too high");
        require(lockPeriod >= MIN_LOCK_PERIOD && lockPeriod <= MAX_LOCK_PERIOD, "Invalid lock period");
        require(minStakeAmount > 0 && maxStakeAmount > minStakeAmount, "Invalid stake amounts");

        poolId = nextPoolId++;
        stakingPools[poolId] = StakingPool({
            validator: validator,
            validatorName: validatorName,
            totalStaked: 0,
            rewardRate: rewardRate,
            minStakeAmount: minStakeAmount,
            maxStakeAmount: maxStakeAmount,
            lockPeriod: lockPeriod,
            active: true,
            totalRewards: 0,
            lastRewardUpdate: block.timestamp
        });

        emit PoolCreated(poolId, validator, validatorName, rewardRate);
    }

    /**
     * @dev Stake XRP in a validator pool
     */
    function stake(uint256 poolId, uint256 amount) external nonReentrant validPool(poolId) {
        StakingPool storage pool = stakingPools[poolId];
        require(amount >= pool.minStakeAmount, "Amount below minimum");
        require(amount <= pool.maxStakeAmount, "Amount above maximum");
        require(!userStakes[msg.sender][poolId].active, "Already staked in this pool");

        // Calculate platform fee
        uint256 platformFee = amount.mul(PLATFORM_FEE_RATE).div(10000);
        uint256 netStakeAmount = amount.sub(platformFee);

        // Transfer XRP to contract
        IERC20(address(0)).safeTransferFrom(msg.sender, address(this), amount);
        
        // Transfer platform fee to fee collector
        IERC20(address(0)).safeTransfer(feeCollector, platformFee);

        // Create user stake
        uint256 lockEndTime = block.timestamp.add(pool.lockPeriod);
        userStakes[msg.sender][poolId] = UserStake({
            poolId: poolId,
            amount: netStakeAmount,
            startTime: block.timestamp,
            lockEndTime: lockEndTime,
            lastRewardClaim: block.timestamp,
            pendingRewards: 0,
            active: true
        });

        // Update pool and user data
        pool.totalStaked = pool.totalStaked.add(netStakeAmount);
        totalStakedAcrossPools = totalStakedAcrossPools.add(netStakeAmount);
        totalUserStaked[msg.sender] = totalUserStaked[msg.sender].add(netStakeAmount);
        userPoolIds[msg.sender].push(poolId);

        // Update platform fees
        totalPlatformFees = totalPlatformFees.add(platformFee);

        emit Staked(poolId, msg.sender, netStakeAmount, lockEndTime);
    }

    /**
     * @dev Unstake XRP from a validator pool
     */
    function unstake(uint256 poolId) external nonReentrant validPool(poolId) validStake(poolId, msg.sender) {
        UserStake storage userStake = userStakes[msg.sender][poolId];
        StakingPool storage pool = stakingPools[poolId];
        
        require(block.timestamp >= userStake.lockEndTime, "Stake still locked");

        // Calculate and claim pending rewards
        uint256 pendingRewards = calculatePendingRewards(poolId, msg.sender);
        if (pendingRewards > 0) {
            userStake.pendingRewards = pendingRewards;
            _claimRewards(poolId);
        }

        // Transfer staked amount back to user
        IERC20(address(0)).safeTransfer(msg.sender, userStake.amount);

        // Update pool and user data
        pool.totalStaked = pool.totalStaked.sub(userStake.amount);
        totalStakedAcrossPools = totalStakedAcrossPools.sub(userStake.amount);
        totalUserStaked[msg.sender] = totalUserStaked[msg.sender].sub(userStake.amount);
        
        // Deactivate user stake
        userStake.active = false;

        emit Unstaked(poolId, msg.sender, userStake.amount);
    }

    /**
     * @dev Claim staking rewards
     */
    function claimRewards(uint256 poolId) external nonReentrant validPool(poolId) validStake(poolId, msg.sender) {
        _claimRewards(poolId);
    }

    /**
     * @dev Internal function to claim rewards
     */
    function _claimRewards(uint256 poolId) internal {
        UserStake storage userStake = userStakes[msg.sender][poolId];
        uint256 pendingRewards = calculatePendingRewards(poolId, msg.sender);
        
        if (pendingRewards > 0) {
            userStake.pendingRewards = 0;
            userStake.lastRewardClaim = block.timestamp;
            
            // Transfer rewards to user
            IERC20(address(0)).safeTransfer(msg.sender, pendingRewards);
            
            // Update pool total rewards
            stakingPools[poolId].totalRewards = stakingPools[poolId].totalRewards.add(pendingRewards);
            
            emit RewardsClaimed(poolId, msg.sender, pendingRewards);
        }
    }

    /**
     * @dev Calculate pending rewards for a user
     */
    function calculatePendingRewards(uint256 poolId, address user) public view returns (uint256) {
        UserStake memory userStake = userStakes[user][poolId];
        if (!userStake.active) return 0;

        StakingPool memory pool = stakingPools[poolId];
        uint256 timeElapsed = block.timestamp.sub(userStake.lastRewardClaim);
        uint256 annualReward = userStake.amount.mul(pool.rewardRate).div(10000);
        
        return annualReward.mul(timeElapsed).div(365 days).add(userStake.pendingRewards);
    }

    /**
     * @dev Update validator performance metrics
     */
    function updateValidatorPerformance(
        address validator,
        uint256 uptime,
        uint256 slashingEvents
    ) external onlyOwner {
        validatorPerformance[validator] = ValidatorPerformance({
            uptime: uptime,
            slashingEvents: slashingEvents,
            totalRewards: validatorPerformance[validator].totalRewards,
            lastUpdate: block.timestamp
        });
    }

    /**
     * @dev Update pool reward rate
     */
    function updatePoolRewardRate(uint256 poolId, uint256 newRewardRate) external onlyOwner validPool(poolId) {
        require(newRewardRate <= MAX_REWARD_RATE, "Reward rate too high");
        stakingPools[poolId].rewardRate = newRewardRate;
        stakingPools[poolId].lastRewardUpdate = block.timestamp;
        
        emit PoolUpdated(poolId, newRewardRate);
    }

    /**
     * @dev Add validator rewards to pool
     */
    function addValidatorRewards(uint256 poolId, uint256 amount) external onlyOwner validPool(poolId) {
        require(amount > 0, "Invalid amount");
        
        // Transfer rewards to contract
        IERC20(address(0)).safeTransferFrom(msg.sender, address(this), amount);
        
        // Update pool rewards
        stakingPools[poolId].totalRewards = stakingPools[poolId].totalRewards.add(amount);
        
        emit ValidatorRewards(poolId, amount);
    }

    /**
     * @dev Get user's staking information
     */
    function getUserStakeInfo(uint256 poolId, address user) external view returns (UserStake memory) {
        return userStakes[user][poolId];
    }

    /**
     * @dev Get user's active pools
     */
    function getUserPools(address user) external view returns (uint256[] memory) {
        return userPoolIds[user];
    }

    /**
     * @dev Get pool information
     */
    function getPoolInfo(uint256 poolId) external view validPool(poolId) returns (StakingPool memory) {
        return stakingPools[poolId];
    }

    /**
     * @dev Authorize a validator
     */
    function authorizeValidator(address validator) external onlyOwner {
        authorizedValidators[validator] = true;
    }

    /**
     * @dev Deauthorize a validator
     */
    function deauthorizeValidator(address validator) external onlyOwner {
        authorizedValidators[validator] = false;
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
    function emergencyWithdraw(uint256 amount) external onlyOwner {
        IERC20(address(0)).safeTransfer(owner(), amount);
    }
}
