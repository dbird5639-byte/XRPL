// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title Peace Protocol Infrastructure
 * @dev Technical foundation for international cooperation and peace agreements
 * @author Vision 2030+ Development Team
 * @notice Implements self-executing peace treaties, diplomatic protocols, and conflict resolution
 */

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract PeaceProtocolInfrastructure is ReentrancyGuard, Ownable {
    using Counters for Counters.Counter;
    
    // ============ ENUMS ============
    
    enum TreatyType {
        NonAggression,
        TradeAgreement,
        EnergyCooperation,
        TechnologySharing,
        EnvironmentalProtection,
        CulturalExchange,
        ScientificCollaboration,
        DefenseCooperation,
        EconomicPartnership,
        PeacefulResolution
    }
    
    enum ConflictLevel {
        Low,        // 0 - Minor disputes
        Medium,     // 1 - Regional tensions
        High,       // 2 - Significant conflicts
        Critical    // 3 - War-level conflicts
    }
    
    enum ResolutionStatus {
        Pending,
        InProgress,
        Resolved,
        Failed,
        Escalated
    }
    
    // ============ STRUCTS ============
    
    struct Nation {
        string name;
        string code;
        address representative;
        uint256 diplomaticWeight;
        bool isActive;
        uint256 joinedTimestamp;
        string[] alliances;
        uint256[] signedTreaties;
    }
    
    struct PeaceTreaty {
        uint256 id;
        string title;
        string description;
        TreatyType treatyType;
        address[] signatories;
        uint256[] requiredSignatures;
        uint256 creationDate;
        uint256 effectiveDate;
        uint256 expirationDate;
        bool isActive;
        bool isExecuted;
        string[] terms;
        uint256[] penalties;
        mapping(address => bool) hasSigned;
        mapping(address => bool) hasViolated;
    }
    
    struct ConflictResolution {
        uint256 id;
        string title;
        string description;
        address[] involvedParties;
        ConflictLevel conflictLevel;
        ResolutionStatus status;
        uint256 startDate;
        uint256 resolutionDate;
        address mediator;
        string[] proposedSolutions;
        uint256[] votesForSolution;
        string finalResolution;
        uint256[] penalties;
    }
    
    struct DiplomaticMission {
        uint256 id;
        string missionType;
        address[] participants;
        string destination;
        uint256 startDate;
        uint256 endDate;
        bool isActive;
        string[] objectives;
        string[] outcomes;
        uint256 successRating;
    }
    
    struct InternationalCourt {
        uint256 id;
        string caseTitle;
        address[] parties;
        address[] judges;
        uint256 filingDate;
        uint256 hearingDate;
        bool isResolved;
        string verdict;
        uint256[] penalties;
        string[] evidence;
    }
    
    // ============ STATE VARIABLES ============
    
    Counters.Counter private _treatyCounter;
    Counters.Counter private _conflictCounter;
    Counters.Counter private _missionCounter;
    Counters.Counter private _courtCaseCounter;
    
    mapping(string => Nation) public nations;
    mapping(uint256 => PeaceTreaty) public peaceTreaties;
    mapping(uint256 => ConflictResolution) public conflictResolutions;
    mapping(uint256 => DiplomaticMission) public diplomaticMissions;
    mapping(uint256 => InternationalCourt) public internationalCourtCases;
    
    mapping(address => bool) public isRegisteredNation;
    mapping(address => uint256[]) public nationTreaties;
    mapping(address => uint256[]) public nationConflicts;
    mapping(address => uint256[]) public nationMissions;
    
    string[] public nationCodes;
    uint256[] public activeTreaties;
    uint256[] public activeConflicts;
    uint256[] public activeMissions;
    uint256[] public pendingCourtCases;
    
    // Protocol constants
    uint256 public constant MIN_SIGNATURES_FOR_TREATY = 2;
    uint256 public constant TREATY_VALIDITY_PERIOD = 365 days;
    uint256 public constant CONFLICT_RESOLUTION_TIMEOUT = 30 days;
    uint256 public constant DIPLOMATIC_MISSION_DURATION = 7 days;
    
    // ============ EVENTS ============
    
    event NationRegistered(string indexed nationCode, address indexed representative, uint256 diplomaticWeight);
    event PeaceTreatyProposed(uint256 indexed treatyId, string title, TreatyType treatyType, address[] signatories);
    event TreatySigned(uint256 indexed treatyId, address indexed signatory, string nationCode);
    event TreatyExecuted(uint256 indexed treatyId, string title, uint256 effectiveDate);
    event TreatyViolated(uint256 indexed treatyId, address indexed violator, string violation);
    event ConflictReported(uint256 indexed conflictId, string title, ConflictLevel level, address[] parties);
    event ConflictResolved(uint256 indexed conflictId, string resolution, uint256 resolutionDate);
    event DiplomaticMissionLaunched(uint256 indexed missionId, string missionType, address[] participants);
    event DiplomaticMissionCompleted(uint256 indexed missionId, uint256 successRating, string[] outcomes);
    event InternationalCourtCaseFiled(uint256 indexed caseId, string caseTitle, address[] parties);
    event CourtVerdictReached(uint256 indexed caseId, string verdict, uint256[] penalties);
    event PeaceProtocolActivated(string protocol, string description);
    event CrossBorderCooperationEstablished(string indexed nationA, string indexed nationB, string cooperationType);
    
    // ============ MODIFIERS ============
    
    modifier onlyRegisteredNation() {
        require(isRegisteredNation[msg.sender], "Only registered nations can perform this action");
        _;
    }
    
    modifier onlyActiveTreaty(uint256 _treatyId) {
        require(peaceTreaties[_treatyId].isActive, "Treaty is not active");
        _;
    }
    
    modifier onlyTreatySignatory(uint256 _treatyId) {
        require(peaceTreaties[_treatyId].hasSigned[msg.sender], "Not a signatory of this treaty");
        _;
    }
    
    // ============ CONSTRUCTOR ============
    
    constructor() {
        _initializeFoundingNations();
    }
    
    // ============ NATION MANAGEMENT ============
    
    function registerNation(
        string memory _name,
        string memory _code,
        uint256 _diplomaticWeight
    ) external {
        require(!isRegisteredNation[msg.sender], "Nation already registered");
        require(_diplomaticWeight > 0, "Diplomatic weight must be greater than 0");
        
        nations[_code] = Nation({
            name: _name,
            code: _code,
            representative: msg.sender,
            diplomaticWeight: _diplomaticWeight,
            isActive: true,
            joinedTimestamp: block.timestamp,
            alliances: new string[](0),
            signedTreaties: new uint256[](0)
        });
        
        isRegisteredNation[msg.sender] = true;
        nationCodes.push(_code);
        
        emit NationRegistered(_code, msg.sender, _diplomaticWeight);
    }
    
    function _initializeFoundingNations() private {
        // Initialize with major nations for 2030+ vision
        // This would be called by the contract deployer
    }
    
    // ============ PEACE TREATY MANAGEMENT ============
    
    function proposePeaceTreaty(
        string memory _title,
        string memory _description,
        TreatyType _treatyType,
        address[] memory _signatories,
        string[] memory _terms,
        uint256 _effectiveDate
    ) external onlyRegisteredNation returns (uint256) {
        require(_signatories.length >= MIN_SIGNATURES_FOR_TREATY, "Insufficient signatories");
        require(_effectiveDate > block.timestamp, "Effective date must be in the future");
        require(_terms.length > 0, "Treaty must have terms");
        
        // Verify all signatories are registered nations
        for (uint256 i = 0; i < _signatories.length; i++) {
            require(isRegisteredNation[_signatories[i]], "All signatories must be registered nations");
        }
        
        _treatyCounter.increment();
        uint256 treatyId = _treatyCounter.current();
        
        PeaceTreaty storage treaty = peaceTreaties[treatyId];
        treaty.id = treatyId;
        treaty.title = _title;
        treaty.description = _description;
        treaty.treatyType = _treatyType;
        treaty.signatories = _signatories;
        treaty.creationDate = block.timestamp;
        treaty.effectiveDate = _effectiveDate;
        treaty.expirationDate = _effectiveDate + TREATY_VALIDITY_PERIOD;
        treaty.isActive = true;
        treaty.isExecuted = false;
        treaty.terms = _terms;
        
        activeTreaties.push(treatyId);
        
        emit PeaceTreatyProposed(treatyId, _title, _treatyType, _signatories);
        
        return treatyId;
    }
    
    function signPeaceTreaty(uint256 _treatyId) external onlyRegisteredNation onlyActiveTreaty(_treatyId) {
        PeaceTreaty storage treaty = peaceTreaties[_treatyId];
        require(!treaty.hasSigned[msg.sender], "Already signed this treaty");
        
        // Verify sender is a designated signatory
        bool isSignatory = false;
        for (uint256 i = 0; i < treaty.signatories.length; i++) {
            if (treaty.signatories[i] == msg.sender) {
                isSignatory = true;
                break;
            }
        }
        require(isSignatory, "Not authorized to sign this treaty");
        
        treaty.hasSigned[msg.sender] = true;
        treaty.requiredSignatures.push(1); // Track signatures
        
        // Add to nation's signed treaties
        nationTreaties[msg.sender].push(_treatyId);
        
        emit TreatySigned(_treatyId, msg.sender, _getNationCodeByAddress(msg.sender));
        
        // Check if treaty can be executed
        if (treaty.requiredSignatures.length >= treaty.signatories.length) {
            _executeTreaty(_treatyId);
        }
    }
    
    function _executeTreaty(uint256 _treatyId) private {
        PeaceTreaty storage treaty = peaceTreaties[_treatyId];
        treaty.isExecuted = true;
        
        // Activate peace protocol based on treaty type
        if (treaty.treatyType == TreatyType.NonAggression) {
            _activateNonAggressionProtocol(_treatyId);
        } else if (treaty.treatyType == TreatyType.EnergyCooperation) {
            _activateEnergyCooperationProtocol(_treatyId);
        } else if (treaty.treatyType == TreatyType.TradeAgreement) {
            _activateTradeCooperationProtocol(_treatyId);
        }
        
        emit TreatyExecuted(_treatyId, treaty.title, treaty.effectiveDate);
    }
    
    function _activateNonAggressionProtocol(uint256 _treatyId) private {
        PeaceTreaty storage treaty = peaceTreaties[_treatyId];
        emit PeaceProtocolActivated("NonAggression", treaty.description);
    }
    
    function _activateEnergyCooperationProtocol(uint256 _treatyId) private {
        PeaceTreaty storage treaty = peaceTreaties[_treatyId];
        emit CrossBorderCooperationEstablished(
            _getNationCodeByAddress(treaty.signatories[0]),
            _getNationCodeByAddress(treaty.signatories[1]),
            "EnergyCooperation"
        );
    }
    
    function _activateTradeCooperationProtocol(uint256 _treatyId) private {
        PeaceTreaty storage treaty = peaceTreaties[_treatyId];
        emit CrossBorderCooperationEstablished(
            _getNationCodeByAddress(treaty.signatories[0]),
            _getNationCodeByAddress(treaty.signatories[1]),
            "TradeCooperation"
        );
    }
    
    function reportTreatyViolation(uint256 _treatyId, address _violator, string memory _violation) external onlyRegisteredNation onlyActiveTreaty(_treatyId) {
        PeaceTreaty storage treaty = peaceTreaties[_treatyId];
        require(treaty.hasSigned[_violator], "Violator must be a treaty signatory");
        require(!treaty.hasViolated[_violator], "Violation already reported");
        
        treaty.hasViolated[_violator] = true;
        
        emit TreatyViolated(_treatyId, _violator, _violation);
        
        // Trigger conflict resolution if needed
        _triggerConflictResolution(_treatyId, _violator, _violation);
    }
    
    // ============ CONFLICT RESOLUTION ============
    
    function reportConflict(
        string memory _title,
        string memory _description,
        address[] memory _involvedParties,
        ConflictLevel _conflictLevel
    ) external onlyRegisteredNation returns (uint256) {
        require(_involvedParties.length >= 2, "Conflict must involve at least 2 parties");
        
        // Verify all parties are registered nations
        for (uint256 i = 0; i < _involvedParties.length; i++) {
            require(isRegisteredNation[_involvedParties[i]], "All parties must be registered nations");
        }
        
        _conflictCounter.increment();
        uint256 conflictId = _conflictCounter.current();
        
        conflictResolutions[conflictId] = ConflictResolution({
            id: conflictId,
            title: _title,
            description: _description,
            involvedParties: _involvedParties,
            conflictLevel: _conflictLevel,
            status: ResolutionStatus.Pending,
            startDate: block.timestamp,
            resolutionDate: 0,
            mediator: address(0),
            proposedSolutions: new string[](0),
            votesForSolution: new uint256[](0),
            finalResolution: "",
            penalties: new uint256[](0)
        });
        
        activeConflicts.push(conflictId);
        
        // Add to each party's conflict list
        for (uint256 i = 0; i < _involvedParties.length; i++) {
            nationConflicts[_involvedParties[i]].push(conflictId);
        }
        
        emit ConflictReported(conflictId, _title, _conflictLevel, _involvedParties);
        
        return conflictId;
    }
    
    function proposeConflictResolution(
        uint256 _conflictId,
        string memory _solution
    ) external onlyRegisteredNation {
        require(conflictResolutions[_conflictId].id != 0, "Conflict does not exist");
        require(conflictResolutions[_conflictId].status == ResolutionStatus.Pending, "Conflict not in pending status");
        
        conflictResolutions[_conflictId].proposedSolutions.push(_solution);
        conflictResolutions[_conflictId].votesForSolution.push(0);
    }
    
    function voteOnConflictResolution(
        uint256 _conflictId,
        uint256 _solutionIndex
    ) external onlyRegisteredNation {
        require(conflictResolutions[_conflictId].id != 0, "Conflict does not exist");
        require(_solutionIndex < conflictResolutions[_conflictId].proposedSolutions.length, "Invalid solution index");
        
        // Verify voter is involved in the conflict
        bool isInvolved = false;
        for (uint256 i = 0; i < conflictResolutions[_conflictId].involvedParties.length; i++) {
            if (conflictResolutions[_conflictId].involvedParties[i] == msg.sender) {
                isInvolved = true;
                break;
            }
        }
        require(isInvolved, "Not involved in this conflict");
        
        conflictResolutions[_conflictId].votesForSolution[_solutionIndex]++;
        
        // Check if resolution can be finalized
        _checkConflictResolution(_conflictId);
    }
    
    function _checkConflictResolution(uint256 _conflictId) private {
        ConflictResolution storage conflict = conflictResolutions[_conflictId];
        
        // Simple majority rule for resolution
        uint256 totalVotes = 0;
        uint256 maxVotes = 0;
        uint256 winningSolution = 0;
        
        for (uint256 i = 0; i < conflict.votesForSolution.length; i++) {
            totalVotes += conflict.votesForSolution[i];
            if (conflict.votesForSolution[i] > maxVotes) {
                maxVotes = conflict.votesForSolution[i];
                winningSolution = i;
            }
        }
        
        if (maxVotes > totalVotes / 2) {
            conflict.status = ResolutionStatus.Resolved;
            conflict.resolutionDate = block.timestamp;
            conflict.finalResolution = conflict.proposedSolutions[winningSolution];
            
            _removeFromActiveConflicts(_conflictId);
            
            emit ConflictResolved(_conflictId, conflict.finalResolution, conflict.resolutionDate);
        }
    }
    
    function _triggerConflictResolution(uint256 _treatyId, address _violator, string memory _violation) private {
        // Automatically trigger conflict resolution for treaty violations
        PeaceTreaty storage treaty = peaceTreaties[_treatyId];
        
        string memory conflictTitle = string(abi.encodePacked("Treaty Violation: ", treaty.title));
        string memory conflictDescription = string(abi.encodePacked("Violation of treaty terms: ", _violation));
        
        address[] memory parties = new address[](2);
        parties[0] = _violator;
        parties[1] = msg.sender; // Reporter
        
        reportConflict(conflictTitle, conflictDescription, parties, ConflictLevel.Medium);
    }
    
    // ============ DIPLOMATIC MISSIONS ============
    
    function launchDiplomaticMission(
        string memory _missionType,
        address[] memory _participants,
        string memory _destination,
        string[] memory _objectives,
        uint256 _duration
    ) external onlyRegisteredNation returns (uint256) {
        require(_participants.length > 0, "Mission must have participants");
        require(_duration <= DIPLOMATIC_MISSION_DURATION, "Mission duration too long");
        require(_objectives.length > 0, "Mission must have objectives");
        
        // Verify all participants are registered nations
        for (uint256 i = 0; i < _participants.length; i++) {
            require(isRegisteredNation[_participants[i]], "All participants must be registered nations");
        }
        
        _missionCounter.increment();
        uint256 missionId = _missionCounter.current();
        
        diplomaticMissions[missionId] = DiplomaticMission({
            id: missionId,
            missionType: _missionType,
            participants: _participants,
            destination: _destination,
            startDate: block.timestamp,
            endDate: block.timestamp + _duration,
            isActive: true,
            objectives: _objectives,
            outcomes: new string[](0),
            successRating: 0
        });
        
        activeMissions.push(missionId);
        
        // Add to each participant's mission list
        for (uint256 i = 0; i < _participants.length; i++) {
            nationMissions[_participants[i]].push(missionId);
        }
        
        emit DiplomaticMissionLaunched(missionId, _missionType, _participants);
        
        return missionId;
    }
    
    function completeDiplomaticMission(
        uint256 _missionId,
        string[] memory _outcomes,
        uint256 _successRating
    ) external onlyRegisteredNation {
        require(diplomaticMissions[_missionId].id != 0, "Mission does not exist");
        require(diplomaticMissions[_missionId].isActive, "Mission not active");
        require(_successRating <= 10, "Success rating must be between 0-10");
        
        // Verify sender is a mission participant
        bool isParticipant = false;
        for (uint256 i = 0; i < diplomaticMissions[_missionId].participants.length; i++) {
            if (diplomaticMissions[_missionId].participants[i] == msg.sender) {
                isParticipant = true;
                break;
            }
        }
        require(isParticipant, "Not a mission participant");
        
        diplomaticMissions[_missionId].isActive = false;
        diplomaticMissions[_missionId].outcomes = _outcomes;
        diplomaticMissions[_missionId].successRating = _successRating;
        
        _removeFromActiveMissions(_missionId);
        
        emit DiplomaticMissionCompleted(_missionId, _successRating, _outcomes);
    }
    
    // ============ INTERNATIONAL COURT ============
    
    function fileInternationalCourtCase(
        string memory _caseTitle,
        address[] memory _parties,
        address[] memory _judges,
        string[] memory _evidence
    ) external onlyRegisteredNation returns (uint256) {
        require(_parties.length >= 2, "Case must have at least 2 parties");
        require(_judges.length >= 3, "Case must have at least 3 judges");
        require(_evidence.length > 0, "Case must have evidence");
        
        _courtCaseCounter.increment();
        uint256 caseId = _courtCaseCounter.current();
        
        internationalCourtCases[caseId] = InternationalCourt({
            id: caseId,
            caseTitle: _caseTitle,
            parties: _parties,
            judges: _judges,
            filingDate: block.timestamp,
            hearingDate: block.timestamp + 7 days,
            isResolved: false,
            verdict: "",
            penalties: new uint256[](0),
            evidence: _evidence
        });
        
        pendingCourtCases.push(caseId);
        
        emit InternationalCourtCaseFiled(caseId, _caseTitle, _parties);
        
        return caseId;
    }
    
    function reachCourtVerdict(
        uint256 _caseId,
        string memory _verdict,
        uint256[] memory _penalties
    ) external onlyRegisteredNation {
        require(internationalCourtCases[_caseId].id != 0, "Case does not exist");
        require(!internationalCourtCases[_caseId].isResolved, "Case already resolved");
        
        // Verify sender is a judge
        bool isJudge = false;
        for (uint256 i = 0; i < internationalCourtCases[_caseId].judges.length; i++) {
            if (internationalCourtCases[_caseId].judges[i] == msg.sender) {
                isJudge = true;
                break;
            }
        }
        require(isJudge, "Not authorized to reach verdict");
        
        internationalCourtCases[_caseId].isResolved = true;
        internationalCourtCases[_caseId].verdict = _verdict;
        internationalCourtCases[_caseId].penalties = _penalties;
        
        _removeFromPendingCourtCases(_caseId);
        
        emit CourtVerdictReached(_caseId, _verdict, _penalties);
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
    
    function _removeFromActiveConflicts(uint256 _conflictId) private {
        for (uint256 i = 0; i < activeConflicts.length; i++) {
            if (activeConflicts[i] == _conflictId) {
                activeConflicts[i] = activeConflicts[activeConflicts.length - 1];
                activeConflicts.pop();
                break;
            }
        }
    }
    
    function _removeFromActiveMissions(uint256 _missionId) private {
        for (uint256 i = 0; i < activeMissions.length; i++) {
            if (activeMissions[i] == _missionId) {
                activeMissions[i] = activeMissions[activeMissions.length - 1];
                activeMissions.pop();
                break;
            }
        }
    }
    
    function _removeFromPendingCourtCases(uint256 _caseId) private {
        for (uint256 i = 0; i < pendingCourtCases.length; i++) {
            if (pendingCourtCases[i] == _caseId) {
                pendingCourtCases[i] = pendingCourtCases[pendingCourtCases.length - 1];
                pendingCourtCases.pop();
                break;
            }
        }
    }
    
    // ============ VIEW FUNCTIONS ============
    
    function getActiveTreaties() external view returns (uint256[] memory) {
        return activeTreaties;
    }
    
    function getActiveConflicts() external view returns (uint256[] memory) {
        return activeConflicts;
    }
    
    function getActiveMissions() external view returns (uint256[] memory) {
        return activeMissions;
    }
    
    function getPendingCourtCases() external view returns (uint256[] memory) {
        return pendingCourtCases;
    }
    
    function getNationCount() external view returns (uint256) {
        return nationCodes.length;
    }
    
    function getTreatyDetails(uint256 _treatyId) external view returns (
        string memory title,
        string memory description,
        TreatyType treatyType,
        uint256 creationDate,
        uint256 effectiveDate,
        uint256 expirationDate,
        bool isActive,
        bool isExecuted
    ) {
        PeaceTreaty storage treaty = peaceTreaties[_treatyId];
        return (
            treaty.title,
            treaty.description,
            treaty.treatyType,
            treaty.creationDate,
            treaty.effectiveDate,
            treaty.expirationDate,
            treaty.isActive,
            treaty.isExecuted
        );
    }
    
    function getConflictDetails(uint256 _conflictId) external view returns (
        string memory title,
        string memory description,
        ConflictLevel conflictLevel,
        ResolutionStatus status,
        uint256 startDate,
        string memory finalResolution
    ) {
        ConflictResolution storage conflict = conflictResolutions[_conflictId];
        return (
            conflict.title,
            conflict.description,
            conflict.conflictLevel,
            conflict.status,
            conflict.startDate,
            conflict.finalResolution
        );
    }
}
