import { useState, useEffect, useCallback } from 'react'
import { web3Service } from '../services/web3Service'

export interface ContractData {
  datasets: any[]
  agents: any[]
  tasks: any[]
  templates: any[]
  isLoading: boolean
  error: string | null
}

export interface UseContractsReturn extends ContractData {
  submitDataset: (data: any) => Promise<string>
  purchaseDataset: (datasetId: number) => Promise<string>
  createAgent: (data: any) => Promise<string>
  deployAgent: (agentId: number) => Promise<string>
  createTask: (data: any) => Promise<string>
  cancelTask: (taskId: number) => Promise<string>
  refreshData: () => Promise<void>
}

export const useContracts = (): UseContractsReturn => {
  const [datasets, setDatasets] = useState<any[]>([])
  const [agents, setAgents] = useState<any[]>([])
  const [tasks, setTasks] = useState<any[]>([])
  const [templates, setTemplates] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load initial data
  useEffect(() => {
    if (web3Service.isConnected()) {
      loadData()
    }
  }, [])

  const loadData = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Load datasets, agents, tasks, and templates
      await Promise.all([
        loadDatasets(),
        loadAgents(),
        loadTasks(),
        loadTemplates()
      ])
    } catch (err: any) {
      setError(err.message || 'Failed to load data')
      console.error('Data loading error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const loadDatasets = useCallback(async () => {
    try {
      // In a real implementation, this would call the contract or API
      // For now, we'll use mock data
      const mockDatasets = [
        {
          id: 1,
          name: 'Financial Market Data',
          description: 'Real-time financial market data',
          category: 'finance',
          price: '500',
          size: 1073741824,
          qualityScore: 95,
          status: 'approved',
          submitter: '0x1234...5678',
          purchaseCount: 127,
          rating: 4.8,
          tags: ['real-time', 'crypto', 'stocks'],
          createdAt: '2024-01-15T10:30:00Z'
        }
      ]
      setDatasets(mockDatasets)
    } catch (err) {
      console.error('Failed to load datasets:', err)
    }
  }, [])

  const loadAgents = useCallback(async () => {
    try {
      // Mock data for agents
      const mockAgents = [
        {
          id: 1,
          name: 'DeFi Trading Bot',
          description: 'Automated DeFi trading strategies',
          purpose: 'Trading and yield optimization',
          status: 'active',
          datasets: [1, 2],
          usageCount: 1247,
          revenue: '2340',
          createdAt: '2024-01-10T10:30:00Z'
        }
      ]
      setAgents(mockAgents)
    } catch (err) {
      console.error('Failed to load agents:', err)
    }
  }, [])

  const loadTasks = useCallback(async () => {
    try {
      // Mock data for tasks
      const mockTasks = [
        {
          id: 1,
          name: 'Daily Portfolio Rebalancing',
          type: 'defi_strategy',
          description: 'Automatically rebalance portfolio',
          status: 'completed',
          lastRun: '2024-01-20T14:30:00Z',
          nextRun: '2024-01-21T14:30:00Z',
          frequency: 'daily',
          successRate: 95,
          totalRuns: 20,
          cost: '25',
          revenue: '45'
        }
      ]
      setTasks(mockTasks)
    } catch (err) {
      console.error('Failed to load tasks:', err)
    }
  }, [])

  const loadTemplates = useCallback(async () => {
    try {
      // Mock data for templates
      const mockTemplates = [
        {
          id: 1,
          name: 'DeFi Yield Optimizer',
          description: 'Automatically find best yield opportunities',
          type: 'defi_strategy',
          cost: '30',
          usageCount: 156,
          rating: 4.5,
          isPublic: true
        }
      ]
      setTemplates(mockTemplates)
    } catch (err) {
      console.error('Failed to load templates:', err)
    }
  }, [])

  const submitDataset = useCallback(async (data: any): Promise<string> => {
    try {
      const txHash = await web3Service.submitDataset(
        data.name,
        data.description,
        data.category,
        data.price,
        data.size,
        data.metadata
      )
      
      // Refresh datasets after submission
      await loadDatasets()
      
      return txHash
    } catch (err: any) {
      setError(err.message || 'Failed to submit dataset')
      throw err
    }
  }, [loadDatasets])

  const purchaseDataset = useCallback(async (datasetId: number): Promise<string> => {
    try {
      const txHash = await web3Service.purchaseDataset(datasetId)
      
      // Refresh datasets after purchase
      await loadDatasets()
      
      return txHash
    } catch (err: any) {
      setError(err.message || 'Failed to purchase dataset')
      throw err
    }
  }, [loadDatasets])

  const createAgent = useCallback(async (data: any): Promise<string> => {
    try {
      const txHash = await web3Service.createAgent(
        data.name,
        data.description,
        data.purpose,
        data.configuration,
        data.datasetIds
      )
      
      // Refresh agents after creation
      await loadAgents()
      
      return txHash
    } catch (err: any) {
      setError(err.message || 'Failed to create agent')
      throw err
    }
  }, [loadAgents])

  const deployAgent = useCallback(async (agentId: number): Promise<string> => {
    try {
      const txHash = await web3Service.deployAgent(agentId)
      
      // Refresh agents after deployment
      await loadAgents()
      
      return txHash
    } catch (err: any) {
      setError(err.message || 'Failed to deploy agent')
      throw err
    }
  }, [loadAgents])

  const createTask = useCallback(async (data: any): Promise<string> => {
    try {
      const txHash = await web3Service.createTask(
        data.taskType,
        data.description,
        data.parameters,
        data.agentIds,
        data.scheduledTime,
        data.isRecurring,
        data.recurrenceInterval
      )
      
      // Refresh tasks after creation
      await loadTasks()
      
      return txHash
    } catch (err: any) {
      setError(err.message || 'Failed to create task')
      throw err
    }
  }, [loadTasks])

  const cancelTask = useCallback(async (taskId: number): Promise<string> => {
    try {
      const txHash = await web3Service.cancelTask(taskId)
      
      // Refresh tasks after cancellation
      await loadTasks()
      
      return txHash
    } catch (err: any) {
      setError(err.message || 'Failed to cancel task')
      throw err
    }
  }, [loadTasks])

  const refreshData = useCallback(async () => {
    await loadData()
  }, [loadData])

  return {
    datasets,
    agents,
    tasks,
    templates,
    isLoading,
    error,
    submitDataset,
    purchaseDataset,
    createAgent,
    deployAgent,
    createTask,
    cancelTask,
    refreshData
  }
}
