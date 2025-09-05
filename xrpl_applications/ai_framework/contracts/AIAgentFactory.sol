// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AIAgentFactory
 * @dev Factory for creating and managing AI agents with custom datasets
 */
contract AIAgentFactory is Ownable, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    // Events
    event AgentCreated(uint256 indexed agentId, address indexed creator, string name, string purpose);
    event DatasetAdded(uint256 indexed agentId, uint256 indexed datasetId, address indexed owner);
    event DatasetRemoved(uint256 indexed agentId, uint256 indexed datasetId, address indexed owner);
    event AgentDeployed(uint256 indexed agentId, address indexed agentAddress);
    event AgentUpdated(uint256 indexed agentId, string newConfiguration);
    event AgentDestroyed(uint256 indexed agentId, address indexed owner);
    
    // Structs
    struct AIAgent {
        uint256 id;
        address creator;
        string name;
        string description;
        string purpose;
        string configuration; // JSON configuration
        uint256[] datasetIds;
        address agentAddress;
        bool isDeployed;
        bool isActive;
        uint256 creationTime;
        uint256 lastUpdateTime;
        uint256 usageCount;
        uint256 totalRevenue;
    }
    
    struct DatasetAccess {
        uint256 datasetId;
        uint256 accessLevel; // 0=read, 1=write, 2=admin
        uint256 addedTime;
        bool isActive;
    }
    
    // State variables
    Counters.Counter private _agentIds;
    mapping(uint256 => AIAgent) public agents;
    mapping(address => uint256[]) public userAgents;
    mapping(uint256 => mapping(uint256 => DatasetAccess)) public agentDatasets;
    mapping(address => bool) public authorizedDatasets;
    
    IERC20 public xrpToken;
    AIDatasetMarketplace public datasetMarketplace;
    
    uint256 public agentCreationFee = 50 * 10**6; // 50 XRP
    uint256 public datasetAccessFee = 10 * 10**6; // 10 XRP per dataset
    uint256 public deploymentFee = 100 * 10**6; // 100 XRP for deployment
    
    // Agent limits
    uint256 public maxDatasetsPerAgent = 10;
    uint256 public maxAgentsPerUser = 5;
    
    constructor(address _xrpToken, address _datasetMarketplace) {
        xrpToken = IERC20(_xrpToken);
        datasetMarketplace = AIDatasetMarketplace(_datasetMarketplace);
    }
    
    /**
     * @dev Create a new AI agent
     */
    function createAgent(
        string memory _name,
        string memory _description,
        string memory _purpose,
        string memory _configuration
    ) external whenNotPaused nonReentrant returns (uint256) {
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_description).length > 0, "Description cannot be empty");
        require(bytes(_purpose).length > 0, "Purpose cannot be empty");
        require(userAgents[msg.sender].length < maxAgentsPerUser, "Max agents per user exceeded");
        
        // Pay creation fee
        require(xrpToken.transferFrom(msg.sender, address(this), agentCreationFee), "Creation fee payment failed");
        
        _agentIds.increment();
        uint256 agentId = _agentIds.current();
        
        agents[agentId] = AIAgent({
            id: agentId,
            creator: msg.sender,
            name: _name,
            description: _description,
            purpose: _purpose,
            configuration: _configuration,
            datasetIds: new uint256[](0),
            agentAddress: address(0),
            isDeployed: false,
            isActive: true,
            creationTime: block.timestamp,
            lastUpdateTime: block.timestamp,
            usageCount: 0,
            totalRevenue: 0
        });
        
        userAgents[msg.sender].push(agentId);
        
        emit AgentCreated(agentId, msg.sender, _name, _purpose);
        return agentId;
    }
    
    /**
     * @dev Add a dataset to an agent
     */
    function addDatasetToAgent(
        uint256 _agentId,
        uint256 _datasetId,
        uint256 _accessLevel
    ) external whenNotPaused nonReentrant {
        require(_agentId > 0 && _agentId <= _agentIds.current(), "Invalid agent ID");
        require(_accessLevel <= 2, "Invalid access level");
        
        AIAgent storage agent = agents[_agentId];
        require(agent.creator == msg.sender, "Not agent creator");
        require(agent.isActive, "Agent not active");
        require(agent.datasetIds.length < maxDatasetsPerAgent, "Max datasets per agent exceeded");
        
        // Verify dataset exists and is approved
        (bool datasetExists, bool isApproved) = _verifyDataset(_datasetId);
        require(datasetExists && isApproved, "Dataset not available");
        
        // Pay dataset access fee
        require(xrpToken.transferFrom(msg.sender, address(this), datasetAccessFee), "Dataset access fee payment failed");
        
        // Add dataset to agent
        agent.datasetIds.push(_datasetId);
        agentDatasets[_agentId][_datasetId] = DatasetAccess({
            datasetId: _datasetId,
            accessLevel: _accessLevel,
            addedTime: block.timestamp,
            isActive: true
        });
        
        emit DatasetAdded(_agentId, _datasetId, msg.sender);
    }
    
    /**
     * @dev Remove a dataset from an agent
     */
    function removeDatasetFromAgent(
        uint256 _agentId,
        uint256 _datasetId
    ) external whenNotPaused {
        require(_agentId > 0 && _agentId <= _agentIds.current(), "Invalid agent ID");
        
        AIAgent storage agent = agents[_agentId];
        require(agent.creator == msg.sender, "Not agent creator");
        
        // Find and remove dataset
        for (uint256 i = 0; i < agent.datasetIds.length; i++) {
            if (agent.datasetIds[i] == _datasetId) {
                agent.datasetIds[i] = agent.datasetIds[agent.datasetIds.length - 1];
                agent.datasetIds.pop();
                break;
            }
        }
        
        // Deactivate dataset access
        agentDatasets[_agentId][_datasetId].isActive = false;
        
        emit DatasetRemoved(_agentId, _datasetId, msg.sender);
    }
    
    /**
     * @dev Deploy an agent (create smart contract instance)
     */
    function deployAgent(uint256 _agentId) external whenNotPaused nonReentrant {
        require(_agentId > 0 && _agentId <= _agentIds.current(), "Invalid agent ID");
        
        AIAgent storage agent = agents[_agentId];
        require(agent.creator == msg.sender, "Not agent creator");
        require(agent.isActive, "Agent not active");
        require(!agent.isDeployed, "Agent already deployed");
        require(agent.datasetIds.length > 0, "No datasets attached");
        
        // Pay deployment fee
        require(xrpToken.transferFrom(msg.sender, address(this), deploymentFee), "Deployment fee payment failed");
        
        // Deploy agent contract (simplified - in real implementation, use CREATE2)
        address agentAddress = address(new AIAgentContract(_agentId, address(this)));
        agent.agentAddress = agentAddress;
        agent.isDeployed = true;
        
        emit AgentDeployed(_agentId, agentAddress);
    }
    
    /**
     * @dev Update agent configuration
     */
    function updateAgentConfiguration(
        uint256 _agentId,
        string memory _newConfiguration
    ) external whenNotPaused {
        require(_agentId > 0 && _agentId <= _agentIds.current(), "Invalid agent ID");
        
        AIAgent storage agent = agents[_agentId];
        require(agent.creator == msg.sender, "Not agent creator");
        require(agent.isActive, "Agent not active");
        
        agent.configuration = _newConfiguration;
        agent.lastUpdateTime = block.timestamp;
        
        emit AgentUpdated(_agentId, _newConfiguration);
    }
    
    /**
     * @dev Destroy an agent
     */
    function destroyAgent(uint256 _agentId) external whenNotPaused {
        require(_agentId > 0 && _agentId <= _agentIds.current(), "Invalid agent ID");
        
        AIAgent storage agent = agents[_agentId];
        require(agent.creator == msg.sender, "Not agent creator");
        
        agent.isActive = false;
        
        // Remove from user's agent list
        for (uint256 i = 0; i < userAgents[msg.sender].length; i++) {
            if (userAgents[msg.sender][i] == _agentId) {
                userAgents[msg.sender][i] = userAgents[msg.sender][userAgents[msg.sender].length - 1];
                userAgents[msg.sender].pop();
                break;
            }
        }
        
        emit AgentDestroyed(_agentId, msg.sender);
    }
    
    /**
     * @dev Get agent details
     */
    function getAgent(uint256 _agentId) external view returns (AIAgent memory) {
        require(_agentId > 0 && _agentId <= _agentIds.current(), "Invalid agent ID");
        return agents[_agentId];
    }
    
    /**
     * @dev Get agent's datasets
     */
    function getAgentDatasets(uint256 _agentId) external view returns (uint256[] memory) {
        require(_agentId > 0 && _agentId <= _agentIds.current(), "Invalid agent ID");
        return agents[_agentId].datasetIds;
    }
    
    /**
     * @dev Get user's agents
     */
    function getUserAgents(address _user) external view returns (uint256[] memory) {
        return userAgents[_user];
    }
    
    /**
     * @dev Get total number of agents
     */
    function getTotalAgents() external view returns (uint256) {
        return _agentIds.current();
    }
    
    // Internal functions
    function _verifyDataset(uint256 _datasetId) internal view returns (bool exists, bool approved) {
        try datasetMarketplace.getDataset(_datasetId) returns (AIDatasetMarketplace.Dataset memory dataset) {
            exists = true;
            approved = (dataset.status == AIDatasetMarketplace.ApprovalStatus.Approved && dataset.isActive);
        } catch {
            exists = false;
            approved = false;
        }
    }
    
    // Admin functions
    function setFees(uint256 _creationFee, uint256 _accessFee, uint256 _deploymentFee) external onlyOwner {
        agentCreationFee = _creationFee;
        datasetAccessFee = _accessFee;
        deploymentFee = _deploymentFee;
    }
    
    function setLimits(uint256 _maxDatasets, uint256 _maxAgents) external onlyOwner {
        maxDatasetsPerAgent = _maxDatasets;
        maxAgentsPerUser = _maxAgents;
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function withdrawFees() external onlyOwner {
        uint256 balance = xrpToken.balanceOf(address(this));
        require(balance > 0, "No fees to withdraw");
        require(xrpToken.transfer(owner(), balance), "Transfer failed");
    }
}

