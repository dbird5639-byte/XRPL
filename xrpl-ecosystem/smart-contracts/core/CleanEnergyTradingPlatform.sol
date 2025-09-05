// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title Clean Energy Trading Platform
 * @dev Blockchain-based energy marketplace for global clean energy cooperation
 * @author Vision 2030+ Development Team
 * @notice Enables cross-border trading of clean energy, carbon credits, and hydrogen
 */

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract CleanEnergyTradingPlatform is ReentrancyGuard, Ownable {
    using Counters for Counters.Counter;
    
    // ============ STRUCTS ============
    
    struct EnergyProducer {
        string name;
        string country;
        address wallet;
        uint256 totalCapacity; // in MWh
        uint256 availableCapacity;
        uint256[] energyTypes; // 1: Solar, 2: Wind, 3: Hydro, 4: Nuclear, 5: Hydrogen
        bool isVerified;
        uint256 registrationDate;
    }
    
    struct EnergyOrder {
        uint256 id;
        address producer;
        uint256 energyType;
        uint256 amount; // in MWh
        uint256 pricePerMWh; // in wei
        uint256 deliveryDate;
        string deliveryLocation;
        bool isActive;
        bool isFulfilled;
        address buyer;
        uint256 timestamp;
    }
    
    struct CarbonCredit {
        uint256 id;
        address issuer;
        uint256 amount; // in tons CO2 equivalent
        uint256 pricePerTon;
        string verificationMethod;
        bool isVerified;
        bool isRetired;
        uint256 issueDate;
        uint256 expiryDate;
    }
    
    struct HydrogenOrder {
        uint256 id;
        address producer;
        uint256 amount; // in kg
        uint256 pricePerKg;
        uint8 purity; // 99.9% = 999
        string productionMethod; // "Green", "Blue", "Grey"
        uint256 deliveryDate;
        string deliveryLocation;
        bool isActive;
        bool isFulfilled;
        address buyer;
    }
    
    // ============ STATE VARIABLES ============
    
    Counters.Counter private _orderCounter;
    Counters.Counter private _carbonCreditCounter;
    Counters.Counter private _hydrogenOrderCounter;
    
    mapping(address => EnergyProducer) public energyProducers;
    mapping(uint256 => EnergyOrder) public energyOrders;
    mapping(uint256 => CarbonCredit) public carbonCredits;
    mapping(uint256 => HydrogenOrder) public hydrogenOrders;
    
    mapping(address => bool) public isRegisteredProducer;
    mapping(address => uint256) public producerBalances;
    
    address[] public registeredProducers;
    uint256[] public activeEnergyOrders;
    uint256[] public availableCarbonCredits;
    uint256[] public activeHydrogenOrders;
    
    // Energy type constants
    uint256 public constant SOLAR = 1;
    uint256 public constant WIND = 2;
    uint256 public constant HYDRO = 3;
    uint256 public constant NUCLEAR = 4;
    uint256 public constant HYDROGEN = 5;
    
    // Platform fees (in basis points, 100 = 1%)
    uint256 public platformFee = 25; // 0.25%
    uint256 public constant MAX_PLATFORM_FEE = 100; // 1%
    
    // ============ EVENTS ============
    
    event ProducerRegistered(address indexed producer, string name, string country, uint256 capacity);
    event EnergyOrderCreated(uint256 indexed orderId, address indexed producer, uint256 energyType, uint256 amount, uint256 price);
    event EnergyOrderFulfilled(uint256 indexed orderId, address indexed buyer, uint256 amount, uint256 totalPrice);
    event CarbonCreditIssued(uint256 indexed creditId, address indexed issuer, uint256 amount, uint256 price);
    event CarbonCreditRetired(uint256 indexed creditId, address indexed buyer, uint256 amount);
    event HydrogenOrderCreated(uint256 indexed orderId, address indexed producer, uint256 amount, uint8 purity);
    event HydrogenOrderFulfilled(uint256 indexed orderId, address indexed buyer, uint256 amount);
    event EnergyCooperationEstablished(address indexed producerA, address indexed producerB, uint256 sharedCapacity);
    event CrossBorderEnergyTransfer(string indexed fromCountry, string indexed toCountry, uint256 amount);
    
    // ============ MODIFIERS ============
    
    modifier onlyRegisteredProducer() {
        require(isRegisteredProducer[msg.sender], "Only registered producers can perform this action");
        _;
    }
    
    modifier onlyActiveOrder(uint256 _orderId) {
        require(energyOrders[_orderId].isActive, "Order is not active");
        _;
    }
    
    modifier onlyVerifiedProducer() {
        require(energyProducers[msg.sender].isVerified, "Producer must be verified");
        _;
    }
    
    // ============ CONSTRUCTOR ============
    
    constructor() {
        // Initialize platform
    }
    
    // ============ PRODUCER MANAGEMENT ============
    
    function registerProducer(
        string memory _name,
        string memory _country,
        uint256 _totalCapacity,
        uint256[] memory _energyTypes
    ) external {
        require(!isRegisteredProducer[msg.sender], "Producer already registered");
        require(_totalCapacity > 0, "Capacity must be greater than 0");
        require(_energyTypes.length > 0, "Must specify at least one energy type");
        
        energyProducers[msg.sender] = EnergyProducer({
            name: _name,
            country: _country,
            wallet: msg.sender,
            totalCapacity: _totalCapacity,
            availableCapacity: _totalCapacity,
            energyTypes: _energyTypes,
            isVerified: false, // Requires manual verification
            registrationDate: block.timestamp
        });
        
        isRegisteredProducer[msg.sender] = true;
        registeredProducers.push(msg.sender);
        
        emit ProducerRegistered(msg.sender, _name, _country, _totalCapacity);
    }
    
    function verifyProducer(address _producer) external onlyOwner {
        require(isRegisteredProducer[_producer], "Producer not registered");
        energyProducers[_producer].isVerified = true;
    }
    
    function updateProducerCapacity(uint256 _newCapacity) external onlyRegisteredProducer {
        require(_newCapacity >= energyProducers[msg.sender].availableCapacity, "New capacity cannot be less than available");
        
        energyProducers[msg.sender].totalCapacity = _newCapacity;
    }
    
    // ============ ENERGY TRADING ============
    
    function createEnergyOrder(
        uint256 _energyType,
        uint256 _amount,
        uint256 _pricePerMWh,
        uint256 _deliveryDate,
        string memory _deliveryLocation
    ) external onlyRegisteredProducer onlyVerifiedProducer returns (uint256) {
        require(_amount > 0, "Amount must be greater than 0");
        require(_pricePerMWh > 0, "Price must be greater than 0");
        require(_deliveryDate > block.timestamp, "Delivery date must be in the future");
        require(energyProducers[msg.sender].availableCapacity >= _amount, "Insufficient available capacity");
        
        // Check if producer supports this energy type
        bool supportsEnergyType = false;
        for (uint256 i = 0; i < energyProducers[msg.sender].energyTypes.length; i++) {
            if (energyProducers[msg.sender].energyTypes[i] == _energyType) {
                supportsEnergyType = true;
                break;
            }
        }
        require(supportsEnergyType, "Producer does not support this energy type");
        
        _orderCounter.increment();
        uint256 orderId = _orderCounter.current();
        
        energyOrders[orderId] = EnergyOrder({
            id: orderId,
            producer: msg.sender,
            energyType: _energyType,
            amount: _amount,
            pricePerMWh: _pricePerMWh,
            deliveryDate: _deliveryDate,
            deliveryLocation: _deliveryLocation,
            isActive: true,
            isFulfilled: false,
            buyer: address(0),
            timestamp: block.timestamp
        });
        
        activeEnergyOrders.push(orderId);
        energyProducers[msg.sender].availableCapacity -= _amount;
        
        emit EnergyOrderCreated(orderId, msg.sender, _energyType, _amount, _pricePerMWh);
        
        return orderId;
    }
    
    function purchaseEnergyOrder(uint256 _orderId) external payable onlyActiveOrder(_orderId) nonReentrant {
        EnergyOrder storage order = energyOrders[_orderId];
        require(order.buyer == address(0), "Order already purchased");
        
        uint256 totalPrice = order.amount * order.pricePerMWh;
        uint256 platformFeeAmount = (totalPrice * platformFee) / 10000;
        uint256 producerAmount = totalPrice - platformFeeAmount;
        
        require(msg.value >= totalPrice, "Insufficient payment");
        
        // Update order
        order.buyer = msg.sender;
        order.isActive = false;
        order.isFulfilled = true;
        
        // Transfer funds
        payable(order.producer).transfer(producerAmount);
        if (platformFeeAmount > 0) {
            payable(owner()).transfer(platformFeeAmount);
        }
        
        // Refund excess payment
        if (msg.value > totalPrice) {
            payable(msg.sender).transfer(msg.value - totalPrice);
        }
        
        // Remove from active orders
        _removeFromActiveOrders(_orderId);
        
        emit EnergyOrderFulfilled(_orderId, msg.sender, order.amount, totalPrice);
        
        // Log cross-border transfer if applicable
        if (keccak256(bytes(energyProducers[order.producer].country)) != keccak256(bytes("Unknown"))) {
            emit CrossBorderEnergyTransfer(energyProducers[order.producer].country, "Buyer Country", order.amount);
        }
    }
    
    function cancelEnergyOrder(uint256 _orderId) external onlyActiveOrder(_orderId) {
        EnergyOrder storage order = energyOrders[_orderId];
        require(order.producer == msg.sender, "Only producer can cancel order");
        
        order.isActive = false;
        energyProducers[msg.sender].availableCapacity += order.amount;
        
        _removeFromActiveOrders(_orderId);
    }
    
    // ============ CARBON CREDIT TRADING ============
    
    function issueCarbonCredit(
        uint256 _amount,
        uint256 _pricePerTon,
        string memory _verificationMethod,
        uint256 _expiryDate
    ) external onlyRegisteredProducer onlyVerifiedProducer returns (uint256) {
        require(_amount > 0, "Amount must be greater than 0");
        require(_pricePerTon > 0, "Price must be greater than 0");
        require(_expiryDate > block.timestamp, "Expiry date must be in the future");
        
        _carbonCreditCounter.increment();
        uint256 creditId = _carbonCreditCounter.current();
        
        carbonCredits[creditId] = CarbonCredit({
            id: creditId,
            issuer: msg.sender,
            amount: _amount,
            pricePerTon: _pricePerTon,
            verificationMethod: _verificationMethod,
            isVerified: false, // Requires manual verification
            isRetired: false,
            issueDate: block.timestamp,
            expiryDate: _expiryDate
        });
        
        availableCarbonCredits.push(creditId);
        
        emit CarbonCreditIssued(creditId, msg.sender, _amount, _pricePerTon);
        
        return creditId;
    }
    
    function verifyCarbonCredit(uint256 _creditId) external onlyOwner {
        require(carbonCredits[_creditId].id != 0, "Credit does not exist");
        carbonCredits[_creditId].isVerified = true;
    }
    
    function purchaseCarbonCredit(uint256 _creditId, uint256 _amount) external payable nonReentrant {
        CarbonCredit storage credit = carbonCredits[_creditId];
        require(credit.id != 0, "Credit does not exist");
        require(credit.isVerified, "Credit must be verified");
        require(!credit.isRetired, "Credit already retired");
        require(credit.amount >= _amount, "Insufficient credit amount");
        require(block.timestamp <= credit.expiryDate, "Credit has expired");
        
        uint256 totalPrice = _amount * credit.pricePerTon;
        uint256 platformFeeAmount = (totalPrice * platformFee) / 10000;
        uint256 issuerAmount = totalPrice - platformFeeAmount;
        
        require(msg.value >= totalPrice, "Insufficient payment");
        
        // Update credit
        credit.amount -= _amount;
        if (credit.amount == 0) {
            credit.isRetired = true;
            _removeFromAvailableCredits(_creditId);
        }
        
        // Transfer funds
        payable(credit.issuer).transfer(issuerAmount);
        if (platformFeeAmount > 0) {
            payable(owner()).transfer(platformFeeAmount);
        }
        
        // Refund excess payment
        if (msg.value > totalPrice) {
            payable(msg.sender).transfer(msg.value - totalPrice);
        }
        
        emit CarbonCreditRetired(_creditId, msg.sender, _amount);
    }
    
    // ============ HYDROGEN TRADING ============
    
    function createHydrogenOrder(
        uint256 _amount,
        uint256 _pricePerKg,
        uint8 _purity,
        string memory _productionMethod,
        uint256 _deliveryDate,
        string memory _deliveryLocation
    ) external onlyRegisteredProducer onlyVerifiedProducer returns (uint256) {
        require(_amount > 0, "Amount must be greater than 0");
        require(_pricePerKg > 0, "Price must be greater than 0");
        require(_purity >= 950, "Purity must be at least 95%"); // 95.0%
        require(_deliveryDate > block.timestamp, "Delivery date must be in the future");
        
        _hydrogenOrderCounter.increment();
        uint256 orderId = _hydrogenOrderCounter.current();
        
        hydrogenOrders[orderId] = HydrogenOrder({
            id: orderId,
            producer: msg.sender,
            amount: _amount,
            pricePerKg: _pricePerKg,
            purity: _purity,
            productionMethod: _productionMethod,
            deliveryDate: _deliveryDate,
            deliveryLocation: _deliveryLocation,
            isActive: true,
            isFulfilled: false,
            buyer: address(0)
        });
        
        activeHydrogenOrders.push(orderId);
        
        emit HydrogenOrderCreated(orderId, msg.sender, _amount, _purity);
        
        return orderId;
    }
    
    function purchaseHydrogenOrder(uint256 _orderId) external payable nonReentrant {
        HydrogenOrder storage order = hydrogenOrders[_orderId];
        require(order.isActive, "Order is not active");
        require(order.buyer == address(0), "Order already purchased");
        
        uint256 totalPrice = order.amount * order.pricePerKg;
        uint256 platformFeeAmount = (totalPrice * platformFee) / 10000;
        uint256 producerAmount = totalPrice - platformFeeAmount;
        
        require(msg.value >= totalPrice, "Insufficient payment");
        
        // Update order
        order.buyer = msg.sender;
        order.isActive = false;
        order.isFulfilled = true;
        
        // Transfer funds
        payable(order.producer).transfer(producerAmount);
        if (platformFeeAmount > 0) {
            payable(owner()).transfer(platformFeeAmount);
        }
        
        // Refund excess payment
        if (msg.value > totalPrice) {
            payable(msg.sender).transfer(msg.value - totalPrice);
        }
        
        // Remove from active orders
        _removeFromActiveHydrogenOrders(_orderId);
        
        emit HydrogenOrderFulfilled(_orderId, msg.sender, order.amount);
    }
    
    // ============ COOPERATION PROTOCOLS ============
    
    function establishEnergyCooperation(
        address _partnerProducer,
        uint256 _sharedCapacity
    ) external onlyRegisteredProducer onlyVerifiedProducer {
        require(isRegisteredProducer[_partnerProducer], "Partner must be registered");
        require(energyProducers[_partnerProducer].isVerified, "Partner must be verified");
        require(_sharedCapacity > 0, "Shared capacity must be greater than 0");
        require(energyProducers[msg.sender].availableCapacity >= _sharedCapacity, "Insufficient capacity");
        
        // This would implement energy sharing agreements
        // For now, we'll just emit an event
        emit EnergyCooperationEstablished(msg.sender, _partnerProducer, _sharedCapacity);
    }
    
    // ============ UTILITY FUNCTIONS ============
    
    function _removeFromActiveOrders(uint256 _orderId) private {
        for (uint256 i = 0; i < activeEnergyOrders.length; i++) {
            if (activeEnergyOrders[i] == _orderId) {
                activeEnergyOrders[i] = activeEnergyOrders[activeEnergyOrders.length - 1];
                activeEnergyOrders.pop();
                break;
            }
        }
    }
    
    function _removeFromAvailableCredits(uint256 _creditId) private {
        for (uint256 i = 0; i < availableCarbonCredits.length; i++) {
            if (availableCarbonCredits[i] == _creditId) {
                availableCarbonCredits[i] = availableCarbonCredits[availableCarbonCredits.length - 1];
                availableCarbonCredits.pop();
                break;
            }
        }
    }
    
    function _removeFromActiveHydrogenOrders(uint256 _orderId) private {
        for (uint256 i = 0; i < activeHydrogenOrders.length; i++) {
            if (activeHydrogenOrders[i] == _orderId) {
                activeHydrogenOrders[i] = activeHydrogenOrders[activeHydrogenOrders.length - 1];
                activeHydrogenOrders.pop();
                break;
            }
        }
    }
    
    // ============ VIEW FUNCTIONS ============
    
    function getActiveEnergyOrders() external view returns (uint256[] memory) {
        return activeEnergyOrders;
    }
    
    function getAvailableCarbonCredits() external view returns (uint256[] memory) {
        return availableCarbonCredits;
    }
    
    function getActiveHydrogenOrders() external view returns (uint256[] memory) {
        return activeHydrogenOrders;
    }
    
    function getProducerCount() external view returns (uint256) {
        return registeredProducers.length;
    }
    
    function getEnergyOrderDetails(uint256 _orderId) external view returns (
        address producer,
        uint256 energyType,
        uint256 amount,
        uint256 pricePerMWh,
        uint256 deliveryDate,
        string memory deliveryLocation,
        bool isActive,
        bool isFulfilled
    ) {
        EnergyOrder storage order = energyOrders[_orderId];
        return (
            order.producer,
            order.energyType,
            order.amount,
            order.pricePerMWh,
            order.deliveryDate,
            order.deliveryLocation,
            order.isActive,
            order.isFulfilled
        );
    }
    
    // ============ ADMIN FUNCTIONS ============
    
    function setPlatformFee(uint256 _newFee) external onlyOwner {
        require(_newFee <= MAX_PLATFORM_FEE, "Fee too high");
        platformFee = _newFee;
    }
    
    function withdrawPlatformFees() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}
