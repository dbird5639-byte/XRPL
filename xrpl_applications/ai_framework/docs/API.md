# XRPL AI Framework API Documentation

## Overview

The XRPL AI Framework provides a comprehensive API for interacting with AI datasets, agents, and automation tasks on the XRP Ledger ecosystem.

## Base URL

```
Production: https://api.xrpl-ai.com/v1
Testnet: https://api-testnet.xrpl-ai.com/v1
Local: http://localhost:3001/api/v1
```

## Authentication

All API requests require authentication using API keys or wallet signatures.

### API Key Authentication

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.xrpl-ai.com/v1/datasets
```

### Wallet Signature Authentication

```typescript
const signature = await wallet.signMessage(message);
const headers = {
  'Authorization': `Bearer ${signature}`,
  'X-Wallet-Address': wallet.address
};
```

## Datasets API

### Get All Datasets

```http
GET /datasets
```

**Query Parameters:**
- `category` (string): Filter by category
- `status` (string): Filter by approval status
- `minPrice` (number): Minimum price filter
- `maxPrice` (number): Maximum price filter
- `quality` (number): Minimum quality score
- `limit` (number): Number of results (default: 20)
- `offset` (number): Pagination offset

**Response:**
```json
{
  "datasets": [
    {
      "id": 1,
      "name": "Financial Market Data",
      "description": "Real-time financial market data",
      "category": "finance",
      "price": "500000000",
      "size": 1073741824,
      "qualityScore": 95,
      "status": "approved",
      "submitter": "0x1234...5678",
      "purchaseCount": 127,
      "rating": 4.8,
      "tags": ["real-time", "crypto", "stocks"],
      "createdAt": "2024-01-15T10:30:00Z",
      "approvedAt": "2024-01-16T09:15:00Z"
    }
  ],
  "total": 1247,
  "limit": 20,
  "offset": 0
}
```

### Get Dataset by ID

```http
GET /datasets/{id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Financial Market Data",
  "description": "Real-time financial market data for AI training",
  "category": "finance",
  "price": "500000000",
  "size": 1073741824,
  "qualityScore": 95,
  "status": "approved",
  "submitter": "0x1234...5678",
  "approver": "0x2345...6789",
  "purchaseCount": 127,
  "totalRevenue": "475000000",
  "rating": 4.8,
  "reviews": [
    {
      "id": 1,
      "user": "0x3456...7890",
      "rating": 5,
      "comment": "Excellent dataset quality",
      "createdAt": "2024-01-20T14:30:00Z"
    }
  ],
  "tags": ["real-time", "crypto", "stocks"],
  "metadata": {
    "format": "json",
    "schema": {...},
    "preview": "QmPreviewHash"
  },
  "createdAt": "2024-01-15T10:30:00Z",
  "approvedAt": "2024-01-16T09:15:00Z"
}
```

### Submit Dataset

```http
POST /datasets
```

**Request Body:**
```json
{
  "name": "New Dataset",
  "description": "Dataset description",
  "category": "finance",
  "price": "300000000",
  "size": 524288,
  "metadata": {
    "format": "csv",
    "schema": {...},
    "preview": "QmPreviewHash"
  },
  "tags": ["trading", "analysis"]
}
```

**Response:**
```json
{
  "datasetId": 123,
  "status": "pending",
  "message": "Dataset submitted for approval"
}
```

### Purchase Dataset

```http
POST /datasets/{id}/purchase
```

**Response:**
```json
{
  "transactionHash": "0xabc123...",
  "status": "success",
  "accessToken": "access_token_here"
}
```

## Agents API

### Get All Agents

```http
GET /agents
```

**Query Parameters:**
- `creator` (string): Filter by creator address
- `status` (string): Filter by deployment status
- `purpose` (string): Filter by purpose
- `limit` (number): Number of results
- `offset` (number): Pagination offset

**Response:**
```json
{
  "agents": [
    {
      "id": 1,
      "name": "DeFi Trading Bot",
      "description": "Automated DeFi trading strategies",
      "purpose": "Trading and yield optimization",
      "creator": "0x1234...5678",
      "status": "active",
      "datasets": [1, 2, 3],
      "usageCount": 1247,
      "revenue": "2340000000",
      "rating": 4.9,
      "createdAt": "2024-01-10T10:30:00Z",
      "deployedAt": "2024-01-12T14:20:00Z"
    }
  ],
  "total": 89,
  "limit": 20,
  "offset": 0
}
```

### Create Agent

```http
POST /agents
```

**Request Body:**
```json
{
  "name": "New AI Agent",
  "description": "Agent description",
  "purpose": "Specific purpose",
  "configuration": {
    "model": "gpt-4",
    "temperature": 0.7,
    "maxTokens": 1000
  },
  "datasets": [1, 2]
}
```

**Response:**
```json
{
  "agentId": 45,
  "status": "created",
  "deploymentFee": "200000000",
  "message": "Agent created successfully"
}
```

### Deploy Agent

```http
POST /agents/{id}/deploy
```

**Response:**
```json
{
  "transactionHash": "0xdef456...",
  "agentAddress": "0x7890...1234",
  "status": "deployed"
}
```

### Use Agent

```http
POST /agents/{id}/use
```

**Request Body:**
```json
{
  "query": "Analyze the current market conditions",
  "parameters": {
    "timeframe": "1d",
    "indicators": ["RSI", "MACD"]
  }
}
```

**Response:**
```json
{
  "result": "Market analysis results...",
  "usageId": "usage_123",
  "cost": "5000000",
  "timestamp": "2024-01-20T15:30:00Z"
}
```

## Automation API

### Get All Tasks

```http
GET /automation/tasks
```

**Query Parameters:**
- `creator` (string): Filter by creator
- `status` (string): Filter by status
- `type` (string): Filter by task type
- `limit` (number): Number of results
- `offset` (number): Pagination offset

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "name": "Daily Portfolio Rebalancing",
      "type": "defi_strategy",
      "description": "Automatically rebalance portfolio",
      "status": "completed",
      "creator": "0x1234...5678",
      "agents": [1, 2],
      "lastRun": "2024-01-20T14:30:00Z",
      "nextRun": "2024-01-21T14:30:00Z",
      "frequency": "daily",
      "successRate": 95,
      "totalRuns": 20,
      "cost": "25000000",
      "revenue": "45000000"
    }
  ],
  "total": 2156,
  "limit": 20,
  "offset": 0
}
```