/**
 * @title AIAgentContract
 * @dev Individual AI agent contract instance
 */
contract AIAgentContract {
    uint256 public agentId;
    address public factory;
    address public owner;
    
    mapping(address => bool) public authorizedUsers;
    uint256 public usageCount;
    uint256 public totalRevenue;
    
    event AgentUsed(address indexed user, string query, uint256 timestamp);
    event RevenueGenerated(uint256 amount, address indexed user);
    
    constructor(uint256 _agentId, address _factory) {
        agentId = _agentId;
        factory = _factory;
        owner = AIAgentFactory(_factory).agents(_agentId).creator;
        authorizedUsers[owner] = true;
    }
    
    function useAgent(string memory _query) external {
        require(authorizedUsers[msg.sender], "Not authorized");
        
        usageCount++;
        emit AgentUsed(msg.sender, _query, block.timestamp);
    }
    
    function addAuthorizedUser(address _user) external {
        require(msg.sender == owner, "Not owner");
        authorizedUsers[_user] = true;
    }
    
    function removeAuthorizedUser(address _user) external {
        require(msg.sender == owner, "Not owner");
        authorizedUsers[_user] = false;
    }
    
    function generateRevenue(uint256 _amount) external {
        require(msg.sender == factory, "Not factory");
        totalRevenue += _amount;
        emit RevenueGenerated(_amount, owner);
    }
}
