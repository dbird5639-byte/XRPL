// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title GamingRewards
 * @dev Smart contract for managing gaming rewards and micro-profits
 */
contract GamingRewards is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using Counters for Counters.Counter;

    // Events
    event GamePlayed(
        address indexed player,
        uint256 indexed gameId,
        uint256 betAmount,
        uint256 winAmount,
        bool won,
        uint256 timestamp
    );
    
    event RewardClaimed(
        address indexed player,
        uint256 amount,
        uint256 timestamp
    );
    
    event LeaderboardUpdated(
        address indexed player,
        uint256 score,
        uint256 rank
    );
    
    event TournamentCreated(
        uint256 indexed tournamentId,
        uint256 entryFee,
        uint256 prizePool,
        uint256 startTime,
        uint256 endTime
    );
    
    event TournamentJoined(
        uint256 indexed tournamentId,
        address indexed player,
        uint256 entryFee
    );
    
    event TournamentCompleted(
        uint256 indexed tournamentId,
        address indexed winner,
        uint256 prize
    );

    // Structs
    struct GameSession {
        uint256 gameId;
        address player;
        uint256 betAmount;
        uint256 winAmount;
        bool won;
        uint256 timestamp;
        uint256 score;
    }
    
    struct PlayerStats {
        uint256 totalGamesPlayed;
        uint256 totalWinnings;
        uint256 totalBets;
        uint256 currentStreak;
        uint256 bestStreak;
        uint256 level;
        uint256 experience;
        uint256 lastPlayTime;
    }
    
    struct Tournament {
        uint256 tournamentId;
        uint256 entryFee;
        uint256 prizePool;
        uint256 startTime;
        uint256 endTime;
        uint256 maxPlayers;
        uint256 currentPlayers;
        bool active;
        address[] participants;
        mapping(address => uint256) playerScores;
    }
    
    struct DailyChallenge {
        uint256 challengeId;
        string description;
        uint256 rewardAmount;
        uint256 targetValue;
        bool active;
        mapping(address => bool) completed;
        mapping(address => uint256) progress;
    }

    // State variables
    mapping(address => PlayerStats) public playerStats;
    mapping(uint256 => GameSession) public gameSessions;
    mapping(uint256 => Tournament) public tournaments;
    mapping(uint256 => DailyChallenge) public dailyChallenges;
    mapping(address => uint256) public pendingRewards;
    mapping(address => uint256) public lastClaimTime;
    
    Counters.Counter private _gameSessionIds;
    Counters.Counter private _tournamentIds;
    Counters.Counter private _challengeIds;
    
    IERC20 public rewardToken;
    IERC20 public betToken;
    
    uint256 public houseEdge = 200; // 2% in basis points
    uint256 public minBet = 1000; // Minimum bet amount
    uint256 public maxBet = 1000000; // Maximum bet amount
    uint256 public claimCooldown = 1 days;
    uint256 public platformFee = 50; // 0.5% in basis points
    
    address public feeRecipient;
    uint256 public totalVolume;
    uint256 public totalPayouts;
    
    // Modifiers
    modifier validBet(uint256 amount) {
        require(amount >= minBet && amount <= maxBet, "Invalid bet amount");
        _;
    }
    
    modifier canClaim() {
        require(
            block.timestamp >= lastClaimTime[msg.sender] + claimCooldown,
            "Claim cooldown not met"
        );
        _;
    }
    
    modifier validTournament(uint256 tournamentId) {
        require(tournamentId < _tournamentIds.current(), "Invalid tournament");
        require(tournaments[tournamentId].active, "Tournament not active");
        _;
    }

    constructor(
        address _rewardToken,
        address _betToken,
        address _feeRecipient
    ) {
        rewardToken = IERC20(_rewardToken);
        betToken = IERC20(_betToken);
        feeRecipient = _feeRecipient;
    }

    /**
     * @dev Play a game and potentially win rewards
     * @param gameType Type of game (1-5 for different games)
     * @param betAmount Amount to bet
     * @param playerChoice Player's choice/strategy
     */
    function playGame(
        uint256 gameType,
        uint256 betAmount,
        uint256 playerChoice
    ) external nonReentrant whenNotPaused validBet(betAmount) {
        require(gameType >= 1 && gameType <= 5, "Invalid game type");
        
        // Transfer bet amount
        betToken.safeTransferFrom(msg.sender, address(this), betAmount);
        
        // Calculate house edge
        uint256 houseFee = (betAmount * houseEdge) / 10000;
        uint256 platformFeeAmount = (betAmount * platformFee) / 10000;
        uint256 netBet = betAmount - houseFee - platformFeeAmount;
        
        // Transfer fees
        if (houseFee > 0) {
            betToken.safeTransfer(owner(), houseFee);
        }
        if (platformFeeAmount > 0) {
            betToken.safeTransfer(feeRecipient, platformFeeAmount);
        }
        
        // Generate game result (simplified random logic)
        uint256 randomSeed = uint256(keccak256(abi.encodePacked(
            block.timestamp,
            block.difficulty,
            msg.sender,
            betAmount,
            playerChoice
        )));
        
        bool won = _determineWin(gameType, playerChoice, randomSeed);
        uint256 winAmount = 0;
        uint256 score = 0;
        
        if (won) {
            // Calculate win amount based on game type and odds
            winAmount = _calculateWinAmount(gameType, netBet, randomSeed);
            pendingRewards[msg.sender] += winAmount;
            score = _calculateScore(gameType, betAmount, winAmount);
        }
        
        // Record game session
        uint256 sessionId = _gameSessionIds.current();
        _gameSessionIds.increment();
        
        gameSessions[sessionId] = GameSession({
            gameId: gameType,
            player: msg.sender,
            betAmount: betAmount,
            winAmount: winAmount,
            won: won,
            timestamp: block.timestamp,
            score: score
        });
        
        // Update player stats
        _updatePlayerStats(msg.sender, won, winAmount, betAmount, score);
        
        // Update global stats
        totalVolume += betAmount;
        if (won) {
            totalPayouts += winAmount;
        }
        
        emit GamePlayed(msg.sender, gameType, betAmount, winAmount, won, block.timestamp);
    }

    /**
     * @dev Claim pending rewards
     */
    function claimRewards() external nonReentrant canClaim {
        uint256 amount = pendingRewards[msg.sender];
        require(amount > 0, "No rewards to claim");
        
        pendingRewards[msg.sender] = 0;
        lastClaimTime[msg.sender] = block.timestamp;
        
        rewardToken.safeTransfer(msg.sender, amount);
        
        emit RewardClaimed(msg.sender, amount, block.timestamp);
    }

    /**
     * @dev Create a tournament
     * @param entryFee Entry fee for the tournament
     * @param duration Tournament duration in seconds
     * @param maxPlayers Maximum number of players
     */
    function createTournament(
        uint256 entryFee,
        uint256 duration,
        uint256 maxPlayers
    ) external onlyOwner {
        require(entryFee > 0, "Invalid entry fee");
        require(duration > 0, "Invalid duration");
        require(maxPlayers > 1, "Invalid max players");
        
        uint256 tournamentId = _tournamentIds.current();
        _tournamentIds.increment();
        
        Tournament storage tournament = tournaments[tournamentId];
        tournament.tournamentId = tournamentId;
        tournament.entryFee = entryFee;
        tournament.prizePool = 0;
        tournament.startTime = block.timestamp;
        tournament.endTime = block.timestamp + duration;
        tournament.maxPlayers = maxPlayers;
        tournament.currentPlayers = 0;
        tournament.active = true;
        
        emit TournamentCreated(tournamentId, entryFee, 0, block.timestamp, tournament.endTime);
    }

    /**
     * @dev Join a tournament
     * @param tournamentId Tournament ID
     */
    function joinTournament(uint256 tournamentId) external nonReentrant validTournament(tournamentId) {
        Tournament storage tournament = tournaments[tournamentId];
        
        require(tournament.currentPlayers < tournament.maxPlayers, "Tournament full");
        require(block.timestamp < tournament.endTime, "Tournament ended");
        require(tournament.playerScores[msg.sender] == 0, "Already joined");
        
        // Transfer entry fee
        betToken.safeTransferFrom(msg.sender, address(this), tournament.entryFee);
        
        tournament.prizePool += tournament.entryFee;
        tournament.currentPlayers++;
        tournament.participants.push(msg.sender);
        tournament.playerScores[msg.sender] = 0;
        
        emit TournamentJoined(tournamentId, msg.sender, tournament.entryFee);
    }

    /**
     * @dev Submit tournament score
     * @param tournamentId Tournament ID
     * @param score Player's score
     */
    function submitTournamentScore(uint256 tournamentId, uint256 score) external validTournament(tournamentId) {
        Tournament storage tournament = tournaments[tournamentId];
        
        require(tournament.playerScores[msg.sender] > 0 || tournament.participants.length > 0, "Not in tournament");
        require(block.timestamp <= tournament.endTime, "Tournament ended");
        
        tournament.playerScores[msg.sender] = score;
    }

    /**
     * @dev Complete tournament and distribute prizes
     * @param tournamentId Tournament ID
     */
    function completeTournament(uint256 tournamentId) external onlyOwner validTournament(tournamentId) {
        Tournament storage tournament = tournaments[tournamentId];
        
        require(block.timestamp >= tournament.endTime, "Tournament not ended");
        require(tournament.active, "Tournament already completed");
        
        tournament.active = false;
        
        // Find winner (simplified - highest score wins)
        address winner = address(0);
        uint256 highestScore = 0;
        
        for (uint256 i = 0; i < tournament.participants.length; i++) {
            address player = tournament.participants[i];
            uint256 score = tournament.playerScores[player];
            if (score > highestScore) {
                highestScore = score;
                winner = player;
            }
        }
        
        if (winner != address(0) && tournament.prizePool > 0) {
            // Transfer prize to winner
            betToken.safeTransfer(winner, tournament.prizePool);
            
            emit TournamentCompleted(tournamentId, winner, tournament.prizePool);
        }
    }

    /**
     * @dev Create daily challenge
     * @param description Challenge description
     * @param rewardAmount Reward amount
     * @param targetValue Target value to achieve
     */
    function createDailyChallenge(
        string calldata description,
        uint256 rewardAmount,
        uint256 targetValue
    ) external onlyOwner {
        uint256 challengeId = _challengeIds.current();
        _challengeIds.increment();
        
        DailyChallenge storage challenge = dailyChallenges[challengeId];
        challenge.challengeId = challengeId;
        challenge.description = description;
        challenge.rewardAmount = rewardAmount;
        challenge.targetValue = targetValue;
        challenge.active = true;
    }

    /**
     * @dev Complete daily challenge
     * @param challengeId Challenge ID
     * @param progress Progress made
     */
    function completeDailyChallenge(uint256 challengeId, uint256 progress) external {
        require(challengeId < _challengeIds.current(), "Invalid challenge");
        
        DailyChallenge storage challenge = dailyChallenges[challengeId];
        require(challenge.active, "Challenge not active");
        require(!challenge.completed[msg.sender], "Already completed");
        require(progress >= challenge.targetValue, "Target not met");
        
        challenge.completed[msg.sender] = true;
        challenge.progress[msg.sender] = progress;
        
        pendingRewards[msg.sender] += challenge.rewardAmount;
    }

    // View functions
    function getPlayerStats(address player) external view returns (PlayerStats memory) {
        return playerStats[player];
    }
    
    function getGameSession(uint256 sessionId) external view returns (GameSession memory) {
        return gameSessions[sessionId];
    }
    
    function getTournamentParticipants(uint256 tournamentId) external view returns (address[] memory) {
        return tournaments[tournamentId].participants;
    }
    
    function getTournamentScore(uint256 tournamentId, address player) external view returns (uint256) {
        return tournaments[tournamentId].playerScores[player];
    }
    
    function getPendingRewards(address player) external view returns (uint256) {
        return pendingRewards[player];
    }
    
    function getLeaderboard() external view returns (address[] memory, uint256[] memory) {
        // Simplified leaderboard - in production, use off-chain indexing
        address[] memory players = new address[](10);
        uint256[] memory scores = new uint256[](10);
        
        // This would be populated with actual leaderboard data
        return (players, scores);
    }

    // Internal functions
    function _determineWin(uint256 gameType, uint256 playerChoice, uint256 randomSeed) internal pure returns (bool) {
        // Simplified win logic - in production, implement proper game mechanics
        uint256 winChance = 0;
        
        if (gameType == 1) { // Simple dice game
            winChance = 4500; // 45% chance
        } else if (gameType == 2) { // Card game
            winChance = 4000; // 40% chance
        } else if (gameType == 3) { // Slot machine
            winChance = 3500; // 35% chance
        } else if (gameType == 4) { // Strategy game
            winChance = 5000 + (playerChoice * 100); // 50% + strategy bonus
        } else if (gameType == 5) { // Skill-based game
            winChance = 6000 + (playerChoice * 200); // 60% + skill bonus
        }
        
        return (randomSeed % 10000) < winChance;
    }
    
    function _calculateWinAmount(uint256 gameType, uint256 betAmount, uint256 randomSeed) internal pure returns (uint256) {
        uint256 multiplier = 0;
        
        if (gameType == 1) {
            multiplier = 20000; // 2x
        } else if (gameType == 2) {
            multiplier = 25000; // 2.5x
        } else if (gameType == 3) {
            multiplier = 30000; // 3x
        } else if (gameType == 4) {
            multiplier = 15000 + (randomSeed % 10000); // 1.5x - 2.5x
        } else if (gameType == 5) {
            multiplier = 12000 + (randomSeed % 8000); // 1.2x - 2x
        }
        
        return (betAmount * multiplier) / 10000;
    }
    
    function _calculateScore(uint256 gameType, uint256 betAmount, uint256 winAmount) internal pure returns (uint256) {
        uint256 baseScore = (betAmount * 10) / 1000; // Base score from bet
        uint256 winBonus = (winAmount * 20) / 1000; // Win bonus
        uint256 gameMultiplier = gameType * 100; // Game type multiplier
        
        return baseScore + winBonus + gameMultiplier;
    }
    
    function _updatePlayerStats(
        address player,
        bool won,
        uint256 winAmount,
        uint256 betAmount,
        uint256 score
    ) internal {
        PlayerStats storage stats = playerStats[player];
        
        stats.totalGamesPlayed++;
        stats.totalBets += betAmount;
        stats.lastPlayTime = block.timestamp;
        
        if (won) {
            stats.totalWinnings += winAmount;
            stats.currentStreak++;
            if (stats.currentStreak > stats.bestStreak) {
                stats.bestStreak = stats.currentStreak;
            }
        } else {
            stats.currentStreak = 0;
        }
        
        // Calculate experience and level
        stats.experience += score;
        stats.level = stats.experience / 10000; // Level up every 10k experience
    }

    // Admin functions
    function updateHouseEdge(uint256 newEdge) external onlyOwner {
        require(newEdge <= 1000, "House edge too high"); // Max 10%
        houseEdge = newEdge;
    }
    
    function updateBetLimits(uint256 newMinBet, uint256 newMaxBet) external onlyOwner {
        require(newMinBet > 0 && newMaxBet > newMinBet, "Invalid bet limits");
        minBet = newMinBet;
        maxBet = newMaxBet;
    }
    
    function updateClaimCooldown(uint256 newCooldown) external onlyOwner {
        claimCooldown = newCooldown;
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
