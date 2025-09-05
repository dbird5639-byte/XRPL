#!/usr/bin/env node

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { XRPLSidechain } from './services/XRPLSidechain';
import { EVMBridge } from './services/EVMBridge';
import { ValidatorService } from './services/ValidatorService';
import { routes } from './routes';

// Load environment variables
dotenv.config();

class XRPLSidechainApp {
  private app: express.Application;
  private xrplSidechain: XRPLSidechain;
  private evmBridge: EVMBridge;
  private validatorService: ValidatorService;
  private port: number;

  constructor() {
    this.app = express();
    this.port = parseInt(process.env.PORT || '3000');
    
    // Initialize services
    this.xrplSidechain = new XRPLSidechain();
    this.evmBridge = new EVMBridge();
    this.validatorService = new ValidatorService();
    
    this.setupMiddleware();
    this.setupRoutes();
    this.setupErrorHandling();
  }

  private setupMiddleware(): void {
    this.app.use(cors());
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
  }

  private setupRoutes(): void {
    this.app.use('/api', routes);
    
    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: {
          xrpl: this.xrplSidechain.isConnected(),
          evm: this.evmBridge.isConnected(),
          validator: this.validatorService.isActive()
        }
      });
    });
  }

  private setupErrorHandling(): void {
    this.app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
      console.error('Error:', err);
      res.status(500).json({
        error: 'Internal server error',
        message: err.message
      });
    });
  }

  public async start(): Promise<void> {
    try {
      // Initialize services
      await this.xrplSidechain.initialize();
      await this.evmBridge.initialize();
      await this.validatorService.initialize();
      
      // Start server
      this.app.listen(this.port, () => {
        console.log(`🚀 XRPL EVM Sidechain running on port ${this.port}`);
        console.log(`📊 Health check: http://localhost:${this.port}/health`);
        console.log(`🔗 API endpoints: http://localhost:${this.port}/api`);
      });
    } catch (error) {
      console.error('Failed to start XRPL Sidechain:', error);
      process.exit(1);
    }
  }

  public async stop(): Promise<void> {
    try {
      await this.xrplSidechain.disconnect();
      await this.evmBridge.disconnect();
      await this.validatorService.stop();
      console.log('🛑 XRPL Sidechain stopped gracefully');
    } catch (error) {
      console.error('Error stopping services:', error);
    }
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Received SIGINT, shutting down gracefully...');
  if (app) {
    await app.stop();
  }
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
  if (app) {
    await app.stop();
  }
  process.exit(0);
});

// Start the application
const app = new XRPLSidechainApp();
app.start().catch((error) => {
  console.error('Failed to start application:', error);
  process.exit(1);
});

export default XRPLSidechainApp;
