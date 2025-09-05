// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title XRPLAgentToken
 * @dev Native token for the XRPL Agent Ecosystem with governance, staking, and utility features
 * @author XRPL Agent Ecosystem
 */
contract XRPLAgentToken is ERC20, ERC20Burnable, ERC20Pausable, ERC20Votes, Ownable, ReentrancyGuard {
    using SafeMath for uint256;

    // Token configuration
    uint256 public constant INITIAL_SUPPLY = 100_000_000 * 1e18; // 100 million tokens
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 1e18; // 1 billion tokens max
    uint256 public constant STAKING_REWARD_RATE = 500; // 5% annual reward rate
    uint256 public constant GOVERNANCE_THRESHOLD = 1000 * 1e18; // 1000 tokens for governance
    
    // Staking structure
    struct StakingInfo {
        uint256 amount;
        uint256 startTime;
        uint256 lastClaimTime;
        uint256 lockPeriod;
        bool isLocked;
    }

    // Events
    event TokensStaked(address indexed user, uint256 amount, uint256 lockPeriod);
    event TokensUnstaked(address indexed user, uint256 amount, uint256 reward);
    event RewardsClaimed(address indexed user, uint256 amount);
    event TokensMinted(address indexed to, uint256 amount, string reason);
    event TokensBurned(address indexed from, uint256 amount, string reason);
    event StakingRewardRateUpdated(uint256 oldRate, uint256 newRate);

    // State variables
    mapping(address => StakingInfo) public stakingInfo;
    mapping(address => bool) public authorizedMinters;
    mapping(address => bool) public authorizedBurners;
    
    uint256 public totalStaked = 0;
    uint256 public stakingRewardRate = STAKING_REWARD_RATE;
    uint256 public lastRewardUpdate = block.timestamp;
    
    // Staking pools
    uint256 public constant POOL_30_DAYS = 30 days;
    uint256 public constant POOL_90_DAYS = 90 days;
    uint256 public constant POOL_180_DAYS = 180 days;
    uint256 public constant POOL_365_DAYS = 365 days;
    
    // Pool reward multipliers
    uint256 public pool30Multiplier = 100; // 1x
    uint256 public pool90Multiplier = 150; // 1.5x
    uint256 public pool180Multiplier = 200; // 2x
    uint256 public pool365Multiplier = 300; // 3x

    // Modifiers
    modifier onlyAuthorizedMinter() {
        require(authorizedMinters[msg.sender] || msg.sender == owner(), "Not authorized minter");
        _;
    }

    modifier onlyAuthorizedBurner() {
        require(authorizedBurners[msg.sender] || msg.sender == owner(), "Not authorized burner");
        _;
    }

    modifier validStakingAmount(uint256 amount) {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        _;
    }

    constructor() ERC20("XRPL Agent Token", "XAT") ERC20Permit("XRPL Agent Token") {
        // Mint initial supply to owner
        _mint(msg.sender, INITIAL_SUPPLY);
    }

    /**
     * @dev Stake tokens for rewards
     */
    function stake(uint256 amount, uint256 lockPeriod) external nonReentrant whenNotPaused validStakingAmount(amount) {
        require(lockPeriod == POOL_30_DAYS || lockPeriod == POOL_90_DAYS || 
                lockPeriod == POOL_180_DAYS || lockPeriod == POOL_365_DAYS, "Invalid lock period");
        
        StakingInfo storage staking = stakingInfo[msg.sender];
        
        // If already staking, claim rewards first
        if (staking.amount > 0) {
            claimRewards();
        }
        
        // Transfer tokens to contract
        _transfer(msg.sender, address(this), amount);
        
        // Update staking info
        staking.amount = staking.amount.add(amount);
        staking.startTime = block.timestamp;
        staking.lastClaimTime = block.timestamp;
        staking.lockPeriod = lockPeriod;
        staking.isLocked = true;
        
        totalStaked = totalStaked.add(amount);
        
        emit TokensStaked(msg.sender, amount, lockPeriod);
    }

    /**
     * @dev Unstake tokens
     */
    function unstake() external nonReentrant whenNotPaused {
        StakingInfo storage staking = stakingInfo[msg.sender];
        
        require(staking.amount > 0, "No staked tokens");
        require(block.timestamp >= staking.startTime.add(staking.lockPeriod), "Lock period not ended");
        
        // Calculate and claim rewards
        uint256 reward = calculateRewards(msg.sender);
        uint256 totalAmount = staking.amount.add(reward);
        
        // Reset staking info
        staking.amount = 0;
        staking.startTime = 0;
        staking.lastClaimTime = 0;
        staking.lockPeriod = 0;
        staking.isLocked = false;
        
        totalStaked = totalStaked.sub(staking.amount);
        
        // Transfer tokens back to user
        _transfer(address(this), msg.sender, totalAmount);
        
        emit TokensUnstaked(msg.sender, staking.amount, reward);
    }

    /**
     * @dev Claim staking rewards
     */
    function claimRewards() public nonReentrant whenNotPaused {
        StakingInfo storage staking = stakingInfo[msg.sender];
        
        require(staking.amount > 0, "No staked tokens");
        
        uint256 reward = calculateRewards(msg.sender);
        require(reward > 0, "No rewards to claim");
        
        staking.lastClaimTime = block.timestamp;
        
        // Mint new tokens as rewards
        _mint(msg.sender, reward);
        
        emit RewardsClaimed(msg.sender, reward);
    }

    /**
     * @dev Calculate staking rewards for a user
     */
    function calculateRewards(address user) public view returns (uint256) {
        StakingInfo memory staking = stakingInfo[user];
        
        if (staking.amount == 0) return 0;
        
        uint256 timeElapsed = block.timestamp.sub(staking.lastClaimTime);
        uint256 annualReward = staking.amount.mul(stakingRewardRate).div(10000);
        uint256 reward = annualReward.mul(timeElapsed).div(365 days);
        
        // Apply pool multiplier
        uint256 multiplier = _getPoolMultiplier(staking.lockPeriod);
        reward = reward.mul(multiplier).div(100);
        
        return reward;
    }

    /**
     * @dev Get pool multiplier based on lock period
     */
    function _getPoolMultiplier(uint256 lockPeriod) internal view returns (uint256) {
        if (lockPeriod == POOL_30_DAYS) return pool30Multiplier;
        if (lockPeriod == POOL_90_DAYS) return pool90Multiplier;
        if (lockPeriod == POOL_180_DAYS) return pool180Multiplier;
        if (lockPeriod == POOL_365_DAYS) return pool365Multiplier;
        return 100; // Default 1x
    }

    /**
     * @dev Mint tokens (only authorized minters)
     */
    function mint(address to, uint256 amount, string memory reason) external onlyAuthorizedMinter {
        require(totalSupply().add(amount) <= MAX_SUPPLY, "Exceeds max supply");
        
        _mint(to, amount);
        
        emit TokensMinted(to, amount, reason);
    }

    /**
     * @dev Burn tokens (only authorized burners)
     */
    function burnFrom(address from, uint256 amount, string memory reason) external onlyAuthorizedBurner {
        _burn(from, amount);
        
        emit TokensBurned(from, amount, reason);
    }

    /**
     * @dev Emergency unstake (with penalty)
     */
    function emergencyUnstake() external nonReentrant whenNotPaused {
        StakingInfo storage staking = stakingInfo[msg.sender];
        
        require(staking.amount > 0, "No staked tokens");
        require(staking.isLocked, "Not locked");
        
        // Calculate penalty (50% of staked amount)
        uint256 penalty = staking.amount.div(2);
        uint256 returnAmount = staking.amount.sub(penalty);
        
        // Reset staking info
        staking.amount = 0;
        staking.startTime = 0;
        staking.lastClaimTime = 0;
        staking.lockPeriod = 0;
        staking.isLocked = false;
        
        totalStaked = totalStaked.sub(staking.amount);
        
        // Transfer tokens back to user (with penalty)
        _transfer(address(this), msg.sender, returnAmount);
        
        // Burn penalty tokens
        _burn(address(this), penalty);
        
        emit TokensUnstaked(msg.sender, returnAmount, 0);
    }

    /**
     * @dev Get user staking info
     */
    function getStakingInfo(address user) external view returns (StakingInfo memory) {
        return stakingInfo[user];
    }

    /**
     * @dev Check if user can participate in governance
     */
    function canParticipateInGovernance(address user) external view returns (bool) {
        return balanceOf(user) >= GOVERNANCE_THRESHOLD;
    }

    /**
     * @dev Get total voting power (including staked tokens)
     */
    function getTotalVotingPower(address user) external view returns (uint256) {
        uint256 balance = balanceOf(user);
        uint256 staked = stakingInfo[user].amount;
        
        // Staked tokens have 2x voting power
        return balance.add(staked);
    }

    /**
     * @dev Authorize minter
     */
    function authorizeMinter(address minter) external onlyOwner {
        authorizedMinters[minter] = true;
    }

    /**
     * @dev Revoke minter authorization
     */
    function revokeMinter(address minter) external onlyOwner {
        authorizedMinters[minter] = false;
    }

    /**
     * @dev Authorize burner
     */
    function authorizeBurner(address burner) external onlyOwner {
        authorizedBurners[burner] = true;
    }

    /**
     * @dev Revoke burner authorization
     */
    function revokeBurner(address burner) external onlyOwner {
        authorizedBurners[burner] = false;
    }

    /**
     * @dev Set staking reward rate
     */
    function setStakingRewardRate(uint256 newRate) external onlyOwner {
        require(newRate <= 1000, "Rate too high"); // Max 10%
        
        uint256 oldRate = stakingRewardRate;
        stakingRewardRate = newRate;
        
        emit StakingRewardRateUpdated(oldRate, newRate);
    }

    /**
     * @dev Set pool multipliers
     */
    function setPoolMultipliers(
        uint256 _pool30Multiplier,
        uint256 _pool90Multiplier,
        uint256 _pool180Multiplier,
        uint256 _pool365Multiplier
    ) external onlyOwner {
        require(_pool30Multiplier >= 100 && _pool30Multiplier <= 500, "Invalid 30-day multiplier");
        require(_pool90Multiplier >= 100 && _pool90Multiplier <= 500, "Invalid 90-day multiplier");
        require(_pool180Multiplier >= 100 && _pool180Multiplier <= 500, "Invalid 180-day multiplier");
        require(_pool365Multiplier >= 100 && _pool365Multiplier <= 500, "Invalid 365-day multiplier");
        
        pool30Multiplier = _pool30Multiplier;
        pool90Multiplier = _pool90Multiplier;
        pool180Multiplier = _pool180Multiplier;
        pool365Multiplier = _pool365Multiplier;
    }

    /**
     * @dev Pause token transfers
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause token transfers
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    // Required overrides for multiple inheritance
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Pausable) {
        super._beforeTokenTransfer(from, to, amount);
    }

    function _afterTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Votes) {
        super._afterTokenTransfer(from, to, amount);
    }

    function _mint(address to, uint256 amount) internal override(ERC20, ERC20Votes) {
        super._mint(to, amount);
    }

    function _burn(address account, uint256 amount) internal override(ERC20, ERC20Votes) {
        super._burn(account, amount);
    }
}
