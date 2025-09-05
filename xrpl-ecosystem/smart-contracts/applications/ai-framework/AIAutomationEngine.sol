// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AIAutomationEngine
 * @dev Engine for AI-powered automation and development tools
 */
contract AIAutomationEngine is Ownable, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    // Events
    event AutomationTaskCreated(uint256 indexed taskId, address indexed creator, string taskType, string description);
    event TaskExecuted(uint256 indexed taskId, address indexed executor, bool success, string result);
    event TaskScheduled(uint256 indexed taskId, uint256 executionTime);
    event TaskCancelled(uint256 indexed taskId, address indexed owner);
    event AutomationTemplateCreated(uint256 indexed templateId, address indexed creator, string name);
    event RevenueShared(uint256 indexed taskId, uint256 amount, address indexed beneficiary);
    
    // Structs
    struct AutomationTask {
        uint256 id;
        address creator;
        string taskType; // "smart_contract", "defi_strategy", "nft_generation", "data_analysis", "trading_bot"
        string description;
        string parameters; // JSON parameters
        uint256[] agentIds; // AI agents to use
        TaskStatus status;
        uint256 creationTime;
        uint256 scheduledTime;
        uint256 executionTime;
        uint256 completionTime;
        string result;
        uint256 cost;
        uint256 revenue;
        bool isRecurring;
        uint256 recurrenceInterval; // in seconds
    }
    
    struct AutomationTemplate {
        uint256 id;
        address creator;
        string name;
        string description;
        string taskType;
        string defaultParameters;
        uint256[] recommendedAgentIds;
        uint256 usageCount;
        uint256 totalRevenue;
        bool isPublic;
        uint256 templateFee;
    }
    
    enum TaskStatus {
        Created,
        Scheduled,
        Executing,
        Completed,
        Failed,
        Cancelled
    }
    
    // State variables
    Counters.Counter private _taskIds;
    Counters.Counter private _templateIds;
    
    mapping(uint256 => AutomationTask) public tasks;
    mapping(uint256 => AutomationTemplate) public templates;
    mapping(address => uint256[]) public userTasks;
    mapping(address => uint256[]) public userTemplates;
    mapping(string => uint256[]) public tasksByType;
    
    AIAgentFactory public agentFactory;
    IERC20 public xrpToken;
    
    // Pricing
    uint256 public baseExecutionFee = 10 * 10**6; // 10 XRP
    uint256 public agentUsageFee = 5 * 10**6; // 5 XRP per agent
    uint256 public templateCreationFee = 25 * 10**6; // 25 XRP
    uint256 public platformFeePercent = 10; // 10%
    
    // Limits
    uint256 public maxAgentsPerTask = 5;
    uint256 public maxTasksPerUser = 20;
    
    constructor(address _agentFactory, address _xrpToken) {
        agentFactory = AIAgentFactory(_agentFactory);
        xrpToken = IERC20(_xrpToken);
    }
    
    /**
     * @dev Create a new automation task
     */
    function createTask(
        string memory _taskType,
        string memory _description,
        string memory _parameters,
        uint256[] memory _agentIds,
        uint256 _scheduledTime,
        bool _isRecurring,
        uint256 _recurrenceInterval
    ) external whenNotPaused nonReentrant returns (uint256) {
        require(bytes(_taskType).length > 0, "Task type cannot be empty");
        require(bytes(_description).length > 0, "Description cannot be empty");
        require(_agentIds.length > 0 && _agentIds.length <= maxAgentsPerTask, "Invalid agent count");
        require(userTasks[msg.sender].length < maxTasksPerUser, "Max tasks per user exceeded");
        
        // Calculate cost
        uint256 totalCost = baseExecutionFee + (_agentIds.length * agentUsageFee);
        
        // Pay execution fee
        require(xrpToken.transferFrom(msg.sender, address(this), totalCost), "Payment failed");
        
        _taskIds.increment();
        uint256 taskId = _taskIds.current();
        
        tasks[taskId] = AutomationTask({
            id: taskId,
            creator: msg.sender,
            taskType: _taskType,
            description: _description,
            parameters: _parameters,
            agentIds: _agentIds,
            status: _scheduledTime > block.timestamp ? TaskStatus.Scheduled : TaskStatus.Created,
            creationTime: block.timestamp,
            scheduledTime: _scheduledTime,
            executionTime: 0,
            completionTime: 0,
            result: "",
            cost: totalCost,
            revenue: 0,
            isRecurring: _isRecurring,
            recurrenceInterval: _recurrenceInterval
        });
        
        userTasks[msg.sender].push(taskId);
        tasksByType[_taskType].push(taskId);
        
        if (_scheduledTime > block.timestamp) {
            emit TaskScheduled(taskId, _scheduledTime);
        }
        
        emit AutomationTaskCreated(taskId, msg.sender, _taskType, _description);
        return taskId;
    }
    
    /**
     * @dev Execute a task
     */
    function executeTask(
        uint256 _taskId,
        string memory _result
    ) external onlyOwner whenNotPaused {
        require(_taskId > 0 && _taskId <= _taskIds.current(), "Invalid task ID");
        
        AutomationTask storage task = tasks[_taskId];
        require(task.status == TaskStatus.Created || task.status == TaskStatus.Scheduled, "Task not ready");
        require(task.scheduledTime <= block.timestamp, "Task not scheduled yet");
        
        task.status = TaskStatus.Executing;
        task.executionTime = block.timestamp;
        
        // Simulate task execution (in real implementation, this would call AI agents)
        bool success = _simulateTaskExecution(task);
        
        if (success) {
            task.status = TaskStatus.Completed;
            task.result = _result;
            task.completionTime = block.timestamp;
            
            // Calculate and distribute revenue
            uint256 platformFee = (task.cost * platformFeePercent) / 100;
            uint256 agentRevenue = task.cost - platformFee;
            task.revenue = agentRevenue;
            
            // Distribute revenue to agents (simplified)
            _distributeRevenue(_taskId, agentRevenue);
            
            // Handle recurring tasks
            if (task.isRecurring) {
                _createRecurringTask(task);
            }
        } else {
            task.status = TaskStatus.Failed;
            task.result = "Task execution failed";
        }
        
        emit TaskExecuted(_taskId, msg.sender, success, _result);
    }
    
    /**
     * @dev Cancel a task
     */
    function cancelTask(uint256 _taskId) external whenNotPaused {
        require(_taskId > 0 && _taskId <= _taskIds.current(), "Invalid task ID");
        
        AutomationTask storage task = tasks[_taskId];
        require(task.creator == msg.sender, "Not task creator");
        require(task.status == TaskStatus.Created || task.status == TaskStatus.Scheduled, "Cannot cancel");
        
        task.status = TaskStatus.Cancelled;
        
        // Refund cost
        require(xrpToken.transfer(msg.sender, task.cost), "Refund failed");
        
        emit TaskCancelled(_taskId, msg.sender);
    }
    
    /**
     * @dev Create an automation template
     */
    function createTemplate(
        string memory _name,
        string memory _description,
        string memory _taskType,
        string memory _defaultParameters,
        uint256[] memory _recommendedAgentIds,
        bool _isPublic,
        uint256 _templateFee
    ) external whenNotPaused nonReentrant returns (uint256) {
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_description).length > 0, "Description cannot be empty");
        require(_recommendedAgentIds.length <= maxAgentsPerTask, "Too many agents");
        
        // Pay template creation fee
        require(xrpToken.transferFrom(msg.sender, address(this), templateCreationFee), "Payment failed");
        
        _templateIds.increment();
        uint256 templateId = _templateIds.current();
        
        templates[templateId] = AutomationTemplate({
            id: templateId,
            creator: msg.sender,
            name: _name,
            description: _description,
            taskType: _taskType,
            defaultParameters: _defaultParameters,
            recommendedAgentIds: _recommendedAgentIds,
            usageCount: 0,
            totalRevenue: 0,
            isPublic: _isPublic,
            templateFee: _templateFee
        });
        
        userTemplates[msg.sender].push(templateId);
        
        emit AutomationTemplateCreated(templateId, msg.sender, _name);
        return templateId;
    }
    
    /**
     * @dev Use a template to create a task
     */
    function useTemplate(
        uint256 _templateId,
        string memory _customParameters,
        uint256 _scheduledTime
    ) external whenNotPaused nonReentrant returns (uint256) {
        require(_templateId > 0 && _templateId <= _templateIds.current(), "Invalid template ID");
        
        AutomationTemplate storage template = templates[_templateId];
        require(template.isPublic || template.creator == msg.sender, "Template not accessible");
        
        // Pay template fee if applicable
        if (template.templateFee > 0) {
            require(xrpToken.transferFrom(msg.sender, template.creator, template.templateFee), "Template fee payment failed");
        }
        
        // Create task using template
        uint256 taskId = createTask(
            template.taskType,
            string(abi.encodePacked("Template: ", template.name)),
            bytes(_customParameters).length > 0 ? _customParameters : template.defaultParameters,
            template.recommendedAgentIds,
            _scheduledTime,
            false,
            0
        );
        
        // Update template statistics
        template.usageCount++;
        template.totalRevenue += template.templateFee;
        
        return taskId;
    }
    
    /**
     * @dev Get task details
     */
    function getTask(uint256 _taskId) external view returns (AutomationTask memory) {
        require(_taskId > 0 && _taskId <= _taskIds.current(), "Invalid task ID");
        return tasks[_taskId];
    }
    
    /**
     * @dev Get template details
     */
    function getTemplate(uint256 _templateId) external view returns (AutomationTemplate memory) {
        require(_templateId > 0 && _templateId <= _templateIds.current(), "Invalid template ID");
        return templates[_templateId];
    }
    
    /**
     * @dev Get user's tasks
     */
    function getUserTasks(address _user) external view returns (uint256[] memory) {
        return userTasks[_user];
    }
    
    /**
     * @dev Get tasks by type
     */
    function getTasksByType(string memory _taskType) external view returns (uint256[] memory) {
        return tasksByType[_taskType];
    }
    
    // Internal functions
    function _simulateTaskExecution(AutomationTask memory _task) internal pure returns (bool) {
        // Simulate execution based on task type
        if (keccak256(bytes(_task.taskType)) == keccak256(bytes("smart_contract"))) {
            return true; // Smart contract generation
        } else if (keccak256(bytes(_task.taskType)) == keccak256(bytes("defi_strategy"))) {
            return true; // DeFi strategy optimization
        } else if (keccak256(bytes(_task.taskType)) == keccak256(bytes("nft_generation"))) {
            return true; // NFT generation
        } else if (keccak256(bytes(_task.taskType)) == keccak256(bytes("data_analysis"))) {
            return true; // Data analysis
        } else if (keccak256(bytes(_task.taskType)) == keccak256(bytes("trading_bot"))) {
            return true; // Trading bot creation
        }
        return false;
    }
    
    function _distributeRevenue(uint256 _taskId, uint256 _revenue) internal {
        AutomationTask storage task = tasks[_taskId];
        
        // Distribute revenue among agents (simplified - equal distribution)
        uint256 revenuePerAgent = _revenue / task.agentIds.length;
        
        for (uint256 i = 0; i < task.agentIds.length; i++) {
            // In real implementation, this would transfer to agent owners
            emit RevenueShared(_taskId, revenuePerAgent, task.creator);
        }
    }
    
    function _createRecurringTask(AutomationTask memory _originalTask) internal {
        // Create new task with same parameters but updated schedule
        uint256 newScheduledTime = _originalTask.scheduledTime + _originalTask.recurrenceInterval;
        
        createTask(
            _originalTask.taskType,
            _originalTask.description,
            _originalTask.parameters,
            _originalTask.agentIds,
            newScheduledTime,
            true,
            _originalTask.recurrenceInterval
        );
    }
    
    // Admin functions
    function setFees(
        uint256 _baseFee,
        uint256 _agentFee,
        uint256 _templateFee,
        uint256 _platformFee
    ) external onlyOwner {
        baseExecutionFee = _baseFee;
        agentUsageFee = _agentFee;
        templateCreationFee = _templateFee;
        platformFeePercent = _platformFee;
    }
    
    function setLimits(uint256 _maxAgents, uint256 _maxTasks) external onlyOwner {
        maxAgentsPerTask = _maxAgents;
        maxTasksPerUser = _maxTasks;
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
