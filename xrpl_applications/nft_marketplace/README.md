# XRPL NFT Marketplace

A comprehensive NFT marketplace built on XRPL that enables users to buy, sell, and auction NFTs while generating passive income through trading fees and royalties.

## Features

- **NFT Trading**: Buy and sell NFTs with fixed prices
- **Auction System**: English auctions with reserve prices
- **Offer System**: Make offers on NFTs
- **Collection Management**: Register and manage NFT collections
- **Royalty System**: Automatic royalty distribution to creators
- **Multi-Token Support**: Accept XRP, USDC, USDT, and other tokens
- **Verification System**: Verified collections and creators

## Revenue Model

- **Platform Fees**: 2.5% fee on all transactions
- **Collection Registration**: Fees for registering collections
- **Premium Features**: Additional fees for advanced features
- **Volume Bonuses**: Reduced fees for high-volume traders

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

### Listing an NFT

```javascript
// List NFT for sale
await nftMarketplace.listNFT(
    nftContractAddress,  // NFT contract address
    tokenId,            // Token ID
    paymentTokenAddress, // Payment token (XRP, USDC, etc.)
    ethers.utils.parseEther("100") // Price
);
```

### Starting an Auction

```javascript
// Start auction
await nftMarketplace.startAuction(
    nftContractAddress,
    tokenId,
    paymentTokenAddress,
    ethers.utils.parseEther("50"), // Reserve price
    7 * 24 * 60 * 60 // 7 days duration
);
```

### Placing a Bid

```javascript
// Place bid on auction
await nftMarketplace.placeBid(
    listingId,
    ethers.utils.parseEther("75") // Bid amount
);
```

### Making an Offer

```javascript
// Make offer on NFT
await nftMarketplace.makeOffer(
    nftContractAddress,
    tokenId,
    paymentTokenAddress,
    ethers.utils.parseEther("80"), // Offer amount
    Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60 // 7 days expiration
);
```

## Smart Contract Functions

### Core Functions
- `listNFT()` - List NFT for sale
- `startAuction()` - Start auction for NFT
- `buyNFT()` - Buy listed NFT
- `placeBid()` - Place bid on auction
- `endAuction()` - End auction
- `makeOffer()` - Make offer on NFT
- `acceptOffer()` - Accept an offer

### View Functions
- `getListing()` - Get listing details
- `getOffer()` - Get offer details
- `getCollection()` - Get collection information
- `getUserListings()` - Get user's listings
- `getUserOffers()` - Get user's offers

### Administrative Functions
- `registerCollection()` - Register NFT collection
- `authorizeNFT()` - Authorize NFT contract
- `authorizeToken()` - Authorize payment token
- `setFeeCollector()` - Set fee collector address

## Fee Structure

### Platform Fees
- **Trading Fee**: 2.5% on all transactions
- **Auction Fee**: 2.5% on auction sales
- **Offer Fee**: 2.5% on offer acceptance

### Royalty Fees
- **Maximum Royalty**: 10%
- **Default Royalty**: 2.5% - 7.5%
- **Creator Royalty**: Automatic distribution

## Collection Management

### Registering a Collection

```javascript
// Register new collection
await nftMarketplace.registerCollection(
    nftContractAddress,
    "Collection Name",
    "SYMBOL",
    500 // 5% royalty fee
);
```

### Collection Features
- **Creator Royalties**: Automatic royalty distribution
- **Verification**: Verified collections get priority
- **Statistics**: Volume and sales tracking
- **Metadata**: Collection name, symbol, and description

## Auction System

### Auction Types
- **English Auctions**: Ascending price auctions
- **Reserve Price**: Minimum price for auction
- **Duration**: 1 hour to 7 days
- **Automatic Ending**: Auctions end automatically

### Bidding Process
1. **Place Bid**: Users place bids above current highest
2. **Bid Refund**: Previous highest bidder gets refunded
3. **Auction End**: Highest bidder wins the NFT
4. **Fund Distribution**: Automatic fund distribution

## Offer System

### Making Offers
- **Expiration Time**: Offers expire after set time
- **Multiple Offers**: Multiple offers can be made
- **Offer Acceptance**: NFT owner can accept any offer
- **Automatic Refund**: Expired offers are automatically refunded

## Security Features

- **Reentrancy Protection**: Prevents reentrancy attacks
- **Pausable**: Emergency pause functionality
- **Access Control**: Owner-only administrative functions
- **NFT Safety**: Safe transfer of NFTs
- **Fund Security**: Secure fund distribution

## Integration Examples

### Web3 Frontend Integration

```javascript
// Connect to marketplace
const marketplace = new ethers.Contract(
    marketplaceAddress,
    marketplaceABI,
    signer
);

// List NFT
const tx = await marketplace.listNFT(
    nftContract,
    tokenId,
    paymentToken,
    price
);
await tx.wait();
```

### Mobile App Integration

```javascript
// Mobile NFT listing
const listNFT = async (nftContract, tokenId, price) => {
    const tx = await marketplace.listNFT(
        nftContract,
        tokenId,
        paymentToken,
        price
    );
    return tx.hash;
};
```

## API Endpoints

### NFT Endpoints
- `POST /api/nfts/list` - List NFT for sale
- `POST /api/nfts/auction` - Start auction
- `POST /api/nfts/buy` - Buy NFT
- `POST /api/nfts/bid` - Place bid
- `GET /api/nfts/:id` - Get NFT details

### Collection Endpoints
- `POST /api/collections/register` - Register collection
- `GET /api/collections/:address` - Get collection info
- `GET /api/collections` - List all collections

### User Endpoints
- `GET /api/users/:address/listings` - Get user listings
- `GET /api/users/:address/offers` - Get user offers
- `GET /api/users/:address/sales` - Get user sales

## Network Configuration

The marketplace supports:
- XRPL mainnet and testnet
- Multiple NFT standards
- Cross-chain compatibility
- IPFS metadata storage

## License

MIT
