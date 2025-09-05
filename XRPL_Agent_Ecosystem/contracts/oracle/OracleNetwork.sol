// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title OracleNetwork
 * @dev Advanced oracle network for providing real-time data feeds to XRPL agents
 * @author XRPL Agent Ecosystem
 */
contract OracleNetwork is ReentrancyGuard, Pausable, Ownable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Data feed types
    enum DataFeedType {
        Price,
        Volume,
        MarketCap,
        TechnicalIndicator,
        News,
        SocialSentiment,
        OnChainMetric,
        Custom
    }

    // Oracle status
    enum OracleStatus {
        Active,
        Suspended,
        Deprecated
    }

    // Data feed structure
    struct DataFeed {
        uint256 feedId;
        string name;
        string description;
        DataFeedType feedType;
        address oracle;
        uint256 updateInterval;
        uint256 lastUpdate;
        uint256 price;
        uint256 decimals;
        bool isActive;
        string metadata;
        uint256[] historicalData;
        uint256[] timestamps;
    }

    // Oracle structure
    struct Oracle {
        address oracleAddress;
        string name;
        string description;
        OracleStatus status;
        uint256 reputation;
        uint256 totalFeeds;
        uint256 successfulUpdates;
        uint256 failedUpdates;
        uint256 stakedAmount;
        uint256 lastUpdate;
        bool isAuthorized;
        string[] supportedDataTypes;
        uint256[] feedIds;
    }

    // Data request structure
    struct DataRequest {
        uint256 requestId;
        address requester;
        uint256 feedId;
        uint256 timestamp;
        bool fulfilled;
        uint256 responseTime;
        string errorMessage;
    }

    // Events
    event DataFeedCreated(
        uint256 indexed feedId,
        address indexed oracle,
        string name,
        DataFeedType feedType
    );
    event DataUpdated(
        uint256 indexed feedId,
        address indexed oracle,
        uint256 newValue,
        uint256 timestamp
    );
    event OracleRegistered(
        address indexed oracle,
        string name,
        uint256 stakedAmount
    );
    event OracleStatusChanged(
        address indexed oracle,
        OracleStatus oldStatus,
        OracleStatus newStatus
    );
    event DataRequested(
        uint256 indexed requestId,
        address indexed requester,
        uint256 indexed feedId
    );
    event DataRequestFulfilled(
        uint256 indexed requestId,
        bool success,
        uint256 responseTime
    );

    // State variables
    mapping(uint256 => DataFeed) public dataFeeds;
    mapping(address => Oracle) public oracles;
    mapping(uint256 => DataRequest) public dataRequests;
    mapping(address => bool) public authorizedOracles;
    mapping(address => uint256[]) public oracleFeeds;
    mapping(address => uint256[]) public userRequests;
    
    uint256 public nextFeedId = 1;
    uint256 public nextRequestId = 1;
    uint256 public totalFeeds = 0;
    uint256 public totalOracles = 0;
    uint256 public totalRequests = 0;
    
    // Configuration
    uint256 public oracleStakeRequirement = 1000 * 1e18; // 1000 tokens
    uint256 public dataUpdateFee = 0.01 ether;
    uint256 public requestFee = 0.001 ether;
    uint256 public maxUpdateInterval = 1 hours;
    uint256 public minUpdateInterval = 1 minutes;
    uint256 public maxHistoricalData = 1000;
    uint256 public oracleRewardRate = 100; // 1%
    
    address public feeCollector;
    IERC20 public nativeToken;

    // Modifiers
    modifier onlyAuthorizedOracle() {
        require(authorizedOracles[msg.sender] || msg.sender == owner(), "Not authorized oracle");
        _;
    }

    modifier validFeed(uint256 feedId) {
        require(feedId > 0 && feedId < nextFeedId, "Invalid feed ID");
        _;
    }

    modifier validOracle(address oracle) {
        require(oracles[oracle].isAuthorized, "Oracle not authorized");
        _;
    }

    constructor(address _feeCollector, address _nativeToken) {
        feeCollector = _feeCollector;
        nativeToken = IERC20(_nativeToken);
    }

    /**
     * @dev Register a new oracle
     */
    function registerOracle(
        string memory name,
        string memory description,
        string[] memory supportedDataTypes
    ) external payable nonReentrant whenNotPaused returns (bool) {
        require(msg.value >= oracleStakeRequirement, "Insufficient stake");
        require(bytes(name).length > 0, "Name required");
        require(bytes(description).length > 0, "Description required");
        require(!oracles[msg.sender].isAuthorized, "Already registered");
        
        oracles[msg.sender] = Oracle({
            oracleAddress: msg.sender,
            name: name,
            description: description,
            status: OracleStatus.Active,
            reputation: 1000, // Starting reputation
            totalFeeds: 0,
            successfulUpdates: 0,
            failedUpdates: 0,
            stakedAmount: msg.value,
            lastUpdate: block.timestamp,
            isAuthorized: true,
            supportedDataTypes: supportedDataTypes,
            feedIds: new uint256[](0)
        });
        
        authorizedOracles[msg.sender] = true;
        totalOracles++;
        
        // Transfer stake to contract
        if (msg.value > 0) {
            payable(address(this)).transfer(msg.value);
        }
        
        emit OracleRegistered(msg.sender, name, msg.value);
        return true;
    }

    /**
     * @dev Create a new data feed
     */
    function createDataFeed(
        string memory name,
        string memory description,
        DataFeedType feedType,
        uint256 updateInterval,
        uint256 decimals,
        string memory metadata
    ) external onlyAuthorizedOracle nonReentrant whenNotPaused returns (uint256 feedId) {
        require(bytes(name).length > 0, "Name required");
        require(bytes(description).length > 0, "Description required");
        require(updateInterval >= minUpdateInterval && updateInterval <= maxUpdateInterval, "Invalid update interval");
        
        feedId = nextFeedId++;
        
        dataFeeds[feedId] = DataFeed({
            feedId: feedId,
            name: name,
            description: description,
            feedType: feedType,
            oracle: msg.sender,
            updateInterval: updateInterval,
            lastUpdate: 0,
            price: 0,
            decimals: decimals,
            isActive: true,
            metadata: metadata,
            historicalData: new uint256[](0),
            timestamps: new uint256[](0)
        });
        
        oracleFeeds[msg.sender].push(feedId);
        oracles[msg.sender].totalFeeds++;
        oracles[msg.sender].feedIds.push(feedId);
        totalFeeds++;
        
        emit DataFeedCreated(feedId, msg.sender, name, feedType);
    }

    /**
     * @dev Update data feed
     */
    function updateDataFeed(
        uint256 feedId,
        uint256 newValue
    ) external onlyAuthorizedOracle validFeed(feedId) nonReentrant whenNotPaused {
        DataFeed storage feed = dataFeeds[feedId];
        Oracle storage oracle = oracles[msg.sender];
        
        require(feed.oracle == msg.sender, "Not feed oracle");
        require(feed.isActive, "Feed not active");
        require(block.timestamp >= feed.lastUpdate + feed.updateInterval, "Update too frequent");
        
        // Update feed data
        feed.price = newValue;
        feed.lastUpdate = block.timestamp;
        
        // Add to historical data
        feed.historicalData.push(newValue);
        feed.timestamps.push(block.timestamp);
        
        // Maintain max historical data limit
        if (feed.historicalData.length > maxHistoricalData) {
            // Remove oldest data
            for (uint256 i = 0; i < feed.historicalData.length - 1; i++) {
                feed.historicalData[i] = feed.historicalData[i + 1];
                feed.timestamps[i] = feed.timestamps[i + 1];
            }
            feed.historicalData.pop();
            feed.timestamps.pop();
        }
        
        // Update oracle stats
        oracle.successfulUpdates++;
        oracle.lastUpdate = block.timestamp;
        
        // Calculate and distribute rewards
        uint256 reward = _calculateOracleReward(msg.sender);
        if (reward > 0) {
            payable(msg.sender).transfer(reward);
        }
        
        emit DataUpdated(feedId, msg.sender, newValue, block.timestamp);
    }

    /**
     * @dev Request data from a feed
     */
    function requestData(uint256 feedId) external payable nonReentrant whenNotPaused returns (uint256 requestId) {
        require(msg.value >= requestFee, "Insufficient fee");
        require(dataFeeds[feedId].isActive, "Feed not active");
        
        requestId = nextRequestId++;
        
        dataRequests[requestId] = DataRequest({
            requestId: requestId,
            requester: msg.sender,
            feedId: feedId,
            timestamp: block.timestamp,
            fulfilled: false,
            responseTime: 0,
            errorMessage: ""
        });
        
        userRequests[msg.sender].push(requestId);
        totalRequests++;
        
        // Transfer request fee
        if (msg.value > 0) {
            payable(feeCollector).transfer(msg.value);
        }
        
        emit DataRequested(requestId, msg.sender, feedId);
    }

    /**
     * @dev Fulfill data request
     */
    function fulfillDataRequest(
        uint256 requestId,
        uint256 data,
        bool success,
        string memory errorMessage
    ) external onlyAuthorizedOracle nonReentrant whenNotPaused {
        DataRequest storage request = dataRequests[requestId];
        Oracle storage oracle = oracles[msg.sender];
        
        require(!request.fulfilled, "Request already fulfilled");
        require(dataFeeds[request.feedId].oracle == msg.sender, "Not feed oracle");
        
        request.fulfilled = true;
        request.responseTime = block.timestamp - request.timestamp;
        
        if (success) {
            // Update feed with new data
            dataFeeds[request.feedId].price = data;
            dataFeeds[request.feedId].lastUpdate = block.timestamp;
            
            oracle.successfulUpdates++;
        } else {
            request.errorMessage = errorMessage;
            oracle.failedUpdates++;
        }
        
        oracle.lastUpdate = block.timestamp;
        
        emit DataRequestFulfilled(requestId, success, request.responseTime);
    }

    /**
     * @dev Get latest data from feed
     */
    function getLatestData(uint256 feedId) external view validFeed(feedId) returns (uint256, uint256) {
        DataFeed memory feed = dataFeeds[feedId];
        return (feed.price, feed.lastUpdate);
    }

    /**
     * @dev Get historical data from feed
     */
    function getHistoricalData(
        uint256 feedId,
        uint256 startIndex,
        uint256 count
    ) external view validFeed(feedId) returns (uint256[] memory, uint256[] memory) {
        DataFeed memory feed = dataFeeds[feedId];
        
        require(startIndex < feed.historicalData.length, "Invalid start index");
        
        uint256 endIndex = startIndex + count;
        if (endIndex > feed.historicalData.length) {
            endIndex = feed.historicalData.length;
        }
        
        uint256[] memory data = new uint256[](endIndex - startIndex);
        uint256[] memory timestamps = new uint256[](endIndex - startIndex);
        
        for (uint256 i = startIndex; i < endIndex; i++) {
            data[i - startIndex] = feed.historicalData[i];
            timestamps[i - startIndex] = feed.timestamps[i];
        }
        
        return (data, timestamps);
    }

    /**
     * @dev Get oracle information
     */
    function getOracle(address oracleAddress) external view returns (Oracle memory) {
        return oracles[oracleAddress];
    }

    /**
     * @dev Get data feed information
     */
    function getDataFeed(uint256 feedId) external view validFeed(feedId) returns (DataFeed memory) {
        return dataFeeds[feedId];
    }

    /**
     * @dev Search data feeds
     */
    function searchDataFeeds(
        string memory query,
        DataFeedType feedType
    ) external view returns (uint256[] memory) {
        uint256[] memory results = new uint256[](totalFeeds);
        uint256 count = 0;
        
        for (uint256 i = 1; i < nextFeedId; i++) {
            DataFeed memory feed = dataFeeds[i];
            
            if (feed.isActive) {
                if (feedType == DataFeedType.Custom || feed.feedType == feedType) {
                    // Simple string matching - could be enhanced
                    if (bytes(feed.name).length > 0) {
                        results[count] = i;
                        count++;
                    }
                }
            }
        }
        
        // Resize array
        uint256[] memory finalResults = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            finalResults[i] = results[i];
        }
        
        return finalResults;
    }

    /**
     * @dev Calculate oracle reward
     */
    function _calculateOracleReward(address oracle) internal view returns (uint256) {
        Oracle memory oracleData = oracles[oracle];
        
        if (oracleData.stakedAmount == 0) return 0;
        
        // Base reward calculation
        uint256 baseReward = oracleData.stakedAmount.mul(oracleRewardRate).div(10000);
        
        // Reputation multiplier
        uint256 reputationMultiplier = oracleData.reputation.div(1000);
        
        return baseReward.mul(reputationMultiplier).div(100);
    }

    /**
     * @dev Update oracle reputation
     */
    function updateOracleReputation(address oracle, int256 reputationChange) external onlyOwner {
        Oracle storage oracleData = oracles[oracle];
        
        if (reputationChange > 0) {
            oracleData.reputation = oracleData.reputation.add(uint256(reputationChange));
        } else {
            uint256 decrease = uint256(-reputationChange);
            if (oracleData.reputation > decrease) {
                oracleData.reputation = oracleData.reputation.sub(decrease);
            } else {
                oracleData.reputation = 0;
            }
        }
    }

    /**
     * @dev Change oracle status
     */
    function changeOracleStatus(address oracle, OracleStatus newStatus) external onlyOwner validOracle(oracle) {
        Oracle storage oracleData = oracles[oracle];
        OracleStatus oldStatus = oracleData.status;
        
        require(newStatus != oldStatus, "Status unchanged");
        
        oracleData.status = newStatus;
        
        if (newStatus == OracleStatus.Suspended || newStatus == OracleStatus.Deprecated) {
            authorizedOracles[oracle] = false;
        } else if (newStatus == OracleStatus.Active) {
            authorizedOracles[oracle] = true;
        }
        
        emit OracleStatusChanged(oracle, oldStatus, newStatus);
    }

    /**
     * @dev Unstake oracle
     */
    function unstakeOracle() external nonReentrant {
        Oracle storage oracleData = oracles[msg.sender];
        
        require(oracleData.isAuthorized, "Not authorized oracle");
        require(oracleData.stakedAmount > 0, "No stake to withdraw");
        
        uint256 stakedAmount = oracleData.stakedAmount;
        oracleData.stakedAmount = 0;
        
        // Deauthorize oracle
        oracleData.isAuthorized = false;
        authorizedOracles[msg.sender] = false;
        
        // Transfer stake back
        payable(msg.sender).transfer(stakedAmount);
    }

    /**
     * @dev Set configuration parameters
     */
    function setConfig(
        uint256 _oracleStakeRequirement,
        uint256 _dataUpdateFee,
        uint256 _requestFee,
        uint256 _maxUpdateInterval,
        uint256 _minUpdateInterval,
        uint256 _maxHistoricalData,
        uint256 _oracleRewardRate
    ) external onlyOwner {
        oracleStakeRequirement = _oracleStakeRequirement;
        dataUpdateFee = _dataUpdateFee;
        requestFee = _requestFee;
        maxUpdateInterval = _maxUpdateInterval;
        minUpdateInterval = _minUpdateInterval;
        maxHistoricalData = _maxHistoricalData;
        oracleRewardRate = _oracleRewardRate;
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

    /**
     * @dev Receive ETH
     */
    receive() external payable {
        // Allow contract to receive ETH for stakes and fees
    }
}
