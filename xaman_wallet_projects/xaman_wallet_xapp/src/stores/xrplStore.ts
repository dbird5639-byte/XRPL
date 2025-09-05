import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { Client, AccountInfo, LedgerIndex } from '@xrplf/xrpl'

export interface XRPLState {
  // Connection state
  isInitialized: boolean
  isConnected: boolean
  client: Client | null
  network: 'mainnet' | 'testnet' | 'devnet'
  
  // Network data
  ledgerIndex: number | null
  fee: string | null
  serverState: string | null
  
  // Actions
  initialize: (network?: 'mainnet' | 'testnet' | 'devnet') => Promise<void>
  connect: () => Promise<void>
  disconnect: () => Promise<void>
  getAccountInfo: (address: string) => Promise<AccountInfo | null>
  getBalance: (address: string) => Promise<string | null>
  updateNetworkInfo: () => Promise<void>
  setNetwork: (network: 'mainnet' | 'testnet' | 'devnet') => void
}

export const useXRPLStore = create<XRPLState>()(
  immer((set, get) => ({
    // Initial state
    isInitialized: false,
    isConnected: false,
    client: null,
    network: 'testnet',
    ledgerIndex: null,
    fee: null,
    serverState: null,
    
    // Actions
    initialize: async (network = 'testnet') => {
      try {
        set((state) => {
          state.isInitialized = false
          state.network = network
        })
        
        const { Client } = await import('@xrplf/xrpl')
        
        const client = new Client(
          network === 'mainnet' 
            ? 'wss://xrplcluster.com'
            : network === 'testnet'
            ? 'wss://s.altnet.rippletest.net:51233'
            : 'wss://s.devnet.rippletest.net:51233'
        )
        
        set((state) => {
          state.client = client
          state.isInitialized = true
        })
        
        await get().connect()
      } catch (error) {
        console.error('Failed to initialize XRPL client:', error)
        throw error
      }
    },
    
    connect: async () => {
      const { client } = get()
      if (!client) {
        throw new Error('Client not initialized')
      }
      
      try {
        await client.connect()
        
        set((state) => {
          state.isConnected = true
        })
        
        await get().updateNetworkInfo()
      } catch (error) {
        console.error('Failed to connect to XRPL:', error)
        throw error
      }
    },
    
    disconnect: async () => {
      const { client } = get()
      if (client && get().isConnected) {
        try {
          await client.disconnect()
        } catch (error) {
          console.error('Error disconnecting from XRPL:', error)
        }
      }
      
      set((state) => {
        state.isConnected = false
        state.ledgerIndex = null
        state.fee = null
        state.serverState = null
      })
    },
    
    getAccountInfo: async (address: string) => {
      const { client } = get()
      if (!client || !get().isConnected) {
        throw new Error('Not connected to XRPL')
      }
      
      try {
        const accountInfo = await client.request({
          command: 'account_info',
          account: address,
          ledger_index: 'validated' as LedgerIndex,
        })
        
        return accountInfo.result.account_data
      } catch (error) {
        console.error('Failed to get account info:', error)
        return null
      }
    },
    
    getBalance: async (address: string) => {
      const { client } = get()
      if (!client || !get().isConnected) {
        throw new Error('Not connected to XRPL')
      }
      
      try {
        const accountInfo = await client.request({
          command: 'account_info',
          account: address,
          ledger_index: 'validated' as LedgerIndex,
        })
        
        const balance = accountInfo.result.account_data.Balance
        return balance
      } catch (error) {
        console.error('Failed to get balance:', error)
        return null
      }
    },
    
    updateNetworkInfo: async () => {
      const { client } = get()
      if (!client || !get().isConnected) {
        return
      }
      
      try {
        const serverInfo = await client.request({
          command: 'server_info',
        })
        
        const fee = await client.request({
          command: 'fee',
        })
        
        set((state) => {
          state.ledgerIndex = serverInfo.result.info.validated_ledger?.seq || null
          state.fee = fee.result.drops?.base_fee || null
          state.serverState = serverInfo.result.info.server_state || null
        })
      } catch (error) {
        console.error('Failed to update network info:', error)
      }
    },
    
    setNetwork: (network: 'mainnet' | 'testnet' | 'devnet') => {
      set((state) => {
        state.network = network
      })
    },
  }))
)
