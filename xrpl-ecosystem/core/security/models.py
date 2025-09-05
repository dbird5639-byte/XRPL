"""
Security Models
Data models for security events, rules, and user profiles
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

class SecurityLevel(Enum):
    """Security level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats"""
    SUSPICIOUS_TRANSACTION = "suspicious_transaction"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNUSUAL_PATTERN = "unusual_pattern"
    MALICIOUS_ADDRESS = "malicious_address"
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    LIQUIDITY_ATTACK = "liquidity_attack"
    PRICE_MANIPULATION = "price_manipulation"
    FRONTRUNNING = "frontrunning"
    MEV_ATTACK = "mev_attack"

class SecurityAction(Enum):
    """Security actions to take"""
    MONITOR = "monitor"
    WARN = "warn"
    THROTTLE = "throttle"
    BLOCK = "block"
    FREEZE = "freeze"
    ALERT = "alert"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"

@dataclass
class SecurityEvent:
    """Security event record"""
    id: str
    event_type: ThreatType
    threat_level: SecurityLevel
    description: str
    user_address: Optional[str] = None
    ip_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    actions_taken: List[SecurityAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityRule:
    """Security rule definition"""
    id: str
    name: str
    description: str
    rule_type: str
    conditions: Dict[str, Any]
    actions: List[SecurityAction]
    priority: int
    is_active: bool = True
    created_at: float = field(default_factory=time.time)

@dataclass
class UserSecurityProfile:
    """User security profile and risk assessment"""
    address: str
    risk_score: int  # 0-100, 100 being highest risk
    trust_score: int  # 0-100, 100 being most trusted
    suspicious_activities: int
    total_transactions: int
    last_activity: float
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
