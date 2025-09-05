import { ethers } from 'ethers'
import { ipfsService } from './ipfsService'

export interface Web3Config {
  rpcUrl: string
  chainId: number
  contracts: {
    xrpToken: string
    datasetMarketplace: string
    agentFactory: string
    automationEngine: string
  }
}

export interface WalletInfo {
  address: string
  balance: string
  network: string
  chainId: number
}

export interface ContractAddresses {
  XRPToken: string
  AIDatasetMarketplace: string
  AIAgentFactory: string
  AIAutomationEngine: string
}

class Web3Service {
  private provider: ethers.providers.Web3Provider | null = null
  private signer: ethers.Signer | null = null
  private config: Web3Config
  private contracts: any = {}

  constructor(config: Web3Config) {
    this.config = config
  }

  /**
   * Connect to Web3 provider (MetaMask, WalletConnect, etc.)
   */
  async connectWallet(): Promise<WalletInfo> {
    if (!window.ethereum) {
      throw new Error('No Web3 provider found. Please install MetaMask or another Web3 wallet.')
    }

    try {
      // Request account access
      await window.ethereum.request({ method: 'eth_requestAccounts' })
      
      // Create provider and signer
      this.provider = new ethers.providers.Web3Provider(window.ethereum)
      this.signer = this.provider.getSigner()
      
      // Get account info
      const address = await this.signer.getAddress()
      const balance = await this.provider.getBalance(address)
      const network = await this.provider.getNetwork()
      
      // Initialize contracts
      await this.initializeContracts()
      
      return {
        address,
        balance: ethers.utils.formatEther(balance),
        network: network.name,
        chainId: network.chainId
      }
    } catch (error) {
      console.error('Failed to connect wallet:', error)
      throw error
    }
  }

  /**
   * Disconnect wallet
   */
  disconnectWallet(): void {
    this.provider = null
    this.signer = null
    this.contracts = {}
  }

  /**
   * Check if wallet is connected
   */
  isConnected(): boolean {
    return this.signer !== null
  }

  /**
   * Get current wallet info
   */
  async getWalletInfo(): Promise<WalletInfo | null> {
    if (!this.signer || !this.provider) {
      return null
    }

    try {
      const address = await this.signer.getAddress()
      const balance = await this.provider.getBalance(address)
      const network = await this.provider.getNetwork()
      
      return {
        address,
        balance: ethers.utils.formatEther(balance),
        network: network.name,
        chainId: network.chainId
      }
    } catch (error) {
      console.error('Failed to get wallet info:', error)
      return null
    }
  }

