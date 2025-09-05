#!/usr/bin/env python3
"""
XRPL Ecosystem Configuration
Centralized configuration management for all XRPL components
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class XRPLConfig:
    """XRPL Network Configuration"""
    mainnet_url: str = "wss://xrplcluster.com"
    testnet_url: str = "wss://s.altnet.rippletest.net:51233"
    devnet_url: str = "wss://s.devnet.rippletest.net:51233"
    amm_devnet_url: str = "wss://amm.devnet.rippletest.net:51233"

@dataclass
class BridgeConfig:
    """Cross-Chain Bridge Configuration"""
    ethereum_rpc: str = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
    solana_rpc: str = "https://api.mainnet-beta.solana.com"
    polygon_rpc: str = "https://polygon-rpc.com"
    cosmos_rpc: str = "https://rpc.cosmos.network:26657"
    
    # Bridge contracts
    ethereum_bridge: str = "0x..."
    solana_bridge: str = "..."
    polygon_bridge: str = "0x..."

@dataclass
class DEXConfig:
    """DEX Trading Engine Configuration"""
    order_book_depth: int = 100
    max_orders_per_user: int = 1000
    min_order_size: float = 0.001
    max_order_size: float = 1000000.0
    fee_structure: Dict[str, float] = None
    
    def __post_init__(self):
        if self.fee_structure is None:
            self.fee_structure = {
                "maker": 0.001,  # 0.1%
                "taker": 0.002,  # 0.2%
                "withdrawal": 0.0001
            }

@dataclass
class AIConfig:
    """AI Trading Configuration"""
    model_path: str = "models/"
    training_data_path: str = "data/training/"
    prediction_interval: int = 60  # seconds
    confidence_threshold: float = 0.7
    max_position_size: float = 0.1  # 10% of portfolio
    
    # ML model parameters
    lstm_units: int = 128
    dropout_rate: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 32

@dataclass
class DatabaseConfig:
    """Database Configuration"""
    postgres_url: str = "postgresql://user:pass@localhost:5432/xrpl_ecosystem"
    redis_url: str = "redis://localhost:6379"
    mongodb_url: str = "mongodb://localhost:27017/xrpl_ecosystem"
    
    # Connection pools
    max_connections: int = 20
    connection_timeout: int = 30

@dataclass
class APIConfig:
    """API Configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "https://yourdomain.com"]

@dataclass
class SecurityConfig:
    """Security Configuration"""
    jwt_secret: str = "your-super-secret-jwt-key"
    jwt_expiration: int = 3600  # 1 hour
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # 1 minute
    
    # API keys
    require_api_key: bool = True
    api_key_header: str = "X-API-Key"

class Config:
    """Main Configuration Class"""
    
    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.base_path = Path(__file__).parent.parent
        
        # Initialize configurations
        self.xrpl = XRPLConfig()
        self.bridge = BridgeConfig()
        self.dex = DEXConfig()
        self.ai = AIConfig()
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.security = SecurityConfig()
        
        # Load environment-specific configs
        self._load_environment_config()
    
    def _load_environment_config(self):
        """Load environment-specific configurations"""
        env_file = self.base_path / f".env.{self.environment}"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        # Override with environment variables
        self._override_from_env()
    
    def _override_from_env(self):
        """Override config values from environment variables"""
        # XRPL
        if os.getenv("XRPL_MAINNET_URL"):
            self.xrpl.mainnet_url = os.getenv("XRPL_MAINNET_URL")
        
        # Bridge
        if os.getenv("ETHEREUM_RPC"):
            self.bridge.ethereum_rpc = os.getenv("ETHEREUM_RPC")
        
        # Database
        if os.getenv("DATABASE_URL"):
            self.database.postgres_url = os.getenv("DATABASE_URL")
        
        # API
        if os.getenv("API_PORT"):
            self.api.port = int(os.getenv("API_PORT"))
        
        # Security
        if os.getenv("JWT_SECRET"):
            self.security.jwt_secret = os.getenv("JWT_SECRET")
    
    def get_xrpl_url(self, network: str = "mainnet") -> str:
        """Get XRPL URL for specified network"""
        urls = {
            "mainnet": self.xrpl.mainnet_url,
            "testnet": self.xrpl.testnet_url,
            "devnet": self.xrpl.devnet_url,
            "amm_devnet": self.xrpl.amm_devnet_url
        }
        return urls.get(network, self.xrpl.mainnet_url)
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"

# Global config instance
config = Config()

# Export commonly used configs
XRPL_CONFIG = config.xrpl
BRIDGE_CONFIG = config.bridge
DEX_CONFIG = config.dex
AI_CONFIG = config.ai
DB_CONFIG = config.database
API_CONFIG = config.api
SECURITY_CONFIG = config.security
