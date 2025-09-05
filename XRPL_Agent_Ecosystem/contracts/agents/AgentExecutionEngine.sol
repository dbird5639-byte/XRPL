// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../registry/AgentRegistry.sol";

/**
 * @title AgentExecutionEngine
 * @dev Advanced execution engine for XRPL agents with sandboxing and resource management
 * @author XRPL Agent Ecosystem
 */
contract AgentExecutionEngine is ReentrancyGuard, Pausable, Ownable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Execution environment structure
    struct ExecutionEnvironment {
        uint256 maxGas;
        uint256 maxMemory;
        uint256 maxStorage;
        uint256 timeout;
        bool allowExternalCalls;
        bool allowStateChanges;
        address[] allowedContracts;
        uint256[] allowedTokens;
    }

    // Agent execution context
    struct ExecutionContext {
        uint256 agentId;
        address executor;
        uint256 startTime;
        uint256 gasLimit;
        uint256 memoryLimit;
        uint256 storageLimit;
        mapping(string => bytes) variables;
        mapping(address => uint256) tokenBalances;
        mapping(address => bool) contractAccess;
        bool isActive;
    }

    // Execution result structure
    struct ExecutionResult {
        bool success;
        bytes returnData;
        uint256 gasUsed;
        uint256 memoryUsed;
        uint256 storageUsed;
        uint256 executionTime;
        string errorMessage;
        uint256[] eventsEmitted;
    }

    // Agent template structure
    struct AgentTemplate {
        string name;
        string description;
        string category;
        string codeTemplate;
        string[] requiredDependencies;
        uint256[] supportedTokens;
        ExecutionEnvironment defaultEnvironment;
        uint256 templateFee;
    }

    // Events
    event AgentExecuted(
        uint256 indexed agentId,
        address indexed executor,
        bool success,
        uint256 gasUsed,
        uint256 executionTime
    );
    event ExecutionEnvironmentCreated(
        uint256 indexed envId,
        address indexed creator,
        uint256 maxGas,
        uint256 timeout
    );
    event AgentTemplateRegistered(
        uint256 indexed templateId,
        string name,
        string category,
        uint256 templateFee
    );
    event ResourceLimitExceeded(
        uint256 indexed agentId,
        string resourceType,
        uint256 limit,
        uint256 used
    );

    // State variables
    mapping(uint256 => ExecutionContext) public executionContexts;
    mapping(uint256 => ExecutionEnvironment) public executionEnvironments;
    mapping(uint256 => AgentTemplate) public agentTemplates;
    mapping(address => bool) public authorizedExecutors;
    mapping(address => bool) public authorizedOracles;
    mapping(uint256 => ExecutionResult[]) public executionHistory;
    
    AgentRegistry public agentRegistry;
    uint256 public nextEnvironmentId = 1;
    uint256 public nextTemplateId = 1;
    uint256 public totalExecutions = 0;
    
    // Configuration
    uint256 public maxExecutionTime = 300; // 5 minutes
    uint256 public maxGasPerExecution = 10_000_000;
    uint256 public maxMemoryPerExecution = 100_000_000; // 100MB
    uint256 public maxStoragePerExecution = 10_000_000; // 10MB
    uint256 public executionFeeRate = 100; // 1%
    
    address public feeCollector;
    IERC20 public nativeToken;

    // Modifiers
    modifier onlyAuthorizedExecutor() {
        require(authorizedExecutors[msg.sender] || msg.sender == owner(), "Not authorized executor");
        _;
    }

    modifier onlyAuthorizedOracle() {
        require(authorizedOracles[msg.sender] || msg.sender == owner(), "Not authorized oracle");
        _;
    }

    modifier validEnvironment(uint256 envId) {
        require(envId > 0 && envId < nextEnvironmentId, "Invalid environment ID");
        _;
    }

    constructor(
        address _agentRegistry,
        address _feeCollector,
        address _nativeToken
    ) {
        agentRegistry = AgentRegistry(_agentRegistry);
        feeCollector = _feeCollector;
        nativeToken = IERC20(_nativeToken);
    }

    /**
     * @dev Create a new execution environment
     */
    function createExecutionEnvironment(
        uint256 maxGas,
        uint256 maxMemory,
        uint256 maxStorage,
        uint256 timeout,
        bool allowExternalCalls,
        bool allowStateChanges,
        address[] memory allowedContracts,
        uint256[] memory allowedTokens
    ) external returns (uint256 envId) {
        require(maxGas <= maxGasPerExecution, "Gas limit too high");
        require(maxMemory <= maxMemoryPerExecution, "Memory limit too high");
        require(maxStorage <= maxStoragePerExecution, "Storage limit too high");
        require(timeout <= maxExecutionTime, "Timeout too high");

        envId = nextEnvironmentId++;
        
        executionEnvironments[envId] = ExecutionEnvironment({
            maxGas: maxGas,
            maxMemory: maxMemory,
            maxStorage: maxStorage,
            timeout: timeout,
            allowExternalCalls: allowExternalCalls,
            allowStateChanges: allowStateChanges,
            allowedContracts: allowedContracts,
            allowedTokens: allowedTokens
        });

        emit ExecutionEnvironmentCreated(envId, msg.sender, maxGas, timeout);
    }

    /**
     * @dev Register an agent template
     */
    function registerAgentTemplate(
        string memory name,
        string memory description,
        string memory category,
        string memory codeTemplate,
        string[] memory requiredDependencies,
        uint256[] memory supportedTokens,
        ExecutionEnvironment memory defaultEnvironment,
        uint256 templateFee
    ) external returns (uint256 templateId) {
        require(bytes(name).length > 0, "Name required");
        require(bytes(codeTemplate).length > 0, "Code template required");

        templateId = nextTemplateId++;
        
        agentTemplates[templateId] = AgentTemplate({
            name: name,
            description: description,
            category: category,
            codeTemplate: codeTemplate,
            requiredDependencies: requiredDependencies,
            supportedTokens: supportedTokens,
            defaultEnvironment: defaultEnvironment,
            templateFee: templateFee
        });

        emit AgentTemplateRegistered(templateId, name, category, templateFee);
    }

    /**
     * @dev Execute an agent with custom environment
     */
    function executeAgentWithEnvironment(
        uint256 agentId,
        uint256 environmentId,
        bytes calldata inputData,
        uint256 maxGas
    ) external payable onlyAuthorizedExecutor nonReentrant whenNotPaused returns (ExecutionResult memory) {
        require(agentRegistry.getAgent(agentId).owner != address(0), "Agent not found");
        require(environmentId > 0 && environmentId < nextEnvironmentId, "Invalid environment");
        
        ExecutionEnvironment memory env = executionEnvironments[environmentId];
        require(maxGas <= env.maxGas, "Gas limit exceeded");
        
        uint256 startTime = block.timestamp;
        uint256 gasStart = gasleft();
        
        // Create execution context
        ExecutionContext storage context = executionContexts[agentId];
        context.agentId = agentId;
        context.executor = msg.sender;
        context.startTime = startTime;
        context.gasLimit = maxGas;
        context.memoryLimit = env.maxMemory;
        context.storageLimit = env.maxStorage;
        context.isActive = true;
        
        ExecutionResult memory result;
        
        try this._executeAgentLogic(agentId, environmentId, inputData, maxGas) returns (bytes memory returnData) {
            result.success = true;
            result.returnData = returnData;
        } catch Error(string memory reason) {
            result.success = false;
            result.errorMessage = reason;
        } catch {
            result.success = false;
            result.errorMessage = "Unknown execution error";
        }
        
        uint256 gasUsed = gasStart - gasleft();
        uint256 executionTime = block.timestamp - startTime;
        
        result.gasUsed = gasUsed;
        result.executionTime = executionTime;
        result.memoryUsed = _calculateMemoryUsage(agentId);
        result.storageUsed = _calculateStorageUsage(agentId);
        
        // Check resource limits
        if (gasUsed > env.maxGas) {
            emit ResourceLimitExceeded(agentId, "gas", env.maxGas, gasUsed);
        }
        if (result.memoryUsed > env.maxMemory) {
            emit ResourceLimitExceeded(agentId, "memory", env.maxMemory, result.memoryUsed);
        }
        if (result.storageUsed > env.maxStorage) {
            emit ResourceLimitExceeded(agentId, "storage", env.maxStorage, result.storageUsed);
        }
        if (executionTime > env.timeout) {
            emit ResourceLimitExceeded(agentId, "timeout", env.timeout, executionTime);
        }
        
        // Record execution
        executionHistory[agentId].push(result);
        totalExecutions++;
        
        // Clean up context
        context.isActive = false;
        
        // Handle fees
        _handleExecutionFees(agentId, msg.value);
        
        emit AgentExecuted(agentId, msg.sender, result.success, gasUsed, executionTime);
        
        return result;
    }

    /**
     * @dev Execute agent with default environment
     */
    function executeAgent(
        uint256 agentId,
        bytes calldata inputData,
        uint256 maxGas
    ) external payable onlyAuthorizedExecutor nonReentrant whenNotPaused returns (ExecutionResult memory) {
        // Use default environment (ID 1)
        return executeAgentWithEnvironment(agentId, 1, inputData, maxGas);
    }

    /**
     * @dev Internal agent execution logic
     */
    function _executeAgentLogic(
        uint256 agentId,
        uint256 environmentId,
        bytes calldata inputData,
        uint256 maxGas
    ) external view returns (bytes memory) {
        require(executionContexts[agentId].isActive, "Context not active");
        
        ExecutionEnvironment memory env = executionEnvironments[environmentId];
        AgentRegistry.Agent memory agent = agentRegistry.getAgent(agentId);
        
        // Validate environment constraints
        require(gasleft() >= maxGas, "Insufficient gas");
        require(block.timestamp - executionContexts[agentId].startTime <= env.timeout, "Execution timeout");
        
        // Simulate agent execution based on category
        if (keccak256(bytes(agent.name)) == keccak256("TradingAgent")) {
            return _executeTradingAgent(agentId, inputData);
        } else if (keccak256(bytes(agent.name)) == keccak256("DeFiAgent")) {
            return _executeDeFiAgent(agentId, inputData);
        } else if (keccak256(bytes(agent.name)) == keccak256("NFTAgent")) {
            return _executeNFTAgent(agentId, inputData);
        } else {
            return _executeGenericAgent(agentId, inputData);
        }
    }

    /**
     * @dev Execute trading agent logic
     */
    function _executeTradingAgent(uint256 agentId, bytes calldata inputData) internal view returns (bytes memory) {
        // Simulate trading logic
        (address token, uint256 amount, string memory action) = abi.decode(inputData, (address, uint256, string));
        
        // Mock trading execution
        uint256 price = _getTokenPrice(token);
        uint256 result = amount.mul(price).div(1e18);
        
        return abi.encode(agentId, action, result, block.timestamp);
    }

    /**
     * @dev Execute DeFi agent logic
     */
    function _executeDeFiAgent(uint256 agentId, bytes calldata inputData) internal view returns (bytes memory) {
        // Simulate DeFi operations
        (string memory operation, uint256 amount, address protocol) = abi.decode(inputData, (string, uint256, address));
        
        // Mock DeFi execution
        uint256 yield = amount.mul(5).div(100); // 5% yield
        
        return abi.encode(agentId, operation, yield, protocol, block.timestamp);
    }

    /**
     * @dev Execute NFT agent logic
     */
    function _executeNFTAgent(uint256 agentId, bytes calldata inputData) internal view returns (bytes memory) {
        // Simulate NFT operations
        (uint256 tokenId, string memory action, uint256 price) = abi.decode(inputData, (uint256, string, uint256));
        
        // Mock NFT execution
        bool success = price > 0;
        
        return abi.encode(agentId, tokenId, action, success, block.timestamp);
    }

    /**
     * @dev Execute generic agent logic
     */
    function _executeGenericAgent(uint256 agentId, bytes calldata inputData) internal view returns (bytes memory) {
        // Generic execution logic
        return abi.encode(agentId, "generic_execution", inputData, block.timestamp);
    }

    /**
     * @dev Get token price (mock implementation)
     */
    function _getTokenPrice(address token) internal view returns (uint256) {
        // Mock price - in real implementation, this would query oracles
        return 1e18; // 1 token = 1 ETH
    }

    /**
     * @dev Calculate memory usage
     */
    function _calculateMemoryUsage(uint256 agentId) internal view returns (uint256) {
        // Mock memory calculation
        return 1024 * 1024; // 1MB
    }

    /**
     * @dev Calculate storage usage
     */
    function _calculateStorageUsage(uint256 agentId) internal view returns (uint256) {
        // Mock storage calculation
        return 100 * 1024; // 100KB
    }

    /**
     * @dev Handle execution fees
     */
    function _handleExecutionFees(uint256 agentId, uint256 totalFee) internal {
        AgentRegistry.Agent memory agent = agentRegistry.getAgent(agentId);
        
        uint256 agentFee = totalFee.mul(agent.feeRate).div(10000);
        uint256 protocolFee = totalFee.sub(agentFee);
        
        if (agentFee > 0) {
            payable(agent.owner).transfer(agentFee);
        }
        if (protocolFee > 0) {
            payable(feeCollector).transfer(protocolFee);
        }
    }

    /**
     * @dev Get execution history for an agent
     */
    function getExecutionHistory(uint256 agentId) external view returns (ExecutionResult[] memory) {
        return executionHistory[agentId];
    }

    /**
     * @dev Get execution environment
     */
    function getExecutionEnvironment(uint256 envId) external view validEnvironment(envId) returns (ExecutionEnvironment memory) {
        return executionEnvironments[envId];
    }

    /**
     * @dev Get agent template
     */
    function getAgentTemplate(uint256 templateId) external view returns (AgentTemplate memory) {
        require(templateId > 0 && templateId < nextTemplateId, "Invalid template ID");
        return agentTemplates[templateId];
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
     * @dev Authorize oracle
     */
    function authorizeOracle(address oracle) external onlyOwner {
        authorizedOracles[oracle] = true;
    }

    /**
     * @dev Revoke oracle authorization
     */
    function revokeOracle(address oracle) external onlyOwner {
        authorizedOracles[oracle] = false;
    }

    /**
     * @dev Set configuration parameters
     */
    function setConfig(
        uint256 _maxExecutionTime,
        uint256 _maxGasPerExecution,
        uint256 _maxMemoryPerExecution,
        uint256 _maxStoragePerExecution,
        uint256 _executionFeeRate
    ) external onlyOwner {
        maxExecutionTime = _maxExecutionTime;
        maxGasPerExecution = _maxGasPerExecution;
        maxMemoryPerExecution = _maxMemoryPerExecution;
        maxStoragePerExecution = _maxStoragePerExecution;
        executionFeeRate = _executionFeeRate;
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
