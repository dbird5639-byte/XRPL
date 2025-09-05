import { create, IPFSHTTPClient } from 'ipfs-http-client'

export interface IPFSConfig {
  host: string
  port: number
  protocol: string
  headers?: {
    authorization?: string
  }
}

export interface DatasetMetadata {
  name: string
  description: string
  category: string
  version: string
  size: number
  format: string
  tags: string[]
  quality: number
  license: string
  creator: string
  createdAt: string
  updatedAt: string
  schema?: any
  preview?: string
}

export interface AgentMetadata {
  name: string
  description: string
  purpose: string
  version: string
  model: string
  configuration: any
  datasets: string[]
  capabilities: string[]
  creator: string
  createdAt: string
  updatedAt: string
}

class IPFSService {
  private client: IPFSHTTPClient | null = null
  private config: IPFSConfig

  constructor(config: IPFSConfig) {
    this.config = config
    this.initializeClient()
  }

  private initializeClient() {
    try {
      this.client = create({
        host: this.config.host,
        port: this.config.port,
        protocol: this.config.protocol,
        headers: this.config.headers
      })
    } catch (error) {
      console.error('Failed to initialize IPFS client:', error)
    }
  }

  /**
   * Upload a file to IPFS
   */
  async uploadFile(file: File): Promise<string> {
    if (!this.client) {
      throw new Error('IPFS client not initialized')
    }

    try {
      const result = await this.client.add(file)
      return result.path
    } catch (error) {
      console.error('Failed to upload file to IPFS:', error)
      throw error
    }
  }

  /**
   * Upload JSON data to IPFS
   */
  async uploadJSON(data: any): Promise<string> {
    if (!this.client) {
      throw new Error('IPFS client not initialized')
    }

    try {
      const jsonString = JSON.stringify(data, null, 2)
      const result = await this.client.add(jsonString)
      return result.path
    } catch (error) {
      console.error('Failed to upload JSON to IPFS:', error)
      throw error
    }
  }

  /**
   * Upload dataset metadata to IPFS
   */
  async uploadDatasetMetadata(metadata: DatasetMetadata): Promise<string> {
    return this.uploadJSON(metadata)
  }

  /**
   * Upload agent metadata to IPFS
   */
  async uploadAgentMetadata(metadata: AgentMetadata): Promise<string> {
    return this.uploadJSON(metadata)
  }

  /**
   * Retrieve data from IPFS
   */
  async getData(hash: string): Promise<string> {
    if (!this.client) {
      throw new Error('IPFS client not initialized')
    }

    try {
      const chunks = []
      for await (const chunk of this.client.cat(hash)) {
        chunks.push(chunk)
      }
      return Buffer.concat(chunks).toString()
    } catch (error) {
      console.error('Failed to retrieve data from IPFS:', error)
      throw error
    }
  }

  /**
   * Retrieve JSON data from IPFS
   */
  async getJSON<T>(hash: string): Promise<T> {
    const data = await this.getData(hash)
    return JSON.parse(data)
  }

  /**
   * Retrieve dataset metadata from IPFS
   */
  async getDatasetMetadata(hash: string): Promise<DatasetMetadata> {
    return this.getJSON<DatasetMetadata>(hash)
  }

  /**
   * Retrieve agent metadata from IPFS
   */
  async getAgentMetadata(hash: string): Promise<AgentMetadata> {
    return this.getJSON<AgentMetadata>(hash)
  }

  /**
   * Pin data to IPFS (ensure it stays available)
   */
  async pinData(hash: string): Promise<void> {
    if (!this.client) {
      throw new Error('IPFS client not initialized')
    }

    try {
      await this.client.pin.add(hash)
    } catch (error) {
      console.error('Failed to pin data to IPFS:', error)
      throw error
    }
  }

  /**
   * Unpin data from IPFS
   */
  async unpinData(hash: string): Promise<void> {
    if (!this.client) {
      throw new Error('IPFS client not initialized')
    }

    try {
      await this.client.pin.rm(hash)
    } catch (error) {
      console.error('Failed to unpin data from IPFS:', error)
      throw error
    }
  }

  /**
   * Get IPFS gateway URL for a hash
   */
  getGatewayURL(hash: string): string {
    return `${this.config.protocol}://${this.config.host}:${this.config.port}/ipfs/${hash}`
  }

  /**
   * Validate IPFS hash format
   */
  isValidHash(hash: string): boolean {
    // Basic validation for IPFS hash (starts with Qm or bafy)
    return /^(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-z2-7]{52})$/.test(hash)
  }

  /**
   * Get file size from IPFS
   */
  async getFileSize(hash: string): Promise<number> {
    if (!this.client) {
      throw new Error('IPFS client not initialized')
    }

    try {
      const stats = await this.client.files.stat(`/ipfs/${hash}`)
      return stats.size
    } catch (error) {
      console.error('Failed to get file size from IPFS:', error)
      throw error
    }
  }

  /**
   * Check if data exists in IPFS
   */
  async exists(hash: string): Promise<boolean> {
    try {
      await this.getData(hash)
      return true
    } catch (error) {
      return false
    }
  }

  /**
   * Upload multiple files as a directory
   */
  async uploadDirectory(files: { path: string; content: File }[]): Promise<string> {
    if (!this.client) {
      throw new Error('IPFS client not initialized')
    }

    try {
      const result = await this.client.addAll(
        files.map(file => ({
          path: file.path,
          content: file.content
        }))
      )

      // Get the root hash (last result)
      let rootHash = ''
      for await (const file of result) {
        rootHash = file.path
      }

      return rootHash
    } catch (error) {
      console.error('Failed to upload directory to IPFS:', error)
      throw error
    }
  }

  /**
   * Get directory contents from IPFS
   */
  async getDirectoryContents(hash: string): Promise<{ name: string; hash: string; size: number }[]> {
    if (!this.client) {
      throw new Error('IPFS client not initialized')
    }

    try {
      const contents = []
      for await (const file of this.client.ls(hash)) {
        contents.push({
          name: file.name,
          hash: file.path,
          size: file.size
        })
      }
      return contents
    } catch (error) {
      console.error('Failed to get directory contents from IPFS:', error)
      throw error
    }
  }
}

// Default IPFS configuration
const defaultConfig: IPFSConfig = {
  host: 'localhost',
  port: 5001,
  protocol: 'http'
}

// Create singleton instance
export const ipfsService = new IPFSService(defaultConfig)

// Export the class for custom configurations
export default IPFSService
