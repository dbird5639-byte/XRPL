import { Router } from 'express';
import { bridgeRoutes } from './bridge';
import { defiRoutes } from './defi';
import { validatorRoutes } from './validator';

const router = Router();

// Mount route modules
router.use('/bridge', bridgeRoutes);
router.use('/defi', defiRoutes);
router.use('/validator', validatorRoutes);

// API info endpoint
router.get('/', (req, res) => {
  res.json({
    name: 'XRPL EVM Sidechain API',
    version: '1.0.0',
    description: 'Bridge and DeFi services for XRPL EVM sidechain',
    endpoints: {
      bridge: '/api/bridge',
      defi: '/api/defi',
      validator: '/api/validator',
      health: '/health'
    }
  });
});

export { router as routes };
