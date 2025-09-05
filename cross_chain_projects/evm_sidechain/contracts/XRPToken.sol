// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title XRPToken
 * @dev ERC20 token representing XRP on EVM sidechain
 */
contract XRPToken is ERC20, ERC20Burnable, ERC20Pausable, Ownable, ReentrancyGuard {
    // Events
    event Mint(address indexed to, uint256 amount, string xrplTxHash);
    event Burn(address indexed from, uint256 amount, string xrplAddress);
    event BridgeUpdated(address indexed newBridge);
    event MinterAdded(address indexed minter);
    event MinterRemoved(address indexed minter);
    
    // State variables
    address public bridge;
    mapping(address => bool) public minters;
    uint256 public maxSupply = 100_000_000_000 * 10**18; // 100B XRP
    bool public mintingEnabled = true;
    
    // Modifiers
    modifier onlyBridge() {
        require(msg.sender == bridge, "Only bridge can call this function");
        _;
    }
    
    modifier onlyMinter() {
        require(minters[msg.sender] || msg.sender == owner(), "Only minters can call this function");
        _;
    }
    
    modifier mintingAllowed() {
        require(mintingEnabled, "Minting is disabled");
        _;
    }
    
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) {
        _mint(msg.sender, initialSupply);
    }
    
    /**
     * @dev Mint tokens (only bridge or minters)
     * @param to Recipient address
     * @param amount Amount to mint
     * @param xrplTxHash XRPL transaction hash
     */
    function mint(
        address to,
        uint256 amount,
        string calldata xrplTxHash
    ) external onlyMinter mintingAllowed nonReentrant {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Amount must be greater than 0");
        require(totalSupply() + amount <= maxSupply, "Exceeds max supply");
        
        _mint(to, amount);
        
        emit Mint(to, amount, xrplTxHash);
    }
    
    /**
     * @dev Burn tokens and prepare for XRPL withdrawal
     * @param amount Amount to burn
     * @param xrplAddress XRPL destination address
     */
    function burnForWithdrawal(
        uint256 amount,
        string calldata xrplAddress
    ) external nonReentrant {
        require(amount > 0, "Amount must be greater than 0");
        require(bytes(xrplAddress).length > 0, "Invalid XRPL address");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        
        _burn(msg.sender, amount);
        
        emit Burn(msg.sender, amount, xrplAddress);
    }
    
    /**
     * @dev Set bridge address (only owner)
     * @param newBridge New bridge address
     */
    function setBridge(address newBridge) external onlyOwner {
        require(newBridge != address(0), "Invalid bridge address");
        bridge = newBridge;
        
        emit BridgeUpdated(newBridge);
    }
    
    /**
     * @dev Add minter (only owner)
     * @param minter Minter address
     */
    function addMinter(address minter) external onlyOwner {
        require(minter != address(0), "Invalid minter address");
        require(!minters[minter], "Minter already exists");
        
        minters[minter] = true;
        
        emit MinterAdded(minter);
    }
    
    /**
     * @dev Remove minter (only owner)
     * @param minter Minter address
     */
    function removeMinter(address minter) external onlyOwner {
        require(minters[minter], "Minter does not exist");
        
        minters[minter] = false;
        
        emit MinterRemoved(minter);
    }
    
    /**
     * @dev Enable/disable minting (only owner)
     * @param enabled Whether minting is enabled
     */
    function setMintingEnabled(bool enabled) external onlyOwner {
        mintingEnabled = enabled;
    }
    
    /**
     * @dev Update max supply (only owner)
     * @param newMaxSupply New max supply
     */
    function updateMaxSupply(uint256 newMaxSupply) external onlyOwner {
        require(newMaxSupply >= totalSupply(), "New max supply too low");
        maxSupply = newMaxSupply;
    }
    
    /**
     * @dev Pause token transfers
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause token transfers
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Get current supply
     * @return Current total supply
     */
    function getCurrentSupply() external view returns (uint256) {
        return totalSupply();
    }
    
    /**
     * @dev Get remaining mintable supply
     * @return Remaining mintable supply
     */
    function getRemainingSupply() external view returns (uint256) {
        return maxSupply - totalSupply();
    }
    
    /**
     * @dev Check if address is minter
     * @param account Address to check
     * @return True if minter
     */
    function isMinter(address account) external view returns (bool) {
        return minters[account] || account == owner();
    }
    
    // Override required functions
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Pausable) {
        super._beforeTokenTransfer(from, to, amount);
    }
}