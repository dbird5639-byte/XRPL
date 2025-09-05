// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title XRPToken
 * @dev ERC-20 representation of XRP for AI Framework
 */
contract XRPToken is ERC20, Ownable, Pausable {
    uint8 private constant _DECIMALS = 6; // XRP has 6 decimals
    
    constructor() ERC20("XRP Token", "XRP") {
        // Mint initial supply (1 billion XRP)
        _mint(msg.sender, 1000000000 * 10**_DECIMALS);
    }
    
    function decimals() public pure override returns (uint8) {
        return _DECIMALS;
    }
    
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
    
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }
}
