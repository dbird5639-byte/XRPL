"""
Web3 Features for XRP Health Score Platform
==========================================

This module provides Web3 features including airdrops, farming, mining,
NFT integration, and other decentralized finance activities.
"""

from .airdrop_system import AirdropSystem, Airdrop
from .farming_system import FarmingSystem, Farm
from .mining_system import MiningSystem, MiningPool
from .nft_integration import NFTIntegration, NFTCollection
from .defi_protocols import DeFiProtocolManager, DeFiProtocol

__all__ = [
    'AirdropSystem',
    'Airdrop',
    'FarmingSystem',
    'Farm',
    'MiningSystem',
    'MiningPool',
    'NFTIntegration',
    'NFTCollection',
    'DeFiProtocolManager',
    'DeFiProtocol'
]
