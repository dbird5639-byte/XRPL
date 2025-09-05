// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/**
 * @title HealthcareRecords
 * @dev Smart contract for managing healthcare records and payments on XRPL
 */
contract HealthcareRecords is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // Events
    event PatientRegistered(
        address indexed patient,
        string patientId,
        uint256 timestamp
    );
    
    event DoctorRegistered(
        address indexed doctor,
        string doctorId,
        string specialization,
        uint256 timestamp
    );
    
    event RecordCreated(
        bytes32 indexed recordId,
        address indexed patient,
        address indexed doctor,
        string recordType,
        uint256 timestamp
    );
    
    event RecordAccessed(
        bytes32 indexed recordId,
        address indexed requester,
        address indexed patient,
        uint256 timestamp
    );
    
    event PaymentProcessed(
        bytes32 indexed paymentId,
        address indexed patient,
        address indexed doctor,
        uint256 amount,
        string service,
        uint256 timestamp
    );
    
    event InsuranceClaimSubmitted(
        bytes32 indexed claimId,
        address indexed patient,
        uint256 amount,
        string reason,
        uint256 timestamp
    );
    
    event PrescriptionIssued(
        bytes32 indexed prescriptionId,
        address indexed patient,
        address indexed doctor,
        string medication,
        uint256 quantity,
        uint256 timestamp
    );

    // Structs
    struct Patient {
        address patientAddress;
        string patientId;
        string name;
        uint256 dateOfBirth;
        string bloodType;
        string[] allergies;
        string[] chronicConditions;
        bool active;
        uint256 registrationTime;
    }
    
    struct Doctor {
        address doctorAddress;
        string doctorId;
        string name;
        string specialization;
        string licenseNumber;
        bool verified;
        bool active;
        uint256 registrationTime;
    }
    
    struct MedicalRecord {
        bytes32 recordId;
        address patient;
        address doctor;
        string recordType; // "consultation", "lab_result", "imaging", "prescription", etc.
        string diagnosis;
        string treatment;
        string notes;
        string[] attachments; // IPFS hashes or encrypted data
        uint256 timestamp;
        bool accessible;
    }
    
    struct Payment {
        bytes32 paymentId;
        address patient;
        address doctor;
        uint256 amount;
        string service;
        string description;
        bool processed;
        uint256 timestamp;
    }
    
    struct InsuranceClaim {
        bytes32 claimId;
        address patient;
        uint256 amount;
        string reason;
        string supportingDocuments;
        bool approved;
        bool processed;
        uint256 timestamp;
    }
    
    struct Prescription {
        bytes32 prescriptionId;
        address patient;
        address doctor;
        string medication;
        uint256 quantity;
        string dosage;
        string instructions;
        bool fulfilled;
        uint256 timestamp;
    }

    // State variables
    mapping(address => Patient) public patients;
    mapping(address => Doctor) public doctors;
    mapping(bytes32 => MedicalRecord) public medicalRecords;
    mapping(bytes32 => Payment) public payments;
    mapping(bytes32 => InsuranceClaim) public insuranceClaims;
    mapping(bytes32 => Prescription) public prescriptions;
    
    mapping(address => bool) public registeredPatients;
    mapping(address => bool) public registeredDoctors;
    mapping(address => bool) public authorizedAccess;
    
    mapping(address => bytes32[]) public patientRecords;
    mapping(address => bytes32[]) public doctorRecords;
    mapping(address => bytes32[]) public patientPayments;
    mapping(address => bytes32[]) public doctorPayments;
    
    IERC20 public paymentToken;
    address public insuranceProvider;
    address public pharmacyContract;
    
    uint256 public consultationFee = 5000; // 50 XRP in drops
    uint256 public recordAccessFee = 100; // 1 XRP in drops
    uint256 public platformFee = 50; // 0.5% in basis points
    
    uint256 public totalRecords;
    uint256 public totalPayments;
    uint256 public totalClaims;

    // Modifiers
    modifier onlyPatient() {
        require(registeredPatients[msg.sender], "Not a registered patient");
        _;
    }
    
    modifier onlyDoctor() {
        require(registeredDoctors[msg.sender], "Not a registered doctor");
        _;
    }
    
    modifier onlyAuthorized() {
        require(
            registeredPatients[msg.sender] || 
            registeredDoctors[msg.sender] || 
            authorizedAccess[msg.sender],
            "Not authorized"
        );
        _;
    }
    
    modifier validAmount(uint256 amount) {
        require(amount > 0, "Amount must be greater than 0");
        _;
    }

    constructor(
        address _paymentToken,
        address _insuranceProvider,
        address _pharmacyContract
    ) {
        paymentToken = IERC20(_paymentToken);
        insuranceProvider = _insuranceProvider;
        pharmacyContract = _pharmacyContract;
    }

    /**
     * @dev Register a new patient
     * @param patientId Unique patient identifier
     * @param name Patient's full name
     * @param dateOfBirth Date of birth (timestamp)
     * @param bloodType Blood type
     * @param allergies Array of known allergies
     * @param chronicConditions Array of chronic conditions
     */
    function registerPatient(
        string calldata patientId,
        string calldata name,
        uint256 dateOfBirth,
        string calldata bloodType,
        string[] calldata allergies,
        string[] calldata chronicConditions
    ) external {
        require(!registeredPatients[msg.sender], "Already registered");
        require(bytes(patientId).length > 0, "Invalid patient ID");
        require(bytes(name).length > 0, "Invalid name");
        
        patients[msg.sender] = Patient({
            patientAddress: msg.sender,
            patientId: patientId,
            name: name,
            dateOfBirth: dateOfBirth,
            bloodType: bloodType,
            allergies: allergies,
            chronicConditions: chronicConditions,
            active: true,
            registrationTime: block.timestamp
        });
        
        registeredPatients[msg.sender] = true;
        
        emit PatientRegistered(msg.sender, patientId, block.timestamp);
    }

    /**
     * @dev Register a new doctor
     * @param doctorId Unique doctor identifier
     * @param name Doctor's full name
     * @param specialization Medical specialization
     * @param licenseNumber Medical license number
     */
    function registerDoctor(
        string calldata doctorId,
        string calldata name,
        string calldata specialization,
        string calldata licenseNumber
    ) external {
        require(!registeredDoctors[msg.sender], "Already registered");
        require(bytes(doctorId).length > 0, "Invalid doctor ID");
        require(bytes(name).length > 0, "Invalid name");
        require(bytes(specialization).length > 0, "Invalid specialization");
        
        doctors[msg.sender] = Doctor({
            doctorAddress: msg.sender,
            doctorId: doctorId,
            name: name,
            specialization: specialization,
            licenseNumber: licenseNumber,
            verified: false, // Requires manual verification
            active: true,
            registrationTime: block.timestamp
        });
        
        registeredDoctors[msg.sender] = true;
        
        emit DoctorRegistered(msg.sender, doctorId, specialization, block.timestamp);
    }

    /**
     * @dev Create a new medical record
     * @param patient Patient's address
     * @param recordType Type of medical record
     * @param diagnosis Diagnosis
     * @param treatment Treatment provided
     * @param notes Additional notes
     * @param attachments Array of attachment hashes
     */
    function createMedicalRecord(
        address patient,
        string calldata recordType,
        string calldata diagnosis,
        string calldata treatment,
        string calldata notes,
        string[] calldata attachments
    ) external onlyDoctor {
        require(registeredPatients[patient], "Patient not registered");
        require(bytes(recordType).length > 0, "Invalid record type");
        
        bytes32 recordId = keccak256(abi.encodePacked(
            patient,
            msg.sender,
            recordType,
            block.timestamp,
            totalRecords
        ));
        
        medicalRecords[recordId] = MedicalRecord({
            recordId: recordId,
            patient: patient,
            doctor: msg.sender,
            recordType: recordType,
            diagnosis: diagnosis,
            treatment: treatment,
            notes: notes,
            attachments: attachments,
            timestamp: block.timestamp,
            accessible: true
        });
        
        patientRecords[patient].push(recordId);
        doctorRecords[msg.sender].push(recordId);
        totalRecords++;
        
        emit RecordCreated(recordId, patient, msg.sender, recordType, block.timestamp);
    }

    /**
     * @dev Access a medical record
     * @param recordId Record ID to access
     */
    function accessMedicalRecord(bytes32 recordId) external onlyAuthorized {
        require(medicalRecords[recordId].accessible, "Record not accessible");
        
        MedicalRecord storage record = medicalRecords[recordId];
        
        // Check if requester is authorized to access this record
        require(
            record.patient == msg.sender || 
            record.doctor == msg.sender || 
            authorizedAccess[msg.sender],
            "Not authorized to access this record"
        );
        
        // Charge access fee if not the patient or doctor
        if (record.patient != msg.sender && record.doctor != msg.sender) {
            paymentToken.safeTransferFrom(msg.sender, address(this), recordAccessFee);
        }
        
        emit RecordAccessed(recordId, msg.sender, record.patient, block.timestamp);
    }

    /**
     * @dev Process a payment for medical services
     * @param patient Patient's address
     * @param amount Payment amount
     * @param service Service provided
     * @param description Service description
     */
    function processPayment(
        address patient,
        uint256 amount,
        string calldata service,
        string calldata description
    ) external onlyDoctor validAmount(amount) {
        require(registeredPatients[patient], "Patient not registered");
        
        bytes32 paymentId = keccak256(abi.encodePacked(
            patient,
            msg.sender,
            amount,
            service,
            block.timestamp,
            totalPayments
        ));
        
        // Calculate platform fee
        uint256 fee = (amount * platformFee) / 10000;
        uint256 netAmount = amount - fee;
        
        // Transfer payment from patient
        paymentToken.safeTransferFrom(patient, address(this), amount);
        
        // Transfer fee to platform
        if (fee > 0) {
            paymentToken.safeTransfer(owner(), fee);
        }
        
        // Transfer net amount to doctor
        paymentToken.safeTransfer(msg.sender, netAmount);
        
        payments[paymentId] = Payment({
            paymentId: paymentId,
            patient: patient,
            doctor: msg.sender,
            amount: amount,
            service: service,
            description: description,
            processed: true,
            timestamp: block.timestamp
        });
        
        patientPayments[patient].push(paymentId);
        doctorPayments[msg.sender].push(paymentId);
        totalPayments++;
        
        emit PaymentProcessed(paymentId, patient, msg.sender, amount, service, block.timestamp);
    }

    /**
     * @dev Submit an insurance claim
     * @param amount Claim amount
     * @param reason Reason for claim
     * @param supportingDocuments Supporting document hashes
     */
    function submitInsuranceClaim(
        uint256 amount,
        string calldata reason,
        string calldata supportingDocuments
    ) external onlyPatient validAmount(amount) {
        bytes32 claimId = keccak256(abi.encodePacked(
            msg.sender,
            amount,
            reason,
            block.timestamp,
            totalClaims
        ));
        
        insuranceClaims[claimId] = InsuranceClaim({
            claimId: claimId,
            patient: msg.sender,
            amount: amount,
            reason: reason,
            supportingDocuments: supportingDocuments,
            approved: false,
            processed: false,
            timestamp: block.timestamp
        });
        
        totalClaims++;
        
        emit InsuranceClaimSubmitted(claimId, msg.sender, amount, reason, block.timestamp);
    }

    /**
     * @dev Issue a prescription
     * @param patient Patient's address
     * @param medication Medication name
     * @param quantity Quantity prescribed
     * @param dosage Dosage instructions
     * @param instructions Additional instructions
     */
    function issuePrescription(
        address patient,
        string calldata medication,
        uint256 quantity,
        string calldata dosage,
        string calldata instructions
    ) external onlyDoctor {
        require(registeredPatients[patient], "Patient not registered");
        require(quantity > 0, "Invalid quantity");
        
        bytes32 prescriptionId = keccak256(abi.encodePacked(
            patient,
            msg.sender,
            medication,
            quantity,
            block.timestamp
        ));
        
        prescriptions[prescriptionId] = Prescription({
            prescriptionId: prescriptionId,
            patient: patient,
            doctor: msg.sender,
            medication: medication,
            quantity: quantity,
            dosage: dosage,
            instructions: instructions,
            fulfilled: false,
            timestamp: block.timestamp
        });
        
        emit PrescriptionIssued(prescriptionId, patient, msg.sender, medication, quantity, block.timestamp);
    }

    /**
     * @dev Fulfill a prescription (called by pharmacy)
     * @param prescriptionId Prescription ID
     */
    function fulfillPrescription(bytes32 prescriptionId) external {
        require(msg.sender == pharmacyContract, "Only pharmacy can fulfill");
        require(prescriptions[prescriptionId].prescriptionId != bytes32(0), "Prescription not found");
        require(!prescriptions[prescriptionId].fulfilled, "Already fulfilled");
        
        prescriptions[prescriptionId].fulfilled = true;
    }

    // View functions
    function getPatient(address patient) external view returns (Patient memory) {
        return patients[patient];
    }
    
    function getDoctor(address doctor) external view returns (Doctor memory) {
        return doctors[doctor];
    }
    
    function getMedicalRecord(bytes32 recordId) external view returns (MedicalRecord memory) {
        return medicalRecords[recordId];
    }
    
    function getPayment(bytes32 paymentId) external view returns (Payment memory) {
        return payments[paymentId];
    }
    
    function getInsuranceClaim(bytes32 claimId) external view returns (InsuranceClaim memory) {
        return insuranceClaims[claimId];
    }
    
    function getPrescription(bytes32 prescriptionId) external view returns (Prescription memory) {
        return prescriptions[prescriptionId];
    }
    
    function getPatientRecords(address patient) external view returns (bytes32[] memory) {
        return patientRecords[patient];
    }
    
    function getDoctorRecords(address doctor) external view returns (bytes32[] memory) {
        return doctorRecords[doctor];
    }

    // Admin functions
    function verifyDoctor(address doctor) external onlyOwner {
        require(registeredDoctors[doctor], "Doctor not registered");
        doctors[doctor].verified = true;
    }
    
    function approveInsuranceClaim(bytes32 claimId) external onlyOwner {
        require(insuranceClaims[claimId].claimId != bytes32(0), "Claim not found");
        require(!insuranceClaims[claimId].processed, "Already processed");
        
        insuranceClaims[claimId].approved = true;
        insuranceClaims[claimId].processed = true;
        
        // Transfer claim amount to patient
        paymentToken.safeTransfer(
            insuranceClaims[claimId].patient,
            insuranceClaims[claimId].amount
        );
    }
    
    function addAuthorizedAccess(address account) external onlyOwner {
        authorizedAccess[account] = true;
    }
    
    function removeAuthorizedAccess(address account) external onlyOwner {
        authorizedAccess[account] = false;
    }
    
    function updateFees(
        uint256 newConsultationFee,
        uint256 newRecordAccessFee,
        uint256 newPlatformFee
    ) external onlyOwner {
        consultationFee = newConsultationFee;
        recordAccessFee = newRecordAccessFee;
        platformFee = newPlatformFee;
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }
}
