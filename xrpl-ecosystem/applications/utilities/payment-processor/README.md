# XRPL Payment Processor

A comprehensive merchant payment gateway for XRPL that enables businesses to accept XRP and other token payments while generating passive income through transaction fees.

## Features

- **Merchant Registration**: Easy merchant onboarding with customizable fee rates
- **Multi-Token Support**: Accept XRP, USDC, USDT, and other authorized tokens
- **Secure Payments**: Cryptographic payment hashing and validation
- **Refund System**: Built-in refund processing for merchants
- **Fee Management**: Configurable fee rates for different merchants
- **Real-time Processing**: Instant payment confirmation and settlement

## Revenue Model

- **Platform Fees**: 0.25% fee on all transactions
- **Merchant Fees**: 0.1% - 5% fee rates (configurable per merchant)
- **Volume Bonuses**: Reduced fees for high-volume merchants
- **Premium Features**: Additional fees for advanced merchant features

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

### Merchant Registration

```javascript
// Register as a merchant
await paymentProcessor.registerMerchant(
    "My Store",           // Business name
    "Description",        // Business description
    150                  // 1.5% fee rate
);
```

### Processing Payments

```javascript
// Customer initiates payment
const paymentId = await paymentProcessor.initiatePayment(
    merchantAddress,     // Merchant address
    tokenAddress,        // Payment token
    ethers.utils.parseEther("100"), // Amount
    "ORDER-123"         // Order ID
);

// Merchant confirms payment
await paymentProcessor.completePayment(paymentId);
```

### Processing Refunds

```javascript
// Process a refund
await paymentProcessor.processRefund(
    paymentId,
    ethers.utils.parseEther("50"), // Refund amount
    "Customer requested refund"    // Reason
);
```

## Smart Contract Functions

### Core Functions
- `registerMerchant()` - Register as a merchant
- `initiatePayment()` - Initiate a payment
- `completePayment()` - Complete a payment
- `processRefund()` - Process a refund
- `cancelPayment()` - Cancel a pending payment

### View Functions
- `getPayment()` - Get payment details
- `getMerchant()` - Get merchant information
- `getMerchantPayments()` - Get merchant's payments
- `getCustomerPayments()` - Get customer's payments
- `getPlatformStats()` - Get platform statistics

### Administrative Functions
- `authorizeToken()` - Authorize payment tokens
- `updateMerchantFeeRate()` - Update merchant fee rate
- `deactivateMerchant()` - Deactivate a merchant

## Fee Structure

### Platform Fees
- **Base Fee**: 0.25% on all transactions
- **Minimum Payment**: 1000 wei
- **Maximum Merchant Fee**: 5%

### Merchant Fees
- **Minimum**: 0.1%
- **Maximum**: 5%
- **Default**: 1-2% (recommended)

## Security Features

- **Payment Hashing**: Cryptographic payment validation
- **Reentrancy Protection**: Prevents reentrancy attacks
- **Pausable**: Emergency pause functionality
- **Access Control**: Owner-only administrative functions
- **Emergency Withdraw**: Emergency fund recovery

## Integration Examples

### Web Store Integration

```javascript
// Frontend payment initiation
const handlePayment = async (orderId, amount) => {
    const tx = await paymentProcessor.initiatePayment(
        merchantAddress,
        xrpTokenAddress,
        amount,
        orderId
    );
    await tx.wait();
    return tx.hash;
};
```

### Mobile App Integration

```javascript
// Mobile payment processing
const processMobilePayment = async (amount, customerAddress) => {
    const paymentId = await paymentProcessor.initiatePayment(
        merchantAddress,
        tokenAddress,
        amount,
        `MOBILE-${Date.now()}`
    );
    return paymentId;
};
```

## API Endpoints

### Payment Endpoints
- `POST /api/payments/initiate` - Initiate payment
- `POST /api/payments/complete` - Complete payment
- `POST /api/payments/refund` - Process refund
- `GET /api/payments/:id` - Get payment details

### Merchant Endpoints
- `POST /api/merchants/register` - Register merchant
- `GET /api/merchants/:address` - Get merchant info
- `PUT /api/merchants/fee-rate` - Update fee rate

## Network Configuration

The processor supports:
- XRPL mainnet and testnet
- Multiple token standards
- Cross-chain compatibility
- Real-time price feeds

## License

MIT
