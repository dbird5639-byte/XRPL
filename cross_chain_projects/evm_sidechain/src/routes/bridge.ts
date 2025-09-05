import { Router, Request, Response } from 'express';
import { EVMBridge } from '../services/EVMBridge';
import { XRPLSidechain } from '../services/XRPLSidechain';

const router = Router();

// Initialize services (these would be injected in a real app)
const evmBridge = new EVMBridge();
const xrplSidechain = new XRPLSidechain();

// Bridge deposit endpoint
router.post('/deposit', async (req: Request, res: Response) => {
  try {
    const { userAddress, amount, xrplAddress } = req.body;

    if (!userAddress || !amount || !xrplAddress) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['userAddress', 'amount', 'xrplAddress']
      });
    }

    const txHash = await evmBridge.deposit(userAddress, amount, xrplAddress);

    res.json({
      success: true,
      transactionHash: txHash,
      message: 'Deposit initiated successfully'
    });
  } catch (error) {
    console.error('Deposit error:', error);
    res.status(500).json({
      error: 'Deposit failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Bridge withdrawal endpoint
router.post('/withdraw', async (req: Request, res: Response) => {
  try {
    const { userAddress, amount, xrplTxHash } = req.body;

    if (!userAddress || !amount || !xrplTxHash) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['userAddress', 'amount', 'xrplTxHash']
      });
    }

    // Verify XRPL transaction
    const isValid = await xrplSidechain.validateTransaction(xrplTxHash);
    if (!isValid) {
      return res.status(400).json({
        error: 'Invalid XRPL transaction',
        message: 'Transaction not found or not validated'
      });
    }

    // Check if already processed
    const isProcessed = await evmBridge.isXrplTxProcessed(xrplTxHash);
    if (isProcessed) {
      return res.status(400).json({
        error: 'Transaction already processed',
        message: 'This XRPL transaction has already been processed'
      });
    }

    const txHash = await evmBridge.withdraw(userAddress, amount, xrplTxHash);

    res.json({
      success: true,
      transactionHash: txHash,
      message: 'Withdrawal completed successfully'
    });
  } catch (error) {
    console.error('Withdrawal error:', error);
    res.status(500).json({
      error: 'Withdrawal failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get balance endpoint
router.get('/balance/:address', async (req: Request, res: Response) => {
  try {
    const { address } = req.params;

    if (!address) {
      return res.status(400).json({
        error: 'Address is required'
      });
    }

    const balance = await evmBridge.getBalance(address);

    res.json({
      address,
      balance,
      currency: 'XRP'
    });
  } catch (error) {
    console.error('Balance error:', error);
    res.status(500).json({
      error: 'Failed to get balance',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get transaction details
router.get('/transaction/:txHash', async (req: Request, res: Response) => {
  try {
    const { txHash } = req.params;

    if (!txHash) {
      return res.status(400).json({
        error: 'Transaction hash is required'
      });
    }

    const txDetails = await evmBridge.getTransactionDetails(txHash);

    res.json({
      success: true,
      transaction: txDetails
    });
  } catch (error) {
    console.error('Transaction details error:', error);
    res.status(500).json({
      error: 'Failed to get transaction details',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Check XRPL transaction status
router.get('/xrpl-status/:txHash', async (req: Request, res: Response) => {
  try {
    const { txHash } = req.params;

    if (!txHash) {
      return res.status(400).json({
        error: 'Transaction hash is required'
      });
    }

    const isValid = await xrplSidechain.validateTransaction(txHash);
    const isProcessed = await evmBridge.isXrplTxProcessed(txHash);

    res.json({
      txHash,
      isValid,
      isProcessed,
      status: isValid ? (isProcessed ? 'processed' : 'pending') : 'invalid'
    });
  } catch (error) {
    console.error('XRPL status error:', error);
    res.status(500).json({
      error: 'Failed to check XRPL transaction status',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get bridge statistics
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const networkInfo = await evmBridge.getNetworkInfo();
    const xrplInfo = await xrplSidechain.getNetworkInfo();

    res.json({
      evm: {
        chainId: networkInfo.chainId,
        blockNumber: networkInfo.blockNumber,
        gasPrice: networkInfo.gasPrice
      },
      xrpl: {
        network: xrplInfo.network,
        ledgerIndex: xrplInfo.ledgerIndex,
        serverState: xrplInfo.serverState
      },
      bridge: {
        status: 'active',
        lastUpdate: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('Stats error:', error);
    res.status(500).json({
      error: 'Failed to get bridge statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export { router as bridgeRoutes };
