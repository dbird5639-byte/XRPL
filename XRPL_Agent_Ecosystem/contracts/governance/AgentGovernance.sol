// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";

/**
 * @title AgentGovernance
 * @dev Advanced governance system for the XRPL Agent Ecosystem with voting, proposals, and treasury management
 * @author XRPL Agent Ecosystem
 */
contract AgentGovernance is ReentrancyGuard, Pausable, Ownable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Proposal types
    enum ProposalType {
        ProtocolUpgrade,
        ParameterChange,
        TreasurySpending,
        AgentPolicy,
        BridgePolicy,
        EmergencyAction
    }

    // Proposal status
    enum ProposalStatus {
        Pending,
        Active,
        Succeeded,
        Defeated,
        Executed,
        Cancelled
    }

    // Proposal structure
    struct Proposal {
        uint256 id;
        address proposer;
        ProposalType proposalType;
        string title;
        string description;
        string[] targets;
        uint256[] values;
        string[] signatures;
        bytes[] calldatas;
        uint256 startBlock;
        uint256 endBlock;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        bool executed;
        ProposalStatus status;
        uint256 creationTime;
        uint256 executionTime;
        string metadata;
    }

    // Voting power structure
    struct VotingPower {
        uint256 tokenBalance;
        uint256 stakedAmount;
        uint256 agentReputation;
        uint256 totalPower;
        uint256 lastUpdate;
    }

    // Treasury transaction structure
    struct TreasuryTransaction {
        uint256 id;
        address recipient;
        address token;
        uint256 amount;
        string purpose;
        bool executed;
        uint256 proposalId;
        uint256 executionTime;
    }

    // Events
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        ProposalType proposalType,
        string title,
        uint256 startBlock,
        uint256 endBlock
    );
    event VoteCast(
        address indexed voter,
        uint256 indexed proposalId,
        uint8 support,
        uint256 votes,
        string reason
    );
    event ProposalExecuted(uint256 indexed proposalId, bool success, string errorMessage);
    event TreasuryTransactionExecuted(
        uint256 indexed txId,
        address indexed recipient,
        uint256 amount,
        uint256 proposalId
    );
    event VotingPowerUpdated(
        address indexed voter,
        uint256 oldPower,
        uint256 newPower,
        uint256 tokenBalance,
        uint256 stakedAmount,
        uint256 agentReputation
    );

    // State variables
    mapping(uint256 => Proposal) public proposals;
    mapping(address => VotingPower) public votingPowers;
    mapping(address => mapping(uint256 => bool)) public hasVoted;
    mapping(uint256 => TreasuryTransaction) public treasuryTransactions;
    mapping(address => bool) public authorizedExecutors;
    mapping(address => bool) public authorizedAgents;
    
    IERC20 public governanceToken;
    address public agentRegistry;
    address public treasury;
    address public emergencyMultisig;
    
    uint256 public nextProposalId = 1;
    uint256 public nextTreasuryTxId = 1;
    uint256 public totalProposals = 0;
    uint256 public totalTreasurySpent = 0;
    
    // Configuration
    uint256 public votingDelay = 1; // 1 block
    uint256 public votingPeriod = 17280; // ~3 days in blocks
    uint256 public proposalThreshold = 1000 * 1e18; // 1000 tokens
    uint256 public quorumVotes = 10000 * 1e18; // 10000 tokens
    uint256 public executionDelay = 17280; // ~3 days in blocks
    uint256 public emergencyExecutionDelay = 1440; // ~6 hours in blocks
    
    // Voting power weights
    uint256 public tokenWeight = 1; // 1x for token balance
    uint256 public stakingWeight = 2; // 2x for staked tokens
    uint256 public reputationWeight = 3; // 3x for agent reputation

    // Modifiers
    modifier onlyAuthorizedExecutor() {
        require(authorizedExecutors[msg.sender] || msg.sender == owner(), "Not authorized executor");
        _;
    }

    modifier onlyAuthorizedAgent() {
        require(authorizedAgents[msg.sender] || msg.sender == owner(), "Not authorized agent");
        _;
    }

    modifier validProposal(uint256 proposalId) {
        require(proposalId > 0 && proposalId < nextProposalId, "Invalid proposal ID");
        _;
    }

    constructor(
        address _governanceToken,
        address _agentRegistry,
        address _treasury,
        address _emergencyMultisig
    ) {
        governanceToken = IERC20(_governanceToken);
        agentRegistry = _agentRegistry;
        treasury = _treasury;
        emergencyMultisig = _emergencyMultisig;
    }

    /**
     * @dev Create a new proposal
     */
    function propose(
        ProposalType proposalType,
        string memory title,
        string memory description,
        string[] memory targets,
        uint256[] memory values,
        string[] memory signatures,
        bytes[] memory calldatas,
        string memory metadata
    ) external nonReentrant whenNotPaused returns (uint256 proposalId) {
        require(governanceToken.balanceOf(msg.sender) >= proposalThreshold, "Insufficient voting power");
        require(targets.length == values.length, "Targets and values length mismatch");
        require(targets.length == signatures.length, "Targets and signatures length mismatch");
        require(targets.length == calldatas.length, "Targets and calldatas length mismatch");
        require(targets.length > 0, "No targets specified");
        require(bytes(title).length > 0, "Title required");
        require(bytes(description).length > 0, "Description required");

        proposalId = nextProposalId++;
        
        proposals[proposalId] = Proposal({
            id: proposalId,
            proposer: msg.sender,
            proposalType: proposalType,
            title: title,
            description: description,
            targets: targets,
            values: values,
            signatures: signatures,
            calldatas: calldatas,
            startBlock: block.number + votingDelay,
            endBlock: block.number + votingDelay + votingPeriod,
            forVotes: 0,
            againstVotes: 0,
            abstainVotes: 0,
            executed: false,
            status: ProposalStatus.Pending,
            creationTime: block.timestamp,
            executionTime: 0,
            metadata: metadata
        });

        totalProposals++;

        emit ProposalCreated(proposalId, msg.sender, proposalType, title, proposals[proposalId].startBlock, proposals[proposalId].endBlock);
    }

    /**
     * @dev Cast a vote on a proposal
     */
    function castVote(
        uint256 proposalId,
        uint8 support,
        string memory reason
    ) external validProposal(proposalId) nonReentrant whenNotPaused {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.number >= proposal.startBlock, "Voting not started");
        require(block.number <= proposal.endBlock, "Voting ended");
        require(!hasVoted[msg.sender][proposalId], "Already voted");
        require(support <= 2, "Invalid vote type"); // 0=against, 1=for, 2=abstain

        uint256 votes = getVotingPower(msg.sender);
        require(votes > 0, "No voting power");

        hasVoted[msg.sender][proposalId] = true;

        if (support == 0) {
            proposal.againstVotes = proposal.againstVotes.add(votes);
        } else if (support == 1) {
            proposal.forVotes = proposal.forVotes.add(votes);
        } else if (support == 2) {
            proposal.abstainVotes = proposal.abstainVotes.add(votes);
        }

        emit VoteCast(msg.sender, proposalId, support, votes, reason);
    }

    /**
     * @dev Execute a proposal
     */
    function executeProposal(uint256 proposalId) external validProposal(proposalId) nonReentrant whenNotPaused {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.number > proposal.endBlock, "Voting not ended");
        require(proposal.status == ProposalStatus.Succeeded, "Proposal not succeeded");
        require(!proposal.executed, "Proposal already executed");
        
        // Check execution delay
        uint256 requiredDelay = proposal.proposalType == ProposalType.EmergencyAction 
            ? emergencyExecutionDelay 
            : executionDelay;
        require(block.number >= proposal.endBlock + requiredDelay, "Execution delay not met");

        proposal.executed = true;
        proposal.status = ProposalStatus.Executed;
        proposal.executionTime = block.timestamp;

        bool success = true;
        string memory errorMessage = "";

        // Execute proposal actions
        for (uint256 i = 0; i < proposal.targets.length; i++) {
            try this._executeAction(
                proposal.targets[i],
                proposal.values[i],
                proposal.signatures[i],
                proposal.calldatas[i]
            ) {
                // Action executed successfully
            } catch Error(string memory reason) {
                success = false;
                errorMessage = reason;
                break;
            } catch {
                success = false;
                errorMessage = "Unknown execution error";
                break;
            }
        }

        if (!success) {
            proposal.status = ProposalStatus.Defeated;
        }

        emit ProposalExecuted(proposalId, success, errorMessage);
    }

    /**
     * @dev Internal action execution
     */
    function _executeAction(
        string memory target,
        uint256 value,
        string memory signature,
        bytes memory calldata
    ) external {
        // This would execute the actual proposal action
        // Implementation depends on the specific action type
        require(bytes(target).length > 0, "Invalid target");
    }

    /**
     * @dev Queue a proposal for execution
     */
    function queueProposal(uint256 proposalId) external validProposal(proposalId) {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.number > proposal.endBlock, "Voting not ended");
        require(proposal.status == ProposalStatus.Pending, "Proposal not pending");
        
        uint256 totalVotes = proposal.forVotes.add(proposal.againstVotes).add(proposal.abstainVotes);
        
        if (totalVotes >= quorumVotes && proposal.forVotes > proposal.againstVotes) {
            proposal.status = ProposalStatus.Succeeded;
        } else {
            proposal.status = ProposalStatus.Defeated;
        }
    }

    /**
     * @dev Cancel a proposal
     */
    function cancelProposal(uint256 proposalId) external validProposal(proposalId) {
        Proposal storage proposal = proposals[proposalId];
        
        require(msg.sender == proposal.proposer || msg.sender == owner(), "Not proposer or owner");
        require(proposal.status == ProposalStatus.Pending, "Proposal not pending");
        require(block.number < proposal.startBlock, "Voting started");
        
        proposal.status = ProposalStatus.Cancelled;
    }

    /**
     * @dev Execute treasury transaction
     */
    function executeTreasuryTransaction(
        uint256 proposalId,
        address recipient,
        address token,
        uint256 amount,
        string memory purpose
    ) external onlyAuthorizedExecutor nonReentrant whenNotPaused {
        Proposal storage proposal = proposals[proposalId];
        
        require(proposal.executed, "Proposal not executed");
        require(proposal.proposalType == ProposalType.TreasurySpending, "Not treasury proposal");
        require(recipient != address(0), "Invalid recipient");
        require(amount > 0, "Invalid amount");

        uint256 txId = nextTreasuryTxId++;
        
        treasuryTransactions[txId] = TreasuryTransaction({
            id: txId,
            recipient: recipient,
            token: token,
            amount: amount,
            purpose: purpose,
            executed: true,
            proposalId: proposalId,
            executionTime: block.timestamp
        });

        // Transfer tokens from treasury
        if (token == address(0)) {
            payable(recipient).transfer(amount);
        } else {
            IERC20(token).safeTransferFrom(treasury, recipient, amount);
        }

        totalTreasurySpent = totalTreasurySpent.add(amount);

        emit TreasuryTransactionExecuted(txId, recipient, amount, proposalId);
    }

    /**
     * @dev Update voting power for an address
     */
    function updateVotingPower(address voter) external onlyAuthorizedAgent {
        uint256 oldPower = votingPowers[voter].totalPower;
        
        uint256 tokenBalance = governanceToken.balanceOf(voter);
        uint256 stakedAmount = _getStakedAmount(voter);
        uint256 agentReputation = _getAgentReputation(voter);
        
        uint256 newPower = tokenBalance.mul(tokenWeight)
            .add(stakedAmount.mul(stakingWeight))
            .add(agentReputation.mul(reputationWeight));
        
        votingPowers[voter] = VotingPower({
            tokenBalance: tokenBalance,
            stakedAmount: stakedAmount,
            agentReputation: agentReputation,
            totalPower: newPower,
            lastUpdate: block.timestamp
        });

        if (oldPower != newPower) {
            emit VotingPowerUpdated(voter, oldPower, newPower, tokenBalance, stakedAmount, agentReputation);
        }
    }

    /**
     * @dev Get voting power for an address
     */
    function getVotingPower(address voter) public view returns (uint256) {
        uint256 tokenBalance = governanceToken.balanceOf(voter);
        uint256 stakedAmount = _getStakedAmount(voter);
        uint256 agentReputation = _getAgentReputation(voter);
        
        return tokenBalance.mul(tokenWeight)
            .add(stakedAmount.mul(stakingWeight))
            .add(agentReputation.mul(reputationWeight));
    }

    /**
     * @dev Get staked amount for an address
     */
    function _getStakedAmount(address voter) internal view returns (uint256) {
        // This would query the staking contract
        // For now, return 0
        return 0;
    }

    /**
     * @dev Get agent reputation for an address
     */
    function _getAgentReputation(address voter) internal view returns (uint256) {
        // This would query the agent registry
        // For now, return 0
        return 0;
    }

    /**
     * @dev Get proposal details
     */
    function getProposal(uint256 proposalId) external view validProposal(proposalId) returns (Proposal memory) {
        return proposals[proposalId];
    }

    /**
     * @dev Get treasury transaction
     */
    function getTreasuryTransaction(uint256 txId) external view returns (TreasuryTransaction memory) {
        require(txId > 0 && txId < nextTreasuryTxId, "Invalid transaction ID");
        return treasuryTransactions[txId];
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
     * @dev Authorize agent
     */
    function authorizeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = true;
    }

    /**
     * @dev Revoke agent authorization
     */
    function revokeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = false;
    }

    /**
     * @dev Set configuration parameters
     */
    function setConfig(
        uint256 _votingDelay,
        uint256 _votingPeriod,
        uint256 _proposalThreshold,
        uint256 _quorumVotes,
        uint256 _executionDelay,
        uint256 _emergencyExecutionDelay
    ) external onlyOwner {
        votingDelay = _votingDelay;
        votingPeriod = _votingPeriod;
        proposalThreshold = _proposalThreshold;
        quorumVotes = _quorumVotes;
        executionDelay = _executionDelay;
        emergencyExecutionDelay = _emergencyExecutionDelay;
    }

    /**
     * @dev Set voting power weights
     */
    function setVotingWeights(
        uint256 _tokenWeight,
        uint256 _stakingWeight,
        uint256 _reputationWeight
    ) external onlyOwner {
        tokenWeight = _tokenWeight;
        stakingWeight = _stakingWeight;
        reputationWeight = _reputationWeight;
    }

    /**
     * @dev Set treasury address
     */
    function setTreasury(address _treasury) external onlyOwner {
        require(_treasury != address(0), "Invalid address");
        treasury = _treasury;
    }

    /**
     * @dev Set emergency multisig
     */
    function setEmergencyMultisig(address _emergencyMultisig) external onlyOwner {
        require(_emergencyMultisig != address(0), "Invalid address");
        emergencyMultisig = _emergencyMultisig;
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
