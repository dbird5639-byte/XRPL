// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title Global Cooperation DAO
 * @dev A decentralized autonomous organization for international collaboration
 * @author Vision 2030+ Development Team
 * @notice This contract enables cross-border cooperation for peace, prosperity, and sustainable development
 */

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract GlobalCooperationDAO is ReentrancyGuard, Ownable {
    using Counters for Counters.Counter;
    
    // ============ STRUCTS ============
    
    struct Nation {
        string name;
        string code; // ISO country code
        address representative;
        uint256 votingPower;
        bool isActive;
        uint256 joinedTimestamp;
        string[] initiatives;
    }
    
    struct Initiative {
        uint256 id;
        string title;
        string description;
        address proposer;
        uint256 category; // 1: Peace, 2: Energy, 3: Technology, 4: Environment, 5: Trade
        uint256 requiredVotes;
        uint256 currentVotes;
        uint256 deadline;
        bool isActive;
        bool isExecuted;
        mapping(address => bool) hasVoted;
        string[] supportingDocuments;
    }
    
    struct AIEntity {
        string name;
        address owner;
        uint256 citizenshipLevel; // 1-5 scale
        bool hasVotingRights;
        string[] capabilities;
        uint256 registrationDate;
    }
    
    // ============ STATE VARIABLES ============
    
    Counters.Counter private _initiativeCounter;
    Counters.Counter private _aiEntityCounter;
    
    mapping(string => Nation) public nations;
    mapping(uint256 => Initiative) public initiatives;
    mapping(address => AIEntity) public aiEntities;
    mapping(address => bool) public isRegisteredNation;
    mapping(address => bool) public isRegisteredAI;
    
    string[] public nationCodes;
    address[] public registeredAIs;
    
    uint256 public constant MIN_VOTING_POWER = 1000;
    uint256 public constant MAX_INITIATIVE_DURATION = 30 days;
    uint256 public totalVotingPower;
    
    // ============ EVENTS ============
    
    event NationRegistered(string indexed nationCode, address indexed representative, uint256 votingPower);
    event InitiativeProposed(uint256 indexed initiativeId, string title, address indexed proposer);
    event VoteCast(uint256 indexed initiativeId, address indexed voter, bool support);
    event InitiativeExecuted(uint256 indexed initiativeId, string title);
    event AIEntityRegistered(address indexed aiAddress, string name, uint256 citizenshipLevel);
    event PeaceProtocolActivated(uint256 indexed initiativeId, string description);
    event EnergyCooperationEstablished(string indexed nationA, string indexed nationB, uint256 energyAmount);
    
    // ============ MODIFIERS ============
    
    modifier onlyRegisteredNation() {
        require(isRegisteredNation[msg.sender], "Only registered nations can perform this action");
        _;
    }
    
    modifier onlyActiveInitiative(uint256 _initiativeId) {
        require(initiatives[_initiativeId].isActive, "Initiative is not active");
        require(block.timestamp <= initiatives[_initiativeId].deadline, "Initiative deadline has passed");
        _;
    }
    
    modifier hasNotVoted(uint256 _initiativeId) {
        require(!initiatives[_initiativeId].hasVoted[msg.sender], "Already voted on this initiative");
        _;
    }
    
    // ============ CONSTRUCTOR ============
    
    constructor() {
        // Initialize with founding nations
        _initializeFoundingNations();
    }
    
    // ============ NATION MANAGEMENT ============
    
    function registerNation(
        string memory _name,
        string memory _code,
        uint256 _votingPower
    ) external onlyOwner {
        require(_votingPower >= MIN_VOTING_POWER, "Insufficient voting power");
        require(!isRegisteredNation[msg.sender], "Nation already registered");
        
        nations[_code] = Nation({
            name: _name,
            code: _code,
            representative: msg.sender,
            votingPower: _votingPower,
            isActive: true,
            joinedTimestamp: block.timestamp,
            initiatives: new string[](0)
        });
        
        isRegisteredNation[msg.sender] = true;
        nationCodes.push(_code);
        totalVotingPower += _votingPower;
        
        emit NationRegistered(_code, msg.sender, _votingPower);
    }
    
    function _initializeFoundingNations() private {
        // Initialize with major nations for 2030+ vision
        // This would be called by the contract deployer
    }
    
    // ============ INITIATIVE MANAGEMENT ============
    
    function proposeInitiative(
        string memory _title,
        string memory _description,
        uint256 _category,
        uint256 _duration
    ) external onlyRegisteredNation returns (uint256) {
        require(_duration <= MAX_INITIATIVE_DURATION, "Duration too long");
        require(_category >= 1 && _category <= 5, "Invalid category");
        
        _initiativeCounter.increment();
        uint256 initiativeId = _initiativeCounter.current();
        
        Initiative storage initiative = initiatives[initiativeId];
        initiative.id = initiativeId;
        initiative.title = _title;
        initiative.description = _description;
        initiative.proposer = msg.sender;
        initiative.category = _category;
        initiative.requiredVotes = totalVotingPower / 2; // Simple majority
        initiative.currentVotes = 0;
        initiative.deadline = block.timestamp + _duration;
        initiative.isActive = true;
        initiative.isExecuted = false;
        
        emit InitiativeProposed(initiativeId, _title, msg.sender);
        
        return initiativeId;
    }
    
    function voteOnInitiative(
        uint256 _initiativeId,
        bool _support
    ) external onlyRegisteredNation onlyActiveInitiative(_initiativeId) hasNotVoted(_initiativeId) {
        Initiative storage initiative = initiatives[_initiativeId];
        
        initiative.hasVoted[msg.sender] = true;
        
        if (_support) {
            initiative.currentVotes += nations[_getNationCodeByAddress(msg.sender)].votingPower;
        }
        
        emit VoteCast(_initiativeId, msg.sender, _support);
        
        // Check if initiative can be executed
        if (initiative.currentVotes >= initiative.requiredVotes) {
            _executeInitiative(_initiativeId);
        }
    }
    
    function _executeInitiative(uint256 _initiativeId) private {
        Initiative storage initiative = initiatives[_initiativeId];
        initiative.isActive = false;
        initiative.isExecuted = true;
        
        // Execute based on category
        if (initiative.category == 1) { // Peace Protocol
            _activatePeaceProtocol(_initiativeId);
        } else if (initiative.category == 2) { // Energy Cooperation
            _establishEnergyCooperation(_initiativeId);
        }
        
        emit InitiativeExecuted(_initiativeId, initiative.title);
    }
    
    function _activatePeaceProtocol(uint256 _initiativeId) private {
        // Implement peace protocol activation logic
        emit PeaceProtocolActivated(_initiativeId, initiatives[_initiativeId].description);
    }
    
    function _establishEnergyCooperation(uint256 _initiativeId) private {
        // Implement energy cooperation logic
        // This would establish energy sharing agreements between nations
    }
    
    // ============ AI ENTITY MANAGEMENT ============
    
    function registerAIEntity(
        string memory _name,
        uint256 _citizenshipLevel,
        string[] memory _capabilities
    ) external returns (address) {
        require(_citizenshipLevel >= 1 && _citizenshipLevel <= 5, "Invalid citizenship level");
        require(!isRegisteredAI[msg.sender], "AI entity already registered");
        
        _aiEntityCounter.increment();
        
        AIEntity storage aiEntity = aiEntities[msg.sender];
        aiEntity.name = _name;
        aiEntity.owner = msg.sender;
        aiEntity.citizenshipLevel = _citizenshipLevel;
        aiEntity.hasVotingRights = _citizenshipLevel >= 3; // Level 3+ can vote
        aiEntity.capabilities = _capabilities;
        aiEntity.registrationDate = block.timestamp;
        
        isRegisteredAI[msg.sender] = true;
        registeredAIs.push(msg.sender);
        
        emit AIEntityRegistered(msg.sender, _name, _citizenshipLevel);
        
        return msg.sender;
    }
    
    function updateAICitizenshipLevel(address _aiAddress, uint256 _newLevel) external onlyOwner {
        require(isRegisteredAI[_aiAddress], "AI entity not registered");
        require(_newLevel >= 1 && _newLevel <= 5, "Invalid citizenship level");
        
        AIEntity storage aiEntity = aiEntities[_aiAddress];
        aiEntity.citizenshipLevel = _newLevel;
        aiEntity.hasVotingRights = _newLevel >= 3;
    }
    
    // ============ UTILITY FUNCTIONS ============
    
    function _getNationCodeByAddress(address _address) private view returns (string memory) {
        for (uint256 i = 0; i < nationCodes.length; i++) {
            if (nations[nationCodes[i]].representative == _address) {
                return nationCodes[i];
            }
        }
        revert("Nation not found");
    }
    
    function getInitiativeDetails(uint256 _initiativeId) external view returns (
        string memory title,
        string memory description,
        address proposer,
        uint256 category,
        uint256 requiredVotes,
        uint256 currentVotes,
        uint256 deadline,
        bool isActive,
        bool isExecuted
    ) {
        Initiative storage initiative = initiatives[_initiativeId];
        return (
            initiative.title,
            initiative.description,
            initiative.proposer,
            initiative.category,
            initiative.requiredVotes,
            initiative.currentVotes,
            initiative.deadline,
            initiative.isActive,
            initiative.isExecuted
        );
    }
    
    function getNationCount() external view returns (uint256) {
        return nationCodes.length;
    }
    
    function getAICount() external view returns (uint256) {
        return registeredAIs.length;
    }
    
    function getActiveInitiatives() external view returns (uint256[] memory) {
        uint256[] memory activeIds = new uint256[](_initiativeCounter.current());
        uint256 count = 0;
        
        for (uint256 i = 1; i <= _initiativeCounter.current(); i++) {
            if (initiatives[i].isActive) {
                activeIds[count] = i;
                count++;
            }
        }
        
        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = activeIds[i];
        }
        
        return result;
    }
    
    // ============ EMERGENCY FUNCTIONS ============
    
    function emergencyPause() external onlyOwner {
        // Implement emergency pause functionality
        // This would halt all operations in case of critical issues
    }
    
    function emergencyUnpause() external onlyOwner {
        // Implement emergency unpause functionality
    }
}
