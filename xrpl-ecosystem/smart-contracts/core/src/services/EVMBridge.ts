import { ethers, Contract, Wallet } from 'ethers';
import { EventEmitter } from 'events';

export interface EVMConfig {
  rpcUrl: string;
  chainId: number;
  bridgeContractAddress: string;
  xrpTokenAddress: string;
  validatorPrivateKey: string;
}

export interface EVMTransaction {
  hash: string;
  from: string;
  to: string;
  value: string;
  gasUsed: string;
  gasPrice: string;
  timestamp: number;
  blockNumber: number;
}

export class EVMBridge extends EventEmitter {
  private provider: ethers.JsonRpcProvider;
  private wallet: Wallet;
  private bridgeContract: Contract;
  private xrpTokenContract: Contract;
  private config: EVMConfig;
  private isConnectedFlag: boolean = false;

  // Contract ABIs (simplified)
  private bridgeABI = [
    "function deposit(uint256 amount, string memory xrplAddress) external",
    "function withdraw(address user, uint256 amount, string memory xrplTxHash) external",
    "function addValidator(address validator) external",
    "function removeValidator(address validator) external",
    "function getTransaction(uint256 txId) external view returns (tuple(address user, uint256 amount, string xrplAddress, uint256 nonce, bool executed, uint256 timestamp))",
    "function isXrplTxProcessed(string memory xrplTxHash) external view returns (bool)",
    "event Deposit(address indexed user, uint256 amount, string xrplAddress, uint256 nonce)",
    "event Withdrawal(address indexed user, uint256 amount, string xrplAddress, uint256 nonce)"
  ];

  private tokenABI = [
    "function transfer(address to, uint256 amount) external returns (bool)",
    "function transferFrom(address from, address to, uint256 amount) external returns (bool)",
    "function balanceOf(address account) external view returns (uint256)",
    "function mint(address to, uint256 amount) external",
    "function burn(address from, uint256 amount) external"
  ];

  constructor() {
    super();
    this.config = {
      rpcUrl: process.env.EVM_RPC_URL || 'http://localhost:8545',
      chainId: parseInt(process.env.EVM_CHAIN_ID || '1337'),
      bridgeContractAddress: process.env.BRIDGE_CONTRACT_ADDRESS || '',
      xrpTokenAddress: process.env.XRP_TOKEN_ADDRESS || '',
      validatorPrivateKey: process.env.VALIDATOR_PRIVATE_KEY || ''
    };
  }

  public async initialize(): Promise<void> {
    try {
      // Initialize provider and wallet
      this.provider = new ethers.JsonRpcProvider(this.config.rpcUrl);
      this.wallet = new ethers.Wallet(this.config.validatorPrivateKey, this.provider);
      
      // Initialize contracts
      this.bridgeContract = new ethers.Contract(
        this.config.bridgeContractAddress,
        this.bridgeABI,
        this.wallet
      );
      
      this.xrpTokenContract = new ethers.Contract(
        this.config.xrpTokenAddress,
        this.tokenABI,
        this.wallet
      );

      // Test connection
      const network = await this.provider.getNetwork();
      if (network.chainId !== BigInt(this.config.chainId)) {
        throw new Error(`Chain ID mismatch. Expected ${this.config.chainId}, got ${network.chainId}`);
      }

      this.isConnectedFlag = true;
      console.log(`✅ Connected to EVM sidechain (Chain ID: ${this.config.chainId})`);
      
      // Start monitoring for bridge events
      this.startEventMonitoring();
      
      this.emit('connected');
    } catch (error) {
      console.error('Failed to connect to EVM sidechain:', error);
      throw error;
    }
  }

  public async disconnect(): Promise<void> {
    try {
      this.isConnectedFlag = false;
      console.log('🔌 Disconnected from EVM sidechain');
      this.emit('disconnected');
    } catch (error) {
      console.error('Error disconnecting from EVM sidechain:', error);
    }
  }

  public isConnected(): boolean {
    return this.isConnectedFlag;
  }

  public async getBalance(address: string): Promise<string> {
    try {
      if (!this.isConnectedFlag) {
        throw new Error('Not connected to EVM sidechain');
      }

      const balance = await this.xrpTokenContract.balanceOf(address);
      return ethers.formatEther(balance);
    } catch (error) {
      console.error('Failed to get balance:', error);
      throw error;
    }
  }

  public async deposit(
    userAddress: string,
    amount: string,
    xrplAddress: string
  ): Promise<string> {
    try {
      if (!this.isConnectedFlag) {
        throw new Error('Not connected to EVM sidechain');
      }

      const amountWei = ethers.parseEther(amount);
      
      // First, approve the bridge contract to spend tokens
      const approveTx = await this.xrpTokenContract.transferFrom(
        userAddress,
        this.config.bridgeContractAddress,
        amountWei
      );
      await approveTx.wait();

      // Then call deposit on the bridge contract
      const depositTx = await this.bridgeContract.deposit(amountWei, xrplAddress);
      const receipt = await depositTx.wait();

      return receipt.hash;
    } catch (error) {
      console.error('Failed to deposit:', error);
      throw error;
    }
  }