### Create Task

```http
POST /automation/tasks
```

**Request Body:**
```json
{
  "name": "Market Analysis Task",
  "type": "data_analysis",
  "description": "Daily market analysis",
  "parameters": {
    "timeframe": "1d",
    "indicators": ["RSI", "MACD", "Bollinger"]
  },
  "agents": [1, 2],
  "scheduledTime": "2024-01-21T09:00:00Z",
  "isRecurring": true,
  "recurrenceInterval": 86400
}
```

**Response:**
```json
{
  "taskId": 123,
  "status": "scheduled",
  "cost": "15000000",
  "message": "Task created successfully"
}
```

### Execute Task

```http
POST /automation/tasks/{id}/execute
```

**Response:**
```json
{
  "executionId": "exec_123",
  "status": "running",
  "estimatedDuration": 300,
  "message": "Task execution started"
}
```

### Get Task Result

```http
GET /automation/tasks/{id}/result
```

**Response:**
```json
{
  "executionId": "exec_123",
  "status": "completed",
  "result": "Task execution results...",
  "duration": 245,
  "cost": "15000000",
  "revenue": "30000000",
  "timestamp": "2024-01-20T15:30:00Z"
}
```

## Templates API

### Get All Templates

```http
GET /automation/templates
```

**Response:**
```json
{
  "templates": [
    {
      "id": 1,
      "name": "DeFi Yield Optimizer",
      "description": "Automatically find best yield opportunities",
      "type": "defi_strategy",
      "creator": "0x1234...5678",
      "agents": [1],
      "cost": "30000000",
      "usageCount": 156,
      "rating": 4.5,
      "isPublic": true,
      "createdAt": "2024-01-10T10:30:00Z"
    }
  ],
  "total": 23,
  "limit": 20,
  "offset": 0
}
```

