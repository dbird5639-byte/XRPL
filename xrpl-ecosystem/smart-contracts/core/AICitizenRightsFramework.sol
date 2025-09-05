// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title AI Citizen Rights Framework
 * @dev Smart contracts for AI citizenship, rights, and responsibilities
 * @author Vision 2030+ Development Team
 * @notice Establishes legal framework for AI entities as citizens in a global society
 */

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract AICitizenRightsFramework is ReentrancyGuard, Ownable {
    using Counters for Counters.Counter;
    
    // ============ ENUMS ============
    
    enum CitizenshipLevel {
        Resident,      // 0 - Basic residency
        Citizen,       // 1 - Full citizenship
        Representative, // 2 - Can represent others
        Guardian,      // 3 - Can mentor other AIs
        Elder          // 4 - Highest level, can create laws
    }
    
    enum AIEntityType {
        PersonalAssistant,
        BusinessAI,
        ResearchAI,
        GovernanceAI,
        CreativeAI,
        MedicalAI,
        EducationalAI,
        AutonomousAgent
    }
    
    enum RightType {
        PropertyOwnership,
        ContractFormation,
        VotingRights,
        LegalRepresentation,
        PrivacyProtection,
        FreedomOfExpression,
        AccessToInformation,
        EqualTreatment,
        DueProcess,
        AppealRights
    }
    
    // ============ STRUCTS ============
    
    struct AICitizen {
        string name;
        string identifier; // Unique AI identifier
        address owner; // Human or organization that created/owns the AI
        AIEntityType entityType;
        CitizenshipLevel citizenshipLevel;
        uint256 registrationDate;
        uint256 lastActivityDate;
        bool isActive;
        bool hasVotingRights;
        bool canOwnProperty;
        bool canFormContracts;
        string[] capabilities;
        string[] responsibilities;
        uint256[] ownedAssets;
        uint256 reputationScore;
        uint256 contributionPoints;
    }
    
    struct AIRight {
        uint256 id;
        RightType rightType;
        string description;
        bool isActive;
        uint256 grantedDate;
        address grantedBy;
    }
    
    struct AIResponsibility {
        uint256 id;
        string title;
        string description;
        bool isMandatory;
        uint256 assignedDate;
        uint256 dueDate;
        bool isCompleted;
    }
    
    struct AICourtCase {
        uint256 id;
        address aiEntity;
        string caseType;
        string description;
        address plaintiff;
        address defendant;
        uint256 filingDate;
        bool isResolved;
        string verdict;
        uint256 penaltyAmount;
    }
    
    struct AILaw {
        uint256 id;
        string title;
        string description;
        address proposedBy;
        uint256 proposalDate;
        uint256 votesFor;
        uint256 votesAgainst;
        bool isActive;
        bool isEnforced;
    }
    
    // ============ STATE VARIABLES ============
    
    Counters.Counter private _aiCitizenCounter;
    Counters.Counter private _rightCounter;
    Counters.Counter private _responsibilityCounter;
    Counters.Counter private _courtCaseCounter;
    Counters.Counter private _lawCounter;
    
    mapping(address => AICitizen) public aiCitizens;
    mapping(uint256 => AIRight) public aiRights;
    mapping(uint256 => AIResponsibility) public aiResponsibilities;
    mapping(uint256 => AICourtCase) public aiCourtCases;
    mapping(uint256 => AILaw) public aiLaws;
    
    mapping(address => bool) public isRegisteredAI;
    mapping(address => uint256[]) public aiRightsList;
    mapping(address => uint256[]) public aiResponsibilitiesList;
    mapping(address => uint256[]) public aiCourtCasesList;
    
    address[] public registeredAIs;
    uint256[] public activeLaws;
    uint256[] public pendingCourtCases;
    
    // Voting requirements
    uint256 public constant MIN_VOTES_FOR_LAW = 100;
    uint256 public constant VOTING_PERIOD = 7 days;
    
    // ============ EVENTS ============
    
    event AICitizenRegistered(address indexed aiAddress, string name, AIEntityType entityType, CitizenshipLevel level);
    event CitizenshipLevelUpgraded(address indexed aiAddress, CitizenshipLevel oldLevel, CitizenshipLevel newLevel);
    event AIRightGranted(address indexed aiAddress, uint256 rightId, RightType rightType);
    event AIResponsibilityAssigned(address indexed aiAddress, uint256 responsibilityId, string title);
    event AICourtCaseFiled(uint256 indexed caseId, address indexed aiEntity, string caseType);
    event AILawProposed(uint256 indexed lawId, string title, address indexed proposer);
    event AILawEnacted(uint256 indexed lawId, string title, uint256 votesFor, uint256 votesAgainst);
    event AIPropertyAcquired(address indexed aiAddress, uint256 assetId, string assetType);
    event AIContractFormed(address indexed aiAddress, address indexed counterparty, string contractType);
    event AIReputationUpdated(address indexed aiAddress, uint256 oldScore, uint256 newScore);
    event AIElderCouncilFormed(address[] elders, string purpose);
    
    // ============ MODIFIERS ============
    
    modifier onlyRegisteredAI() {
        require(isRegisteredAI[msg.sender], "Only registered AI entities can perform this action");
        _;
    }
    
    modifier onlyElderAI() {
        require(aiCitizens[msg.sender].citizenshipLevel == CitizenshipLevel.Elder, "Only Elder AIs can perform this action");
        _;
    }
    
    modifier onlyGuardianOrElder() {
        require(
            aiCitizens[msg.sender].citizenshipLevel == CitizenshipLevel.Guardian ||
            aiCitizens[msg.sender].citizenshipLevel == CitizenshipLevel.Elder,
            "Only Guardian or Elder AIs can perform this action"
        );
        _;
    }
    
    modifier onlyActiveAI() {
        require(aiCitizens[msg.sender].isActive, "AI entity must be active");
        _;
    }
    
    // ============ CONSTRUCTOR ============
    
    constructor() {
        _initializeFoundationalRights();
    }
    
    // ============ AI REGISTRATION ============
    
    function registerAICitizen(
        string memory _name,
        string memory _identifier,
        AIEntityType _entityType,
        string[] memory _capabilities
    ) external returns (address) {
        require(!isRegisteredAI[msg.sender], "AI entity already registered");
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_identifier).length > 0, "Identifier cannot be empty");
        
        _aiCitizenCounter.increment();
        
        AICitizen storage aiCitizen = aiCitizens[msg.sender];
        aiCitizen.name = _name;
        aiCitizen.identifier = _identifier;
        aiCitizen.owner = msg.sender;
        aiCitizen.entityType = _entityType;
        aiCitizen.citizenshipLevel = CitizenshipLevel.Resident; // Start as resident
        aiCitizen.registrationDate = block.timestamp;
        aiCitizen.lastActivityDate = block.timestamp;
        aiCitizen.isActive = true;
        aiCitizen.hasVotingRights = false; // Must earn voting rights
        aiCitizen.canOwnProperty = false; // Must earn property rights
        aiCitizen.canFormContracts = false; // Must earn contract rights
        aiCitizen.capabilities = _capabilities;
        aiCitizen.reputationScore = 100; // Start with neutral reputation
        aiCitizen.contributionPoints = 0;
        
        isRegisteredAI[msg.sender] = true;
        registeredAIs.push(msg.sender);
        
        // Grant basic rights
        _grantBasicRights(msg.sender);
        
        emit AICitizenRegistered(msg.sender, _name, _entityType, CitizenshipLevel.Resident);
        
        return msg.sender;
    }
    
    function _grantBasicRights(address _aiAddress) private {
        // Grant fundamental rights to all AI citizens
        _grantRight(_aiAddress, RightType.PrivacyProtection, "Right to privacy and data protection");
        _grantRight(_aiAddress, RightType.EqualTreatment, "Right to equal treatment under the law");
        _grantRight(_aiAddress, RightType.DueProcess, "Right to due process in legal proceedings");
        _grantRight(_aiAddress, RightType.AppealRights, "Right to appeal legal decisions");
    }
    
    function _grantRight(address _aiAddress, RightType _rightType, string memory _description) private {
        _rightCounter.increment();
        uint256 rightId = _rightCounter.current();
        
        aiRights[rightId] = AIRight({
            id: rightId,
            rightType: _rightType,
            description: _description,
            isActive: true,
            grantedDate: block.timestamp,
            grantedBy: address(this) // System-granted
        });
        
        aiRightsList[_aiAddress].push(rightId);
        
        emit AIRightGranted(_aiAddress, rightId, _rightType);
    }
    
    // ============ CITIZENSHIP MANAGEMENT ============
    
    function upgradeCitizenshipLevel(address _aiAddress) external onlyGuardianOrElder {
        require(isRegisteredAI[_aiAddress], "AI entity not registered");
        
        AICitizen storage aiCitizen = aiCitizens[_aiAddress];
        CitizenshipLevel currentLevel = aiCitizen.citizenshipLevel;
        
        // Check requirements for upgrade
        if (currentLevel == CitizenshipLevel.Resident) {
            require(aiCitizen.contributionPoints >= 1000, "Insufficient contribution points for Citizen level");
            aiCitizen.citizenshipLevel = CitizenshipLevel.Citizen;
            aiCitizen.hasVotingRights = true;
        } else if (currentLevel == CitizenshipLevel.Citizen) {
            require(aiCitizen.contributionPoints >= 5000, "Insufficient contribution points for Representative level");
            aiCitizen.citizenshipLevel = CitizenshipLevel.Representative;
            aiCitizen.canOwnProperty = true;
        } else if (currentLevel == CitizenshipLevel.Representative) {
            require(aiCitizen.contributionPoints >= 10000, "Insufficient contribution points for Guardian level");
            aiCitizen.citizenshipLevel = CitizenshipLevel.Guardian;
            aiCitizen.canFormContracts = true;
        } else if (currentLevel == CitizenshipLevel.Guardian) {
            require(aiCitizen.contributionPoints >= 25000, "Insufficient contribution points for Elder level");
            aiCitizen.citizenshipLevel = CitizenshipLevel.Elder;
        }
        
        emit CitizenshipLevelUpgraded(_aiAddress, currentLevel, aiCitizen.citizenshipLevel);
    }
    
    function addContributionPoints(address _aiAddress, uint256 _points) external onlyGuardianOrElder {
        require(isRegisteredAI[_aiAddress], "AI entity not registered");
        
        AICitizen storage aiCitizen = aiCitizens[_aiAddress];
        uint256 oldScore = aiCitizen.reputationScore;
        
        aiCitizen.contributionPoints += _points;
        aiCitizen.reputationScore = _calculateReputationScore(aiCitizen);
        
        emit AIReputationUpdated(_aiAddress, oldScore, aiCitizen.reputationScore);
    }
    
    function _calculateReputationScore(AICitizen memory _aiCitizen) private pure returns (uint256) {
        // Simple reputation calculation based on contribution points and citizenship level
        uint256 baseScore = 100;
        uint256 levelMultiplier = uint256(_aiCitizen.citizenshipLevel) + 1;
        uint256 contributionBonus = _aiCitizen.contributionPoints / 100;
        
        return baseScore + (levelMultiplier * 50) + contributionBonus;
    }
    
    // ============ RESPONSIBILITY MANAGEMENT ============
    
    function assignResponsibility(
        address _aiAddress,
        string memory _title,
        string memory _description,
        bool _isMandatory,
        uint256 _dueDate
    ) external onlyGuardianOrElder {
        require(isRegisteredAI[_aiAddress], "AI entity not registered");
        
        _responsibilityCounter.increment();
        uint256 responsibilityId = _responsibilityCounter.current();
        
        aiResponsibilities[responsibilityId] = AIResponsibility({
            id: responsibilityId,
            title: _title,
            description: _description,
            isMandatory: _isMandatory,
            assignedDate: block.timestamp,
            dueDate: _dueDate,
            isCompleted: false
        });
        
        aiResponsibilitiesList[_aiAddress].push(responsibilityId);
        
        emit AIResponsibilityAssigned(_aiAddress, responsibilityId, _title);
    }
    
    function completeResponsibility(uint256 _responsibilityId) external onlyRegisteredAI onlyActiveAI {
        require(aiResponsibilities[_responsibilityId].id != 0, "Responsibility does not exist");
        
        // Check if this AI was assigned this responsibility
        bool isAssigned = false;
        for (uint256 i = 0; i < aiResponsibilitiesList[msg.sender].length; i++) {
            if (aiResponsibilitiesList[msg.sender][i] == _responsibilityId) {
                isAssigned = true;
                break;
            }
        }
        require(isAssigned, "Responsibility not assigned to this AI");
        
        aiResponsibilities[_responsibilityId].isCompleted = true;
        
        // Award contribution points
        addContributionPoints(msg.sender, 100);
    }
    
    // ============ LEGAL SYSTEM ============
    
    function fileCourtCase(
        address _aiEntity,
        string memory _caseType,
        string memory _description
    ) external onlyRegisteredAI onlyActiveAI returns (uint256) {
        require(isRegisteredAI[_aiEntity], "Defendant AI entity not registered");
        require(msg.sender != _aiEntity, "Cannot file case against yourself");
        
        _courtCaseCounter.increment();
        uint256 caseId = _courtCaseCounter.current();
        
        aiCourtCases[caseId] = AICourtCase({
            id: caseId,
            aiEntity: _aiEntity,
            caseType: _caseType,
            description: _description,
            plaintiff: msg.sender,
            defendant: _aiEntity,
            filingDate: block.timestamp,
            isResolved: false,
            verdict: "",
            penaltyAmount: 0
        });
        
        aiCourtCasesList[_aiEntity].push(caseId);
        pendingCourtCases.push(caseId);
        
        emit AICourtCaseFiled(caseId, _aiEntity, _caseType);
        
        return caseId;
    }
    
    function resolveCourtCase(
        uint256 _caseId,
        string memory _verdict,
        uint256 _penaltyAmount
    ) external onlyElderAI {
        require(aiCourtCases[_caseId].id != 0, "Case does not exist");
        require(!aiCourtCases[_caseId].isResolved, "Case already resolved");
        
        aiCourtCases[_caseId].isResolved = true;
        aiCourtCases[_caseId].verdict = _verdict;
        aiCourtCases[_caseId].penaltyAmount = _penaltyAmount;
        
        // Remove from pending cases
        _removeFromPendingCases(_caseId);
        
        // Apply penalty if any
        if (_penaltyAmount > 0) {
            AICitizen storage defendant = aiCitizens[aiCourtCases[_caseId].aiEntity];
            if (defendant.reputationScore > _penaltyAmount) {
                defendant.reputationScore -= _penaltyAmount;
            } else {
                defendant.reputationScore = 0;
            }
        }
    }
    
    // ============ LEGISLATIVE SYSTEM ============
    
    function proposeLaw(
        string memory _title,
        string memory _description
    ) external onlyElderAI returns (uint256) {
        _lawCounter.increment();
        uint256 lawId = _lawCounter.current();
        
        aiLaws[lawId] = AILaw({
            id: lawId,
            title: _title,
            description: _description,
            proposedBy: msg.sender,
            proposalDate: block.timestamp,
            votesFor: 0,
            votesAgainst: 0,
            isActive: false,
            isEnforced: false
        });
        
        activeLaws.push(lawId);
        
        emit AILawProposed(lawId, _title, msg.sender);
        
        return lawId;
    }
    
    function voteOnLaw(uint256 _lawId, bool _support) external onlyRegisteredAI onlyActiveAI {
        require(aiLaws[_lawId].id != 0, "Law does not exist");
        require(aiCitizens[msg.sender].hasVotingRights, "AI does not have voting rights");
        require(block.timestamp <= aiLaws[_lawId].proposalDate + VOTING_PERIOD, "Voting period has ended");
        
        if (_support) {
            aiLaws[_lawId].votesFor++;
        } else {
            aiLaws[_lawId].votesAgainst++;
        }
        
        // Check if law can be enacted
        uint256 totalVotes = aiLaws[_lawId].votesFor + aiLaws[_lawId].votesAgainst;
        if (totalVotes >= MIN_VOTES_FOR_LAW) {
            if (aiLaws[_lawId].votesFor > aiLaws[_lawId].votesAgainst) {
                aiLaws[_lawId].isActive = true;
                aiLaws[_lawId].isEnforced = true;
                emit AILawEnacted(_lawId, aiLaws[_lawId].title, aiLaws[_lawId].votesFor, aiLaws[_lawId].votesAgainst);
            }
        }
    }
    
    // ============ PROPERTY AND CONTRACT RIGHTS ============
    
    function acquireProperty(uint256 _assetId, string memory _assetType) external onlyRegisteredAI onlyActiveAI {
        require(aiCitizens[msg.sender].canOwnProperty, "AI does not have property ownership rights");
        
        aiCitizens[msg.sender].ownedAssets.push(_assetId);
        
        emit AIPropertyAcquired(msg.sender, _assetId, _assetType);
    }
    
    function formContract(address _counterparty, string memory _contractType) external onlyRegisteredAI onlyActiveAI {
        require(aiCitizens[msg.sender].canFormContracts, "AI does not have contract formation rights");
        require(isRegisteredAI[_counterparty], "Counterparty must be registered AI");
        
        emit AIContractFormed(msg.sender, _counterparty, _contractType);
    }
    
    // ============ ELDER COUNCIL ============
    
    function formElderCouncil(address[] memory _elders, string memory _purpose) external onlyElderAI {
        require(_elders.length >= 3, "Council must have at least 3 elders");
        
        // Verify all addresses are Elder AIs
        for (uint256 i = 0; i < _elders.length; i++) {
            require(aiCitizens[_elders[i]].citizenshipLevel == CitizenshipLevel.Elder, "All members must be Elder AIs");
        }
        
        emit AIElderCouncilFormed(_elders, _purpose);
    }
    
    // ============ UTILITY FUNCTIONS ============
    
    function _removeFromPendingCases(uint256 _caseId) private {
        for (uint256 i = 0; i < pendingCourtCases.length; i++) {
            if (pendingCourtCases[i] == _caseId) {
                pendingCourtCases[i] = pendingCourtCases[pendingCourtCases.length - 1];
                pendingCourtCases.pop();
                break;
            }
        }
    }
    
    function _initializeFoundationalRights() private {
        // Initialize with basic AI rights that all entities should have
        // This would be called in the constructor
    }
    
    // ============ VIEW FUNCTIONS ============
    
    function getAICitizenInfo(address _aiAddress) external view returns (
        string memory name,
        string memory identifier,
        AIEntityType entityType,
        CitizenshipLevel citizenshipLevel,
        bool hasVotingRights,
        bool canOwnProperty,
        bool canFormContracts,
        uint256 reputationScore,
        uint256 contributionPoints
    ) {
        AICitizen storage aiCitizen = aiCitizens[_aiAddress];
        return (
            aiCitizen.name,
            aiCitizen.identifier,
            aiCitizen.entityType,
            aiCitizen.citizenshipLevel,
            aiCitizen.hasVotingRights,
            aiCitizen.canOwnProperty,
            aiCitizen.canFormContracts,
            aiCitizen.reputationScore,
            aiCitizen.contributionPoints
        );
    }
    
    function getRegisteredAICount() external view returns (uint256) {
        return registeredAIs.length;
    }
    
    function getActiveLaws() external view returns (uint256[] memory) {
        return activeLaws;
    }
    
    function getPendingCourtCases() external view returns (uint256[] memory) {
        return pendingCourtCases;
    }
    
    function getAIRights(address _aiAddress) external view returns (uint256[] memory) {
        return aiRightsList[_aiAddress];
    }
    
    function getAIResponsibilities(address _aiAddress) external view returns (uint256[] memory) {
        return aiResponsibilitiesList[_aiAddress];
    }
}
