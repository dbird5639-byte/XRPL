import { Router, Request, Response } from 'express';
import { ValidatorService } from '../services/ValidatorService';

const router = Router();

// Initialize validator service (this would be injected in a real app)
const validatorService = new ValidatorService();

// Get validator status
router.get('/status', async (req: Request, res: Response) => {
  try {
    const status = await validatorService.getStatus();

    res.json({
      success: true,
      status
    });
  } catch (error) {
    console.error('Get validator status error:', error);
    res.status(500).json({
      error: 'Failed to get validator status',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get validator statistics
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const stats = await validatorService.getStatistics();

    res.json({
      success: true,
      stats
    });
  } catch (error) {
    console.error('Get validator stats error:', error);
    res.status(500).json({
      error: 'Failed to get validator statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get pending transactions
router.get('/transactions/pending', async (req: Request, res: Response) => {
  try {
    const pendingTxs = await validatorService.getPendingTransactions();

    res.json({
      success: true,
      transactions: pendingTxs,
      count: pendingTxs.length
    });
  } catch (error) {
    console.error('Get pending transactions error:', error);
    res.status(500).json({
      error: 'Failed to get pending transactions',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Process a transaction
router.post('/transactions/:txId/process', async (req: Request, res: Response) => {
  try {
    const { txId } = req.params;
    const { action } = req.body; // 'approve' or 'reject'

    if (!action || !['approve', 'reject'].includes(action)) {
      return res.status(400).json({
        error: 'Invalid action',
        validActions: ['approve', 'reject']
      });
    }

    const result = await validatorService.processTransaction(txId, action);

    res.json({
      success: true,
      transactionId: txId,
      action,
      result
    });
  } catch (error) {
    console.error('Process transaction error:', error);
    res.status(500).json({
      error: 'Failed to process transaction',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get validator configuration
router.get('/config', async (req: Request, res: Response) => {
  try {
    const config = await validatorService.getConfiguration();

    res.json({
      success: true,
      config
    });
  } catch (error) {
    console.error('Get validator config error:', error);
    res.status(500).json({
      error: 'Failed to get validator configuration',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Update validator configuration
router.put('/config', async (req: Request, res: Response) => {
  try {
    const { threshold, autoProcess, maxGasPrice } = req.body;

    const config = await validatorService.updateConfiguration({
      threshold,
      autoProcess,
      maxGasPrice
    });

    res.json({
      success: true,
      config
    });
  } catch (error) {
    console.error('Update validator config error:', error);
    res.status(500).json({
      error: 'Failed to update validator configuration',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get validator logs
router.get('/logs', async (req: Request, res: Response) => {
  try {
    const { limit = 100, offset = 0 } = req.query;

    const logs = await validatorService.getLogs(
      parseInt(limit as string),
      parseInt(offset as string)
    );

    res.json({
      success: true,
      logs,
      count: logs.length
    });
  } catch (error) {
    console.error('Get validator logs error:', error);
    res.status(500).json({
      error: 'Failed to get validator logs',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Start/stop validator
router.post('/control', async (req: Request, res: Response) => {
  try {
    const { action } = req.body; // 'start' or 'stop'

    if (!action || !['start', 'stop'].includes(action)) {
      return res.status(400).json({
        error: 'Invalid action',
        validActions: ['start', 'stop']
      });
    }

    if (action === 'start') {
      await validatorService.start();
    } else {
      await validatorService.stop();
    }

    res.json({
      success: true,
      action,
      message: `Validator ${action}ed successfully`
    });
  } catch (error) {
    console.error('Validator control error:', error);
    res.status(500).json({
      error: `Failed to ${req.body.action} validator`,
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export { router as validatorRoutes };
