# XRPL Lending Platform

A peer-to-peer lending platform built on XRPL that allows users to borrow and lend digital assets using XRP as collateral.

## Features

- **Peer-to-Peer Lending**: Borrow and lend digital assets directly between users
- **XRP Collateral**: Use XRP and other supported tokens as collateral
- **Automated Liquidations**: Automatic liquidation of undercollateralized positions
- **Platform Fees**: Earn passive income through transaction fees
- **Flexible Terms**: Customizable loan terms and interest rates
- **Security**: Built with OpenZeppelin security standards

## Revenue Model

- **Platform Fees**: 0.25% fee on all loan transactions
- **Liquidation Penalties**: 10% penalty on liquidated collateral
- **Interest Spread**: Potential to earn from interest rate spreads

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

### Creating a Loan

```javascript
// Create a loan request
await lendingPlatform.createLoan(
    xrpTokenAddress,    // Collateral token (XRP)
    usdcTokenAddress,   // Loan token (USDC)
    ethers.utils.parseEther("1000"), // 1000 XRP collateral
    ethers.utils.parseUnits("500", 6), // 500 USDC loan
    1000,               // 10% APR
    30 * 24 * 60 * 60   // 30 days duration
);
```

### Funding a Loan

```javascript
// Fund an existing loan
await lendingPlatform.fundLoan(loanId);
```

### Repaying a Loan

```javascript
// Repay a loan
await lendingPlatform.repayLoan(loanId);
```

## Smart Contract Functions

### Core Functions
- `createLoan()` - Create a new loan request
- `fundLoan()` - Fund an existing loan
- `repayLoan()` - Repay a loan
- `liquidateLoan()` - Liquidate an undercollateralized loan

### View Functions
- `getLoan()` - Get loan details
- `getUserLoans()` - Get user's loans
- `calculateInterest()` - Calculate accrued interest
- `isUndercollateralized()` - Check if loan is liquidatable

## Security Features

- Reentrancy protection
- Pausable functionality
- Owner-only administrative functions
- Emergency withdrawal capabilities
- Collateral ratio validation

## Network Configuration

The platform is designed to work with XRPL EVM sidechain and supports:
- XRP as primary collateral
- Various ERC-20 tokens
- Cross-chain compatibility

## License

MIT
