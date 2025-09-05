import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import { Wallet as XRPLWallet } from '@xrplf/xrpl'

export interface WalletState {
  // Connection state
  isConnected: boolean
  isLoading: boolean
  error: string | null
  
  // Wallet data
  wallet: XRPLWallet | null
  address: string | null
  balance: string | null
  sequence: number | null
  
  // Actions
  connect: (wallet: XRPLWallet) => void
  disconnect: () => void
  updateBalance: (balance: string) => void
  updateSequence: (sequence: number) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useWalletStore = create<WalletState>()(
  persist(
    immer((set, get) => ({
      // Initial state
      isConnected: false,
      isLoading: false,
      error: null,
      wallet: null,
      address: null,
      balance: null,
      sequence: null,
      
      // Actions
      connect: (wallet: XRPLWallet) => {
        set((state) => {
          state.isConnected = true
          state.wallet = wallet
          state.address = wallet.address
          state.error = null
        })
      },
      
      disconnect: () => {
        set((state) => {
          state.isConnected = false
          state.wallet = null
          state.address = null
          state.balance = null
          state.sequence = null
          state.error = null
        })
      },
      
      updateBalance: (balance: string) => {
        set((state) => {
          state.balance = balance
        })
      },
      
      updateSequence: (sequence: number) => {
        set((state) => {
          state.sequence = sequence
        })
      },
      
      setLoading: (loading: boolean) => {
        set((state) => {
          state.isLoading = loading
        })
      },
      
      setError: (error: string | null) => {
        set((state) => {
          state.error = error
        })
      },
      
      clearError: () => {
        set((state) => {
          state.error = null
        })
      },
    })),
    {
      name: 'xaman-wallet-storage',
      partialize: (state) => ({
        isConnected: state.isConnected,
        address: state.address,
        balance: state.balance,
        sequence: state.sequence,
      }),
    }
  )
)