### Use Template

```http
POST /automation/templates/{id}/use
```

**Request Body:**
```json
{
  "customParameters": {
    "protocols": ["uniswap", "compound"],
    "threshold": 0.1
  },
  "scheduledTime": "2024-01-21T09:00:00Z"
}
```

**Response:**
```json
{
  "taskId": 124,
  "status": "created",
  "cost": "30000000",
  "message": "Template used successfully"
}
```

## Analytics API

### Get Platform Statistics

```http
GET /analytics/platform
```

**Response:**
```json
{
  "datasets": {
    "total": 1247,
    "approved": 1156,
    "pending": 67,
    "rejected": 24
  },
  "agents": {
    "total": 89,
    "active": 76,
    "deploying": 8,
    "inactive": 5
  },
  "tasks": {
    "total": 2156,
    "completed": 1987,
    "running": 45,
    "scheduled": 89,
    "failed": 35
  },
  "revenue": {
    "total": "45230000000",
    "platform": "4523000000",
    "creators": "40707000000"
  }
}
```

### Get User Statistics

```http
GET /analytics/user/{address}
```

**Response:**
```json
{
  "user": "0x1234...5678",
  "datasets": {
    "submitted": 5,
    "approved": 4,
    "purchased": 12,
    "revenue": "1250000000"
  },
  "agents": {
    "created": 3,
    "active": 2,
    "usage": 1247,
    "revenue": "2340000000"
  },
  "tasks": {
    "created": 15,
    "completed": 142,
    "revenue": "890000000"
  },
  "totalRevenue": "4480000000"
}
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameters",
    "details": {
      "field": "price",
      "reason": "Price must be between 100 and 1000000 XRP"
    }
  },
  "timestamp": "2024-01-20T15:30:00Z",
  "requestId": "req_123456"
}
```

### Error Codes

- `INVALID_REQUEST`: Invalid request parameters
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Rate Limiting

API requests are rate limited:

- **Free Tier**: 100 requests/hour
- **Pro Tier**: 1000 requests/hour
- **Enterprise**: 10000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642694400
```

## Webhooks

Configure webhooks to receive real-time notifications:

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["dataset.approved", "agent.deployed", "task.completed"],
  "secret": "your_webhook_secret"
}
```

**Webhook Payload:**
```json
{
  "event": "dataset.approved",
  "data": {
    "datasetId": 123,
    "name": "Financial Data",
    "approver": "0x2345...6789"
  },
  "timestamp": "2024-01-20T15:30:00Z",
  "signature": "webhook_signature"
}
```

## SDKs

Official SDKs are available for:

- **JavaScript/TypeScript**: `npm install @xrpl-ai/sdk`
- **Python**: `pip install xrpl-ai-sdk`
- **Go**: `go get github.com/xrpl-ai/sdk-go`

### JavaScript SDK Example

```typescript
import { XRPLAI } from '@xrpl-ai/sdk';

const client = new XRPLAI({
  apiKey: 'your_api_key',
  network: 'mainnet'
});

// Get datasets
const datasets = await client.datasets.list({
  category: 'finance',
  limit: 10
});

// Create agent
const agent = await client.agents.create({
  name: 'Trading Bot',
  description: 'Automated trading',
  purpose: 'Trading',
  configuration: {
    model: 'gpt-4',
    temperature: 0.7
  }
});
```

## Support

For API support:

- **Documentation**: [docs.xrpl-ai.com/api](https://docs.xrpl-ai.com/api)
- **Status Page**: [status.xrpl-ai.com](https://status.xrpl-ai.com)
- **Support Email**: api-support@xrpl-ai.com
- **Discord**: [Join our developer community](https://discord.gg/xrpl-ai)
