# XRPL Staking Service

An automated XRPL validator staking service that allows users to stake XRP with validators and earn rewards while providing passive income through platform fees.

## Features

- **Automated Staking**: Stake XRP with trusted validators
- **Reward Distribution**: Automatic reward calculation and distribution
- **Validator Performance**: Track validator uptime and performance metrics
- **Flexible Lock Periods**: Choose from 7 days to 1 year lock periods
- **Platform Fees**: Earn 1% fee on all staking transactions
- **Security**: Built with OpenZeppelin security standards

## Revenue Model

- **Platform Fees**: 1% fee on all staking transactions
- **Validator Partnerships**: Revenue sharing with validators
- **Performance Bonuses**: Additional fees for high-performing validators

## Installation

```bash
npm install
```

## Deployment

```bash
# Compile contracts
npm run compile

# Deploy to XRPL network
npm run deploy

# Verify contracts
npm run verify
```

## Usage

### Staking XRP

```javascript
// Stake XRP in a validator pool
await stakingService.stake(
    poolId,                    // Pool ID
    ethers.utils.parseEther("1000") // 1000 XRP
);
```

### Claiming Rewards

```javascript
// Claim staking rewards
await stakingService.claimRewards(poolId);
```

### Unstaking

```javascript
// Unstake after lock period
await stakingService.unstake(poolId);
```

## Smart Contract Functions

### Core Functions
- `stake()` - Stake XRP in a validator pool
- `unstake()` - Unstake XRP after lock period
- `claimRewards()` - Claim accumulated rewards
- `createStakingPool()` - Create new validator pool (owner only)

### View Functions
- `getUserStakeInfo()` - Get user's staking information
- `getUserPools()` - Get user's active pools
- `getPoolInfo()` - Get pool information
- `calculatePendingRewards()` - Calculate pending rewards

### Administrative Functions
- `authorizeValidator()` - Authorize new validator
- `updatePoolRewardRate()` - Update pool reward rate
- `addValidatorRewards()` - Add validator rewards to pool

## Validator Management

### Adding Validators

```javascript
// Authorize a new validator
await stakingService.authorizeValidator(validatorAddress);

// Create staking pool for validator
await stakingService.createStakingPool(
    validatorAddress,
    "Validator Name",
    1000, // 10% APR
    ethers.utils.parseEther("100"), // Min stake
    ethers.utils.parseEther("10000"), // Max stake
    30 * 24 * 60 * 60 // 30 days lock
);
```

### Performance Tracking

```javascript
// Update validator performance
await stakingService.updateValidatorPerformance(
    validatorAddress,
    99, // 99% uptime
    0   // No slashing events
);
```

## Reward Calculation

Rewards are calculated based on:
- Staked amount
- Annual percentage rate (APR)
- Time staked
- Validator performance

Formula: `Reward = (Staked Amount × APR × Time Staked) / 365 days`

## Security Features

- Reentrancy protection
- Pausable functionality
- Owner-only administrative functions
- Emergency withdrawal capabilities
- Lock period enforcement

## Network Configuration

The service is designed to work with XRPL and supports:
- XRP as the primary staking token
- Multiple validator pools
- Cross-chain compatibility
- Real-time performance monitoring

## License

MIT
