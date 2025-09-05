"""
Cross-Chain Bridge Models
Data models for bridge transactions and network configurations
"""

from typing import Optional
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from datetime import datetime

class BridgeStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class NetworkType(Enum):
    XRPL = "XRPL"
    ETHEREUM = "ETHEREUM"
    BSC = "BSC"
    POLYGON = "POLYGON"
    ARBITRUM = "ARBITRUM"
    OPTIMISM = "OPTIMISM"

@dataclass
class BridgeTransaction:
    id: str
    source_network: NetworkType
    target_network: NetworkType
    source_address: str
    target_address: str
    amount: Decimal
    token: str
    status: BridgeStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    tx_hash: Optional[str] = None
    fee: Optional[Decimal] = None
    confirmation_blocks: int = 0

@dataclass
class NetworkConfig:
    name: str
    type: NetworkType
    rpc_url: str
    chain_id: int
    native_token: str
    gas_token: str
    bridge_contract: str
    min_confirmations: int
    fee_rate: Decimal
