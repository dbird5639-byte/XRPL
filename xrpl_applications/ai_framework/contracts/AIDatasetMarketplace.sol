// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AIDatasetMarketplace
 * @dev Marketplace for AI datasets with Ripple approval workflow
 */
contract AIDatasetMarketplace is Ownable, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    // Events
    event DatasetSubmitted(uint256 indexed datasetId, address indexed submitter, string name, string category);
    event DatasetApproved(uint256 indexed datasetId, address indexed approver);
    event DatasetRejected(uint256 indexed datasetId, address indexed approver, string reason);
    event DatasetPurchased(uint256 indexed datasetId, address indexed buyer, uint256 price);
    event DatasetUpdated(uint256 indexed datasetId, string newMetadata);
    
    // Structs
    struct Dataset {
        uint256 id;
        address submitter;
        string name;
        string description;
        string category;
        string metadataHash; // IPFS hash
        uint256 price;
        uint256 size; // in bytes
        uint256 qualityScore;
        ApprovalStatus status;
        uint256 submissionTime;
        uint256 approvalTime;
        address approver;
        string rejectionReason;
        bool isActive;
        uint256 purchaseCount;
        uint256 totalRevenue;
    }
    
    enum ApprovalStatus {
        Pending,
        Approved,
        Rejected,
        Suspended
    }
    
    // State variables
    Counters.Counter private _datasetIds;
    mapping(uint256 => Dataset) public datasets;
    mapping(address => uint256[]) public userDatasets;
    mapping(string => uint256[]) public categoryDatasets;
    mapping(address => bool) public approvedSubmitters;
    mapping(address => bool) public rippleApprovers;
    
    IERC20 public xrpToken;
    uint256 public platformFeePercent = 5; // 5% platform fee
    uint256 public minimumDatasetPrice = 100 * 10**6; // 100 XRP (6 decimals)
    uint256 public maximumDatasetPrice = 1000000 * 10**6; // 1M XRP
    
    // Quality thresholds
    uint256 public minimumQualityScore = 70;
    uint256 public minimumDatasetSize = 1024; // 1KB minimum
    
    constructor(address _xrpToken) {
        xrpToken = IERC20(_xrpToken);
        rippleApprovers[msg.sender] = true;
    }
    
    /**
     * @dev Submit a new dataset for approval
     */
    function submitDataset(
        string memory _name,
        string memory _description,
        string memory _category,
        string memory _metadataHash,
        uint256 _price,
        uint256 _size
    ) external whenNotPaused nonReentrant returns (uint256) {
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_description).length > 0, "Description cannot be empty");
        require(bytes(_category).length > 0, "Category cannot be empty");
        require(bytes(_metadataHash).length > 0, "Metadata hash cannot be empty");
        require(_price >= minimumDatasetPrice && _price <= maximumDatasetPrice, "Invalid price range");
        require(_size >= minimumDatasetSize, "Dataset too small");
        
        _datasetIds.increment();
        uint256 datasetId = _datasetIds.current();
        
        datasets[datasetId] = Dataset({
            id: datasetId,
            submitter: msg.sender,
            name: _name,
            description: _description,
            category: _category,
            metadataHash: _metadataHash,
            price: _price,
            size: _size,
            qualityScore: 0, // Will be set during approval
            status: ApprovalStatus.Pending,
            submissionTime: block.timestamp,
            approvalTime: 0,
            approver: address(0),
            rejectionReason: "",
            isActive: false,
            purchaseCount: 0,
            totalRevenue: 0
        });
        
        userDatasets[msg.sender].push(datasetId);
        categoryDatasets[_category].push(datasetId);
        
        emit DatasetSubmitted(datasetId, msg.sender, _name, _category);
        return datasetId;
    }
    
    /**
     * @dev Approve a dataset (only Ripple approvers)
     */
    function approveDataset(
        uint256 _datasetId,
        uint256 _qualityScore
    ) external onlyRippleApprover {
        require(_datasetId > 0 && _datasetId <= _datasetIds.current(), "Invalid dataset ID");
        Dataset storage dataset = datasets[_datasetId];
        require(dataset.status == ApprovalStatus.Pending, "Dataset not pending");
        require(_qualityScore >= minimumQualityScore, "Quality score too low");
        
        dataset.status = ApprovalStatus.Approved;
        dataset.qualityScore = _qualityScore;
        dataset.approvalTime = block.timestamp;
        dataset.approver = msg.sender;
        dataset.isActive = true;
        
        emit DatasetApproved(_datasetId, msg.sender);
    }
    
    /**
     * @dev Reject a dataset (only Ripple approvers)
     */
    function rejectDataset(
        uint256 _datasetId,
        string memory _reason
    ) external onlyRippleApprover {
        require(_datasetId > 0 && _datasetId <= _datasetIds.current(), "Invalid dataset ID");
        Dataset storage dataset = datasets[_datasetId];
        require(dataset.status == ApprovalStatus.Pending, "Dataset not pending");
        
        dataset.status = ApprovalStatus.Rejected;
        dataset.rejectionReason = _reason;
        dataset.approvalTime = block.timestamp;
        dataset.approver = msg.sender;
        
        emit DatasetRejected(_datasetId, msg.sender, _reason);
    }
    
    /**
     * @dev Purchase a dataset
     */
    function purchaseDataset(uint256 _datasetId) external whenNotPaused nonReentrant {
        require(_datasetId > 0 && _datasetId <= _datasetIds.current(), "Invalid dataset ID");
        Dataset storage dataset = datasets[_datasetId];
        require(dataset.status == ApprovalStatus.Approved, "Dataset not approved");
        require(dataset.isActive, "Dataset not active");
        require(dataset.submitter != msg.sender, "Cannot purchase own dataset");
        
        uint256 totalPrice = dataset.price;
        uint256 platformFee = (totalPrice * platformFeePercent) / 100;
        uint256 submitterRevenue = totalPrice - platformFee;
        
        // Transfer XRP tokens
        require(xrpToken.transferFrom(msg.sender, address(this), totalPrice), "Transfer failed");
        require(xrpToken.transfer(dataset.submitter, submitterRevenue), "Submitter transfer failed");
        
        // Update dataset statistics
        dataset.purchaseCount++;
        dataset.totalRevenue += submitterRevenue;
        
        emit DatasetPurchased(_datasetId, msg.sender, totalPrice);
    }
    
    /**
     * @dev Update dataset metadata (only submitter)
     */
    function updateDatasetMetadata(
        uint256 _datasetId,
        string memory _newMetadataHash
    ) external {
        require(_datasetId > 0 && _datasetId <= _datasetIds.current(), "Invalid dataset ID");
        Dataset storage dataset = datasets[_datasetId];
        require(dataset.submitter == msg.sender, "Not dataset submitter");
        require(dataset.status == ApprovalStatus.Approved, "Dataset not approved");
        
        dataset.metadataHash = _newMetadataHash;
        emit DatasetUpdated(_datasetId, _newMetadataHash);
    }
    
    /**
     * @dev Get dataset details
     */
    function getDataset(uint256 _datasetId) external view returns (Dataset memory) {
        require(_datasetId > 0 && _datasetId <= _datasetIds.current(), "Invalid dataset ID");
        return datasets[_datasetId];
    }
    
    /**
     * @dev Get datasets by category
     */
    function getDatasetsByCategory(string memory _category) external view returns (uint256[] memory) {
        return categoryDatasets[_category];
    }
    
    /**
     * @dev Get user's datasets
     */
    function getUserDatasets(address _user) external view returns (uint256[] memory) {
        return userDatasets[_user];
    }
    
    /**
     * @dev Get total number of datasets
     */
    function getTotalDatasets() external view returns (uint256) {
        return _datasetIds.current();
    }
    
    // Admin functions
    function addRippleApprover(address _approver) external onlyOwner {
        rippleApprovers[_approver] = true;
    }
    
    function removeRippleApprover(address _approver) external onlyOwner {
        rippleApprovers[_approver] = false;
    }
    
    function setPlatformFee(uint256 _feePercent) external onlyOwner {
        require(_feePercent <= 20, "Fee too high"); // Max 20%
        platformFeePercent = _feePercent;
    }
    
    function setPriceLimits(uint256 _minPrice, uint256 _maxPrice) external onlyOwner {
        minimumDatasetPrice = _minPrice;
        maximumDatasetPrice = _maxPrice;
    }
    
    function setQualityThresholds(uint256 _minScore, uint256 _minSize) external onlyOwner {
        minimumQualityScore = _minScore;
        minimumDatasetSize = _minSize;
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function withdrawPlatformFees() external onlyOwner {
        uint256 balance = xrpToken.balanceOf(address(this));
        require(balance > 0, "No fees to withdraw");
        require(xrpToken.transfer(owner(), balance), "Transfer failed");
    }
    
    // Modifiers
    modifier onlyRippleApprover() {
        require(rippleApprovers[msg.sender], "Not a Ripple approver");
        _;
    }
}
