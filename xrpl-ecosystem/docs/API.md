# XRPL Ecosystem API Documentation

Comprehensive API documentation for the XRPL Ecosystem platform.

## 🔗 Base URL

```
Production: https://api.xrpl-ecosystem.org
Staging: https://staging-api.xrpl-ecosystem.org
Development: http://localhost:3001
```

## 🔐 Authentication

All API requests require authentication using JWT tokens.

### Headers
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

### Getting a Token
```bash
POST /auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

## 📊 Core APIs

### XRPL Client API

#### Get Account Information
```http
GET /api/xrpl/account/{address}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "address": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
    "balance": "1000000000",
    "sequence": 12345,
    "reserve": "10000000",
    "flags": 0
  }
}
```

#### Get Account Balances
```http
GET /api/xrpl/account/{address}/balances
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "currency": "XRP",
      "value": "1000.000000",
      "issuer": null
    },
    {
      "currency": "USD",
      "value": "500.000000",
      "issuer": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH"
    }
  ]
}
```

#### Send Payment
```http
POST /api/xrpl/payment
```

**Request:**
```json
{
  "from": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
  "to": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
  "amount": "1000000",
  "currency": "XRP",
  "memo": "Payment memo"
}
```

### Trading API

#### Get Order Book
```http
GET /api/trading/orderbook/{pair}
```

**Parameters:**
- `pair`: Trading pair (e.g., "XRP/USD")

**Response:**
```json
{
  "success": true,
  "data": {
    "pair": "XRP/USD",
    "bids": [
      {
        "price": "0.50",
        "amount": "1000.00",
        "total": "500.00"
      }
    ],
    "asks": [
      {
        "price": "0.51",
        "amount": "1000.00",
        "total": "510.00"
      }
    ]
  }
}
```

#### Place Order
```http
POST /api/trading/orders
```

**Request:**
```json
{
  "pair": "XRP/USD",
  "side": "buy",
  "type": "limit",
  "amount": "1000.00",
  "price": "0.50"
}
```

#### Get User Orders
```http
GET /api/trading/orders
```

**Query Parameters:**
- `status`: Order status (open, filled, cancelled)
- `pair`: Trading pair
- `limit`: Number of results (default: 20)
- `offset`: Offset for pagination

### DeFi API

#### Get Lending Pools
```http
GET /api/defi/pools
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "pool-1",
      "asset": "XRP",
      "totalLiquidity": "1000000.00",
      "apy": 5.25,
      "utilization": 75.5
    }
  ]
}
```

#### Deposit to Pool
```http
POST /api/defi/deposit
```

**Request:**
```json
{
  "poolId": "pool-1",
  "amount": "1000.00"
}
```

#### Withdraw from Pool
```http
POST /api/defi/withdraw
```

**Request:**
```json
{
  "poolId": "pool-1",
  "amount": "500.00"
}
```

### NFT API

#### Get NFT Collection
```http
GET /api/nft/collections
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "collection-1",
      "name": "XRPL Art",
      "description": "Digital art on XRPL",
      "totalSupply": 1000,
      "floorPrice": "10.00"
    }
  ]
}
```

#### Get NFTs by Collection
```http
GET /api/nft/collections/{collectionId}/nfts
```

#### Create NFT
```http
POST /api/nft/create
```

**Request:**
```json
{
  "name": "My NFT",
  "description": "A unique digital asset",
  "image": "https://example.com/image.png",
  "metadata": {
    "attributes": [
      {
        "trait_type": "Color",
        "value": "Blue"
      }
    ]
  }
}
```

### AI API

#### Get AI Agents
```http
GET /api/ai/agents
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "agent-1",
      "name": "Trading Bot",
      "type": "trading",
      "status": "active",
      "performance": {
        "winRate": 75.5,
        "totalTrades": 100,
        "profitLoss": "250.00"
      }
    }
  ]
}
```

#### Create AI Agent
```http
POST /api/ai/agents
```

**Request:**
```json
{
  "name": "My Trading Bot",
  "type": "trading",
  "config": {
    "strategy": "momentum",
    "riskLevel": "medium",
    "maxPositionSize": "1000.00"
  }
}
```

### Bridge API

#### Get Bridge Transactions
```http
GET /api/bridge/transactions
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "bridge-1",
      "fromNetwork": "XRPL",
      "toNetwork": "Ethereum",
      "amount": "1000.00",
      "asset": "XRP",
      "status": "completed",
      "timestamp": 1640995200000
    }
  ]
}
```

#### Initiate Bridge Transaction
```http
POST /api/bridge/transfer
```

**Request:**
```json
{
  "fromNetwork": "XRPL",
  "toNetwork": "Ethereum",
  "amount": "1000.00",
  "asset": "XRP",
  "recipient": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
}
```

### Security API

#### Get Security Events
```http
GET /api/security/events
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "event-1",
      "type": "warning",
      "level": "medium",
      "message": "Unusual trading activity detected",
      "timestamp": 1640995200000,
      "resolved": false
    }
  ]
}
```

#### Add Security Rule
```http
POST /api/security/rules
```

**Request:**
```json
{
  "name": "Large Transaction Alert",
  "condition": "amount > 10000",
  "action": "alert",
  "enabled": true
}
```

## 📈 WebSocket APIs

### Real-time Price Updates
```javascript
const ws = new WebSocket('wss://api.xrpl-ecosystem.org/ws/prices');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Price update:', data);
};
```

### Order Book Updates
```javascript
const ws = new WebSocket('wss://api.xrpl-ecosystem.org/ws/orderbook/XRP-USD');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Order book update:', data);
};
```

## 🚨 Error Handling

All API responses follow a consistent error format:

```json
{
  "success": false,
  "error": "INVALID_AMOUNT",
  "message": "Amount must be greater than 0",
  "details": {
    "field": "amount",
    "value": "0"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_TOKEN` | Authentication token is invalid or expired |
| `INSUFFICIENT_BALANCE` | Account has insufficient balance |
| `INVALID_AMOUNT` | Amount is invalid or too small |
| `ORDER_NOT_FOUND` | Order with specified ID not found |
| `NETWORK_ERROR` | Network connection error |
| `RATE_LIMITED` | Too many requests, rate limited |

## 📊 Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| General API | 1000 requests | 1 hour |
| Trading API | 100 requests | 1 minute |
| WebSocket | 10 connections | per IP |

## 🔄 Pagination

List endpoints support pagination:

```http
GET /api/trading/orders?limit=20&offset=0
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

## 📝 SDKs

### JavaScript/TypeScript
```bash
npm install @xrpl-ecosystem/sdk
```

```javascript
import { XRPLClient } from '@xrpl-ecosystem/sdk';

const client = new XRPLClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.xrpl-ecosystem.org'
});

const account = await client.xrpl.getAccount('rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH');
```

### Python
```bash
pip install xrpl-ecosystem-sdk
```

```python
from xrpl_ecosystem import XRPLClient

client = XRPLClient(api_key='your-api-key')
account = client.xrpl.get_account('rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH')
```

## 🧪 Testing

Use our sandbox environment for testing:

```bash
# Sandbox API
https://sandbox-api.xrpl-ecosystem.org
```

## 📞 Support

- **Documentation**: [docs.xrpl-ecosystem.org](https://docs.xrpl-ecosystem.org)
- **Status Page**: [status.xrpl-ecosystem.org](https://status.xrpl-ecosystem.org)
- **Support**: [support@xrpl-ecosystem.org](mailto:support@xrpl-ecosystem.org)
- **Discord**: [discord.gg/xrpl-ecosystem](https://discord.gg/xrpl-ecosystem)

---

**Last Updated**: 2024-01-15
**API Version**: v1.0.0