  /**
   * Switch to correct network
   */
  async switchNetwork(): Promise<void> {
    if (!window.ethereum) {
      throw new Error('No Web3 provider found')
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${this.config.chainId.toString(16)}` }]
      })
    } catch (error: any) {
      // If network doesn't exist, add it
      if (error.code === 4902) {
        await this.addNetwork()
      } else {
        throw error
      }
    }
  }

  /**
   * Add network to wallet
   */
  private async addNetwork(): Promise<void> {
    if (!window.ethereum) {
      throw new Error('No Web3 provider found')
    }

    const networkConfig = {
      chainId: `0x${this.config.chainId.toString(16)}`,
      chainName: 'XRPL Sidechain',
      rpcUrls: [this.config.rpcUrl],
      nativeCurrency: {
        name: 'XRP',
        symbol: 'XRP',
        decimals: 6
      },
      blockExplorerUrls: ['https://explorer.xrpl-sidechain.com']
    }

    await window.ethereum.request({
      method: 'wallet_addEthereumChain',
      params: [networkConfig]
    })
  }

  /**
   * Initialize contract instances
   */
  private async initializeContracts(): Promise<void> {
    if (!this.signer) {
      throw new Error('Wallet not connected')
    }

    try {
      // Import contract ABIs (in real implementation, these would be imported from artifacts)
      const contractABIs = await this.getContractABIs()
      
      // Initialize contracts
      this.contracts.xrpToken = new ethers.Contract(
        this.config.contracts.xrpToken,
        contractABIs.XRPToken,
        this.signer
      )
      
      this.contracts.datasetMarketplace = new ethers.Contract(
        this.config.contracts.datasetMarketplace,
        contractABIs.AIDatasetMarketplace,
        this.signer
      )
      
      this.contracts.agentFactory = new ethers.Contract(
        this.config.contracts.agentFactory,
        contractABIs.AIAgentFactory,
        this.signer
      )
      
      this.contracts.automationEngine = new ethers.Contract(
        this.config.contracts.automationEngine,
        contractABIs.AIAutomationEngine,
        this.signer
      )
    } catch (error) {
      console.error('Failed to initialize contracts:', error)
      throw error
    }
  }

  /**
   * Get contract ABIs (placeholder - in real implementation, import from artifacts)
   */
  private async getContractABIs(): Promise<any> {
    // In a real implementation, these would be imported from compiled artifacts
    return {
      XRPToken: [], // ABI would be imported here
      AIDatasetMarketplace: [],
      AIAgentFactory: [],
      AIAutomationEngine: []
    }
  }

  /**
   * Dataset Marketplace Functions
   */
  async submitDataset(
    name: string,
    description: string,
    category: string,
    price: string,
    size: number,
    metadata: any
  ): Promise<string> {
    if (!this.contracts.datasetMarketplace) {
      throw new Error('Contract not initialized')
    }

    try {
      // Upload metadata to IPFS
      const metadataHash = await ipfsService.uploadDatasetMetadata(metadata)
      
      // Submit dataset to contract
      const tx = await this.contracts.datasetMarketplace.submitDataset(
        name,
        description,
        category,
        metadataHash,
        ethers.utils.parseUnits(price, 6), // XRP has 6 decimals
        size
      )
      
      await tx.wait()
      return tx.hash
    } catch (error) {
      console.error('Failed to submit dataset:', error)
      throw error
    }
  }

  async purchaseDataset(datasetId: number): Promise<string> {
    if (!this.contracts.datasetMarketplace) {
      throw new Error('Contract not initialized')
    }

    try {
      const tx = await this.contracts.datasetMarketplace.purchaseDataset(datasetId)
      await tx.wait()
      return tx.hash
    } catch (error) {
      console.error('Failed to purchase dataset:', error)
      throw error
    }
  }

  async getDataset(datasetId: number): Promise<any> {
    if (!this.contracts.datasetMarketplace) {
      throw new Error('Contract not initialized')
    }

    try {
      const dataset = await this.contracts.datasetMarketplace.getDataset(datasetId)
      
      // Fetch metadata from IPFS
      const metadata = await ipfsService.getDatasetMetadata(dataset.metadataHash)
      
      return {
        ...dataset,
        metadata
      }
    } catch (error) {
      console.error('Failed to get dataset:', error)
      throw error
    }
  }

  /**
   * Agent Factory Functions
   */
  async createAgent(
    name: string,
    description: string,
    purpose: string,
    configuration: any,
    datasetIds: number[]
  ): Promise<string> {
    if (!this.contracts.agentFactory) {
      throw new Error('Contract not initialized')
    }

    try {
      // Create agent
      const tx = await this.contracts.agentFactory.createAgent(
        name,
        description,
        purpose,
        JSON.stringify(configuration)
      )
      
      await tx.wait()
      
      // Add datasets to agent
      for (const datasetId of datasetIds) {
        const addTx = await this.contracts.agentFactory.addDatasetToAgent(
          // Get agent ID from transaction events
          1, // This would be parsed from the transaction event
          datasetId,
          1 // Access level
        )
        await addTx.wait()
      }
      
      return tx.hash
    } catch (error) {
      console.error('Failed to create agent:', error)
      throw error
    }
  }

  async deployAgent(agentId: number): Promise<string> {
    if (!this.contracts.agentFactory) {
      throw new Error('Contract not initialized')
    }

    try {
      const tx = await this.contracts.agentFactory.deployAgent(agentId)
      await tx.wait()
      return tx.hash
    } catch (error) {
      console.error('Failed to deploy agent:', error)
      throw error
    }
  }

  async getAgent(agentId: number): Promise<any> {
    if (!this.contracts.agentFactory) {
      throw new Error('Contract not initialized')
    }

    try {
      const agent = await this.contracts.agentFactory.getAgent(agentId)
      const datasets = await this.contracts.agentFactory.getAgentDatasets(agentId)
      
      return {
        ...agent,
        datasets
      }
    } catch (error) {
      console.error('Failed to get agent:', error)
      throw error
    }
  }

  /**
   * Automation Engine Functions
   */
  async createTask(
    taskType: string,
    description: string,
    parameters: any,
    agentIds: number[],
    scheduledTime: number,
    isRecurring: boolean = false,
    recurrenceInterval: number = 0
  ): Promise<string> {
    if (!this.contracts.automationEngine) {
      throw new Error('Contract not initialized')
    }

    try {
      const tx = await this.contracts.automationEngine.createTask(
        taskType,
        description,
        JSON.stringify(parameters),
        agentIds,
        scheduledTime,
        isRecurring,
        recurrenceInterval
      )
      
      await tx.wait()
      return tx.hash
    } catch (error) {
      console.error('Failed to create task:', error)
      throw error
    }
  }

  async getTask(taskId: number): Promise<any> {
    if (!this.contracts.automationEngine) {
      throw new Error('Contract not initialized')
    }

    try {
      return await this.contracts.automationEngine.getTask(taskId)
    } catch (error) {
      console.error('Failed to get task:', error)
      throw error
    }
  }

  async cancelTask(taskId: number): Promise<string> {
    if (!this.contracts.automationEngine) {
      throw new Error('Contract not initialized')
    }

    try {
      const tx = await this.contracts.automationEngine.cancelTask(taskId)
      await tx.wait()
      return tx.hash
    } catch (error) {
      console.error('Failed to cancel task:', error)
      throw error
    }
  }

  /**
   * Token Functions
   */
  async getTokenBalance(address?: string): Promise<string> {
    if (!this.contracts.xrpToken) {
      throw new Error('Contract not initialized')
    }

    try {
      const balance = await this.contracts.xrpToken.balanceOf(
        address || (await this.signer!.getAddress())
      )
      return ethers.utils.formatUnits(balance, 6) // XRP has 6 decimals
    } catch (error) {
      console.error('Failed to get token balance:', error)
      throw error
    }
  }

  async approveToken(spender: string, amount: string): Promise<string> {
    if (!this.contracts.xrpToken) {
      throw new Error('Contract not initialized')
    }

    try {
      const tx = await this.contracts.xrpToken.approve(
        spender,
        ethers.utils.parseUnits(amount, 6)
      )
      await tx.wait()
      return tx.hash
    } catch (error) {
      console.error('Failed to approve token:', error)
      throw error
    }
  }

  /**
   * Utility Functions
   */
  async waitForTransaction(txHash: string): Promise<any> {
    if (!this.provider) {
      throw new Error('Provider not initialized')
    }

    try {
      return await this.provider.waitForTransaction(txHash)
    } catch (error) {
      console.error('Failed to wait for transaction:', error)
      throw error
    }
  }

  async getTransactionReceipt(txHash: string): Promise<any> {
    if (!this.provider) {
      throw new Error('Provider not initialized')
    }

    try {
      return await this.provider.getTransactionReceipt(txHash)
    } catch (error) {
      console.error('Failed to get transaction receipt:', error)
      throw error
    }
  }

  /**
   * Event Listeners
   */
  onDatasetSubmitted(callback: (event: any) => void): void {
    if (!this.contracts.datasetMarketplace) {
      throw new Error('Contract not initialized')
    }

    this.contracts.datasetMarketplace.on('DatasetSubmitted', callback)
  }

  onAgentCreated(callback: (event: any) => void): void {
    if (!this.contracts.agentFactory) {
      throw new Error('Contract not initialized')
    }

    this.contracts.agentFactory.on('AgentCreated', callback)
  }

  onTaskExecuted(callback: (event: any) => void): void {
    if (!this.contracts.automationEngine) {
      throw new Error('Contract not initialized')
    }

    this.contracts.automationEngine.on('TaskExecuted', callback)
  }

  /**
   * Remove all event listeners
   */
  removeAllListeners(): void {
    Object.values(this.contracts).forEach((contract: any) => {
      if (contract && contract.removeAllListeners) {
        contract.removeAllListeners()
      }
    })
  }
}

// Default configuration
const defaultConfig: Web3Config = {
  rpcUrl: 'http://localhost:8545',
  chainId: 1337,
  contracts: {
    xrpToken: '0x...', // Contract addresses would be set here
    datasetMarketplace: '0x...',
    agentFactory: '0x...',
    automationEngine: '0x...'
  }
}

// Create singleton instance
export const web3Service = new Web3Service(defaultConfig)

// Export the class for custom configurations
export default Web3Service

// Extend Window interface for TypeScript
declare global {
  interface Window {
    ethereum?: any
  }
}