  public async withdraw(
    userAddress: string,
    amount: string,
    xrplTxHash: string
  ): Promise<string> {
    try {
      if (!this.isConnectedFlag) {
        throw new Error('Not connected to EVM sidechain');
      }

      const amountWei = ethers.parseEther(amount);
      
      const tx = await this.bridgeContract.withdraw(userAddress, amountWei, xrplTxHash);
      const receipt = await tx.wait();

      return receipt.hash;
    } catch (error) {
      console.error('Failed to withdraw:', error);
      throw error;
    }
  }

  public async mintTokens(toAddress: string, amount: string): Promise<string> {
    try {
      if (!this.isConnectedFlag) {
        throw new Error('Not connected to EVM sidechain');
      }

      const amountWei = ethers.parseEther(amount);
      
      const tx = await this.xrpTokenContract.mint(toAddress, amountWei);
      const receipt = await tx.wait();

      return receipt.hash;
    } catch (error) {
      console.error('Failed to mint tokens:', error);
      throw error;
    }
  }

  public async burnTokens(fromAddress: string, amount: string): Promise<string> {
    try {
      if (!this.isConnectedFlag) {
        throw new Error('Not connected to EVM sidechain');
      }

      const amountWei = ethers.parseEther(amount);
      
      const tx = await this.xrpTokenContract.burn(fromAddress, amountWei);
      const receipt = await tx.wait();

      return receipt.hash;
    } catch (error) {
      console.error('Failed to burn tokens:', error);
      throw error;
    }
  }

  public async getTransactionDetails(txHash: string): Promise<EVMTransaction> {
    try {
      if (!this.isConnectedFlag) {
        throw new Error('Not connected to EVM sidechain');
      }

      const tx = await this.provider.getTransaction(txHash);
      const receipt = await this.provider.getTransactionReceipt(txHash);
      const block = await this.provider.getBlock(receipt!.blockNumber);

      return {
        hash: tx!.hash,
        from: tx!.from,
        to: tx!.to || '',
        value: ethers.formatEther(tx!.value),
        gasUsed: receipt!.gasUsed.toString(),
        gasPrice: tx!.gasPrice?.toString() || '0',
        timestamp: block!.timestamp,
        blockNumber: receipt!.blockNumber
      };
    } catch (error) {
      console.error('Failed to get transaction details:', error);
      throw error;
    }
  }

  public async isXrplTxProcessed(xrplTxHash: string): Promise<boolean> {
    try {
      if (!this.isConnectedFlag) {
        return false;
      }

      return await this.bridgeContract.isXrplTxProcessed(xrplTxHash);
    } catch (error) {
      console.error('Failed to check XRPL transaction status:', error);
      return false;
    }
  }

  public async getBridgeTransaction(txId: number): Promise<any> {
    try {
      if (!this.isConnectedFlag) {
        throw new Error('Not connected to EVM sidechain');
      }

      return await this.bridgeContract.getTransaction(txId);
    } catch (error) {
      console.error('Failed to get bridge transaction:', error);
      throw error;
    }
  }

  private startEventMonitoring(): void {
    try {
      // Monitor deposit events
      this.bridgeContract.on('Deposit', (user, amount, xrplAddress, nonce, event) => {
        this.emit('deposit', {
          user,
          amount: ethers.formatEther(amount),
          xrplAddress,
          nonce: nonce.toString(),
          txHash: event.transactionHash,
          blockNumber: event.blockNumber
        });
      });

      // Monitor withdrawal events
      this.bridgeContract.on('Withdrawal', (user, amount, xrplAddress, nonce, event) => {
        this.emit('withdrawal', {
          user,
          amount: ethers.formatEther(amount),
          xrplAddress,
          nonce: nonce.toString(),
          txHash: event.transactionHash,
          blockNumber: event.blockNumber
        });
      });

      console.log('📡 Started monitoring bridge events');
    } catch (error) {
      console.error('Failed to start event monitoring:', error);
    }
  }

  public async getNetworkInfo(): Promise<any> {
    try {
      if (!this.isConnectedFlag) {
        throw new Error('Not connected to EVM sidechain');
      }

      const network = await this.provider.getNetwork();
      const blockNumber = await this.provider.getBlockNumber();
      const gasPrice = await this.provider.getFeeData();

      return {
        chainId: network.chainId.toString(),
        name: network.name,
        blockNumber,
        gasPrice: gasPrice.gasPrice?.toString() || '0'
      };
    } catch (error) {
      console.error('Failed to get network info:', error);
      throw error;
    }
  }

  public getConfig(): EVMConfig {
    return { ...this.config };
  }

  public getWallet(): Wallet {
    return this.wallet;
  }

  public getProvider(): ethers.JsonRpcProvider {
    return this.provider;
  }
}
