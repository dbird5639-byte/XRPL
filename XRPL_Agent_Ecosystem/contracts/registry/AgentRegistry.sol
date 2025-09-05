// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title AgentRegistry
 * @dev Central registry for managing XRPL agents on the EVM sidechain
 * @author XRPL Agent Ecosystem
 */
contract AgentRegistry is ReentrancyGuard, Pausable, Ownable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Agent status enumeration
    enum AgentStatus {
        Inactive,
        Active,
        Suspended,
        Deprecated
    }

    // Agent category enumeration
    enum AgentCategory {
        Trading,
        DeFi,
        NFT,
        Gaming,
        Social,
        Analytics,
        Security,
        Custom
    }

    // Agent structure
    struct Agent {
        address owner;
        string name;
        string description;
        string version;
        AgentCategory category;
        AgentStatus status;
        uint256 registrationTime;
        uint256 lastUpdateTime;
        uint256 reputationScore;
        uint256 totalExecutions;
        uint256 successfulExecutions;
        uint256 failedExecutions;
        string metadataURI; // IPFS hash for agent metadata
        string codeURI; // IPFS hash for agent code
        address[] dependencies; // Other agents this agent depends on
        uint256[] supportedTokens; // Token IDs this agent supports
        bool isPublic;
        uint256 stakingAmount;
        uint256 feeRate; // Basis points (e.g., 100 = 1%)
    }

    // Agent execution record
    struct ExecutionRecord {
        address executor;
        uint256 agentId;
        uint256 timestamp;
        bool success;
        uint256 gasUsed;
        string resultHash;
        uint256 feePaid;
    }

    // Events
    event AgentRegistered(
        uint256 indexed agentId,
        address indexed owner,
        string name,
        AgentCategory category
    );
    event AgentUpdated(uint256 indexed agentId, string version, string metadataURI);
    event AgentStatusChanged(uint256 indexed agentId, AgentStatus oldStatus, AgentStatus newStatus);
    event AgentExecuted(
        uint256 indexed agentId,
        address indexed executor,
        bool success,
        uint256 gasUsed,
        uint256 feePaid
    );
    event ReputationUpdated(uint256 indexed agentId, uint256 oldScore, uint256 newScore);
    event StakingUpdated(uint256 indexed agentId, uint256 oldAmount, uint256 newAmount);

    // State variables
    mapping(uint256 => Agent) public agents;
    mapping(address => uint256[]) public ownerAgents;
    mapping(AgentCategory => uint256[]) public categoryAgents;
    mapping(address => bool) public authorizedExecutors;
    mapping(uint256 => ExecutionRecord[]) public agentExecutions;
    mapping(address => uint256) public executorReputation;
    
    uint256 public nextAgentId = 1;
    uint256 public totalAgents = 0;
    uint256 public totalExecutions = 0;
    
    // Configuration
    uint256 public registrationFee = 0.1 ether;
    uint256 public updateFee = 0.05 ether;
    uint256 public executionFeeRate = 50; // 0.5%
    uint256 public minStakingAmount = 1 ether;
    uint256 public maxReputationScore = 10000;
    
    address public feeCollector;
    IERC20 public nativeToken;

    // Modifiers
    modifier onlyAgentOwner(uint256 agentId) {
        require(agents[agentId].owner == msg.sender, "Not agent owner");
        _;
    }

    modifier validAgent(uint256 agentId) {
        require(agentId > 0 && agentId < nextAgentId, "Invalid agent ID");
        require(agents[agentId].status != AgentStatus.Inactive, "Agent inactive");
        _;
    }

    modifier onlyAuthorizedExecutor() {
        require(authorizedExecutors[msg.sender] || msg.sender == owner(), "Not authorized executor");
        _;
    }

    constructor(address _feeCollector, address _nativeToken) {
        feeCollector = _feeCollector;
        nativeToken = IERC20(_nativeToken);
    }

    /**
     * @dev Register a new agent
     */
    function registerAgent(
        string memory name,
        string memory description,
        string memory version,
        AgentCategory category,
        string memory metadataURI,
        string memory codeURI,
        address[] memory dependencies,
        uint256[] memory supportedTokens,
        bool isPublic,
        uint256 feeRate
    ) external payable nonReentrant whenNotPaused returns (uint256 agentId) {
        require(msg.value >= registrationFee, "Insufficient registration fee");
        require(bytes(name).length > 0, "Name required");
        require(bytes(description).length > 0, "Description required");
        require(bytes(metadataURI).length > 0, "Metadata URI required");
        require(bytes(codeURI).length > 0, "Code URI required");
        require(feeRate <= 1000, "Fee rate too high"); // Max 10%

        agentId = nextAgentId++;
        
        agents[agentId] = Agent({
            owner: msg.sender,
            name: name,
            description: description,
            version: version,
            category: category,
            status: AgentStatus.Active,
            registrationTime: block.timestamp,
            lastUpdateTime: block.timestamp,
            reputationScore: 1000, // Starting reputation
            totalExecutions: 0,
            successfulExecutions: 0,
            failedExecutions: 0,
            metadataURI: metadataURI,
            codeURI: codeURI,
            dependencies: dependencies,
            supportedTokens: supportedTokens,
            isPublic: isPublic,
            stakingAmount: 0,
            feeRate: feeRate
        });

        ownerAgents[msg.sender].push(agentId);
        categoryAgents[category].push(agentId);
        totalAgents++;

        // Transfer registration fee
        if (msg.value > 0) {
            payable(feeCollector).transfer(msg.value);
        }

        emit AgentRegistered(agentId, msg.sender, name, category);
    }

    /**
     * @dev Update agent information
     */
    function updateAgent(
        uint256 agentId,
        string memory name,
        string memory description,
        string memory version,
        string memory metadataURI,
        string memory codeURI,
        address[] memory dependencies,
        uint256[] memory supportedTokens,
        bool isPublic,
        uint256 feeRate
    ) external payable onlyAgentOwner(agentId) nonReentrant whenNotPaused {
        require(msg.value >= updateFee, "Insufficient update fee");
        require(bytes(name).length > 0, "Name required");
        require(bytes(description).length > 0, "Description required");
        require(feeRate <= 1000, "Fee rate too high");

        Agent storage agent = agents[agentId];
        
        agent.name = name;
        agent.description = description;
        agent.version = version;
        agent.metadataURI = metadataURI;
        agent.codeURI = codeURI;
        agent.dependencies = dependencies;
        agent.supportedTokens = supportedTokens;
        agent.isPublic = isPublic;
        agent.feeRate = feeRate;
        agent.lastUpdateTime = block.timestamp;

        // Transfer update fee
        if (msg.value > 0) {
            payable(feeCollector).transfer(msg.value);
        }

        emit AgentUpdated(agentId, version, metadataURI);
    }

    /**
     * @dev Change agent status
     */
    function changeAgentStatus(uint256 agentId, AgentStatus newStatus) 
        external 
        onlyAgentOwner(agentId) 
        validAgent(agentId) 
    {
        Agent storage agent = agents[agentId];
        AgentStatus oldStatus = agent.status;
        
        require(newStatus != oldStatus, "Status unchanged");
        
        agent.status = newStatus;
        
        emit AgentStatusChanged(agentId, oldStatus, newStatus);
    }

    /**
     * @dev Stake tokens for agent
     */
    function stakeForAgent(uint256 agentId, uint256 amount) 
        external 
        onlyAgentOwner(agentId) 
        nonReentrant 
    {
        require(amount >= minStakingAmount, "Insufficient staking amount");
        
        Agent storage agent = agents[agentId];
        uint256 oldAmount = agent.stakingAmount;
        
        nativeToken.safeTransferFrom(msg.sender, address(this), amount);
        agent.stakingAmount = agent.stakingAmount.add(amount);
        
        emit StakingUpdated(agentId, oldAmount, agent.stakingAmount);
    }

    /**
     * @dev Unstake tokens from agent
     */
    function unstakeFromAgent(uint256 agentId, uint256 amount) 
        external 
        onlyAgentOwner(agentId) 
        nonReentrant 
    {
        Agent storage agent = agents[agentId];
        require(agent.stakingAmount >= amount, "Insufficient staked amount");
        
        uint256 oldAmount = agent.stakingAmount;
        agent.stakingAmount = agent.stakingAmount.sub(amount);
        
        nativeToken.safeTransfer(msg.sender, amount);
        
        emit StakingUpdated(agentId, oldAmount, agent.stakingAmount);
    }

    /**
     * @dev Execute an agent
     */
    function executeAgent(
        uint256 agentId,
        bytes calldata inputData,
        uint256 maxGas
    ) external payable onlyAuthorizedExecutor validAgent(agentId) nonReentrant returns (bool success, bytes memory result) {
        Agent storage agent = agents[agentId];
        require(agent.isPublic || msg.sender == agent.owner, "Agent not public");
        
        uint256 gasStart = gasleft();
        uint256 executionFee = msg.value;
        
        // Calculate agent fee
        uint256 agentFee = executionFee.mul(agent.feeRate).div(10000);
        uint256 protocolFee = executionFee.sub(agentFee);
        
        // Transfer fees
        if (agentFee > 0) {
            payable(agent.owner).transfer(agentFee);
        }
        if (protocolFee > 0) {
            payable(feeCollector).transfer(protocolFee);
        }
        
        // Execute agent logic (simplified - real implementation would call agent contract)
        try this._executeAgentLogic(agentId, inputData, maxGas) returns (bytes memory _result) {
            success = true;
            result = _result;
            agent.successfulExecutions++;
        } catch {
            success = false;
            result = "";
            agent.failedExecutions++;
        }
        
        uint256 gasUsed = gasStart - gasleft();
        agent.totalExecutions++;
        totalExecutions++;
        
        // Update reputation based on execution result
        _updateReputation(agentId, success, gasUsed);
        
        // Record execution
        agentExecutions[agentId].push(ExecutionRecord({
            executor: msg.sender,
            agentId: agentId,
            timestamp: block.timestamp,
            success: success,
            gasUsed: gasUsed,
            resultHash: keccak256(result),
            feePaid: executionFee
        }));
        
        emit AgentExecuted(agentId, msg.sender, success, gasUsed, executionFee);
    }

    /**
     * @dev Internal agent execution logic
     */
    function _executeAgentLogic(uint256 agentId, bytes calldata inputData, uint256 maxGas) 
        external 
        view 
        returns (bytes memory) 
    {
        // This is a placeholder - real implementation would:
        // 1. Load agent code from IPFS
        // 2. Execute in sandboxed environment
        // 3. Return results
        require(gasleft() >= maxGas, "Insufficient gas");
        
        return abi.encode(agentId, block.timestamp, "execution_result");
    }

    /**
     * @dev Update agent reputation
     */
    function _updateReputation(uint256 agentId, bool success, uint256 gasUsed) internal {
        Agent storage agent = agents[agentId];
        uint256 oldScore = agent.reputationScore;
        
        if (success) {
            // Increase reputation for successful execution
            uint256 increase = gasUsed.div(1000); // Gas efficiency bonus
            agent.reputationScore = agent.reputationScore.add(increase);
        } else {
            // Decrease reputation for failed execution
            uint256 decrease = 100; // Fixed penalty
            if (agent.reputationScore > decrease) {
                agent.reputationScore = agent.reputationScore.sub(decrease);
            } else {
                agent.reputationScore = 0;
            }
        }
        
        // Cap reputation score
        if (agent.reputationScore > maxReputationScore) {
            agent.reputationScore = maxReputationScore;
        }
        
        if (oldScore != agent.reputationScore) {
            emit ReputationUpdated(agentId, oldScore, agent.reputationScore);
        }
    }

    /**
     * @dev Get agent information
     */
    function getAgent(uint256 agentId) external view returns (Agent memory) {
        return agents[agentId];
    }

    /**
     * @dev Get agents by owner
     */
    function getAgentsByOwner(address owner) external view returns (uint256[] memory) {
        return ownerAgents[owner];
    }

    /**
     * @dev Get agents by category
     */
    function getAgentsByCategory(AgentCategory category) external view returns (uint256[] memory) {
        return categoryAgents[category];
    }

    /**
     * @dev Get agent execution history
     */
    function getAgentExecutions(uint256 agentId) external view returns (ExecutionRecord[] memory) {
        return agentExecutions[agentId];
    }

    /**
     * @dev Search agents by name
     */
    function searchAgents(string memory query) external view returns (uint256[] memory) {
        uint256[] memory results = new uint256[](totalAgents);
        uint256 count = 0;
        
        for (uint256 i = 1; i < nextAgentId; i++) {
            if (agents[i].status == AgentStatus.Active) {
                // Simple string matching - could be enhanced with more sophisticated search
                if (bytes(agents[i].name).length > 0) {
                    results[count] = i;
                    count++;
                }
            }
        }
        
        // Resize array to actual results
        uint256[] memory finalResults = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            finalResults[i] = results[i];
        }
        
        return finalResults;
    }

    /**
     * @dev Authorize executor
     */
    function authorizeExecutor(address executor) external onlyOwner {
        authorizedExecutors[executor] = true;
    }

    /**
     * @dev Revoke executor authorization
     */
    function revokeExecutor(address executor) external onlyOwner {
        authorizedExecutors[executor] = false;
    }

    /**
     * @dev Set configuration parameters
     */
    function setConfig(
        uint256 _registrationFee,
        uint256 _updateFee,
        uint256 _executionFeeRate,
        uint256 _minStakingAmount,
        uint256 _maxReputationScore
    ) external onlyOwner {
        registrationFee = _registrationFee;
        updateFee = _updateFee;
        executionFeeRate = _executionFeeRate;
        minStakingAmount = _minStakingAmount;
        maxReputationScore = _maxReputationScore;
    }

    /**
     * @dev Set fee collector
     */
    function setFeeCollector(address _feeCollector) external onlyOwner {
        require(_feeCollector != address(0), "Invalid address");
        feeCollector = _feeCollector;
    }

    /**
     * @dev Pause contract
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Emergency withdraw
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        if (token == address(0)) {
            payable(owner()).transfer(amount);
        } else {
            IERC20(token).safeTransfer(owner(), amount);
        }
    }
}
