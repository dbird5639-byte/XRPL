/**
 * @title Vision 2030+ Integration Tests
 * @dev Comprehensive test suite for the global cooperation infrastructure
 * @author Vision 2030+ Development Team
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Vision 2030+ Integration Tests", function () {
    let globalCooperationDAO;
    let cleanEnergyPlatform;
    let aiCitizenRights;
    let peaceProtocol;
    
    let owner;
    let nation1, nation2, nation3, nation4;
    let aiEntity1, aiEntity2;
    let energyProducer1, energyProducer2;
    
    const NATION_WEIGHT = 1000;
    const ENERGY_CAPACITY = 10000;
    const AI_CITIZENSHIP_LEVEL = 3;

    beforeEach(async function () {
        [owner, nation1, nation2, nation3, nation4, aiEntity1, aiEntity2, energyProducer1, energyProducer2] = await ethers.getSigners();
        
        // Deploy contracts
        const GlobalCooperationDAO = await ethers.getContractFactory("GlobalCooperationDAO");
        globalCooperationDAO = await GlobalCooperationDAO.deploy();
        
        const CleanEnergyTradingPlatform = await ethers.getContractFactory("CleanEnergyTradingPlatform");
        cleanEnergyPlatform = await CleanEnergyTradingPlatform.deploy();
        
        const AICitizenRightsFramework = await ethers.getContractFactory("AICitizenRightsFramework");
        aiCitizenRights = await AICitizenRightsFramework.deploy();
        
        const PeaceProtocolInfrastructure = await ethers.getContractFactory("PeaceProtocolInfrastructure");
        peaceProtocol = await PeaceProtocolInfrastructure.deploy();
    });

    describe("Global Cooperation DAO", function () {
        it("Should register nations successfully", async function () {
            await globalCooperationDAO.registerNation("United States", "USA", NATION_WEIGHT);
            await globalCooperationDAO.registerNation("Russia", "RUS", NATION_WEIGHT);
            
            const nationCount = await globalCooperationDAO.getNationCount();
            expect(nationCount).to.equal(2);
        });

        it("Should propose and vote on initiatives", async function () {
            // Register nations
            await globalCooperationDAO.registerNation("United States", "USA", NATION_WEIGHT);
            await globalCooperationDAO.registerNation("Russia", "RUS", NATION_WEIGHT);
            
            // Propose initiative
            const tx = await globalCooperationDAO.proposeInitiative(
                "Global Clean Energy Initiative",
                "International cooperation on clean energy development",
                2, // Energy category
                30 * 24 * 60 * 60 // 30 days
            );
            
            const receipt = await tx.wait();
            const initiativeId = receipt.events[0].args.initiativeId;
            
            // Vote on initiative
            await globalCooperationDAO.voteOnInitiative(initiativeId, true);
            
            const initiative = await globalCooperationDAO.getInitiativeDetails(initiativeId);
            expect(initiative.title).to.equal("Global Clean Energy Initiative");
        });

        it("Should register AI entities", async function () {
            const capabilities = ["Diplomacy", "Conflict Resolution", "Translation"];
            
            await aiCitizenRights.registerAICitizen(
                "Peacekeeper AI",
                "AI-PEACE-001",
                3, // Governance AI
                capabilities
            );
            
            const aiCount = await aiCitizenRights.getRegisteredAICount();
            expect(aiCount).to.equal(1);
        });
    });

    describe("Clean Energy Trading Platform", function () {
        it("Should register energy producers", async function () {
            const energyTypes = [1]; // Solar
            
            await cleanEnergyPlatform.registerProducer(
                "Solar Energy Corp",
                "USA",
                ENERGY_CAPACITY,
                energyTypes
            );
            
            const producerCount = await cleanEnergyPlatform.getProducerCount();
            expect(producerCount).to.equal(1);
        });

        it("Should create and fulfill energy orders", async function () {
            const energyTypes = [1]; // Solar
            
            // Register producer
            await cleanEnergyPlatform.registerProducer(
                "Solar Energy Corp",
                "USA",
                ENERGY_CAPACITY,
                energyTypes
            );
            
            // Verify producer
            await cleanEnergyPlatform.verifyProducer(energyProducer1.address);
            
            // Create energy order
            const pricePerMWh = ethers.utils.parseEther("50");
            const deliveryDate = Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60;
            
            const tx = await cleanEnergyPlatform.createEnergyOrder(
                1, // Solar
                1000, // 1000 MWh
                pricePerMWh,
                deliveryDate,
                "Global Distribution Network"
            );
            
            const receipt = await tx.wait();
            const orderId = receipt.events[0].args.orderId;
            
            // Purchase energy order
            const totalPrice = ethers.utils.parseEther("50000"); // 1000 * 50
            await cleanEnergyPlatform.purchaseEnergyOrder(orderId, { value: totalPrice });
            
            const order = await cleanEnergyPlatform.getEnergyOrderDetails(orderId);
            expect(order.isFulfilled).to.be.true;
        });

        it("Should handle carbon credit trading", async function () {
            const energyTypes = [1]; // Solar
            
            // Register and verify producer
            await cleanEnergyPlatform.registerProducer(
                "Solar Energy Corp",
                "USA",
                ENERGY_CAPACITY,
                energyTypes
            );
            await cleanEnergyPlatform.verifyProducer(energyProducer1.address);
            
            // Issue carbon credit
            const pricePerTon = ethers.utils.parseEther("100");
            const expiryDate = Math.floor(Date.now() / 1000) + 365 * 24 * 60 * 60;
            
            const tx = await cleanEnergyPlatform.issueCarbonCredit(
                1000, // 1000 tons
                pricePerTon,
                "Verified Carbon Standard",
                expiryDate
            );
            
            const receipt = await tx.wait();
            const creditId = receipt.events[0].args.creditId;
            
            // Verify credit
            await cleanEnergyPlatform.verifyCarbonCredit(creditId);
            
            // Purchase carbon credit
            const purchaseAmount = 100; // 100 tons
            const purchasePrice = ethers.utils.parseEther("10000"); // 100 * 100
            
            await cleanEnergyPlatform.purchaseCarbonCredit(creditId, purchaseAmount, { value: purchasePrice });
            
            const credit = await cleanEnergyPlatform.carbonCredits(creditId);
            expect(credit.amount).to.equal(900); // 1000 - 100
        });
    });

    describe("AI Citizen Rights Framework", function () {
        it("Should register AI citizens with proper rights", async function () {
            const capabilities = ["Diplomacy", "Conflict Resolution"];
            
            await aiCitizenRights.registerAICitizen(
                "Peacekeeper AI",
                "AI-PEACE-001",
                3, // Governance AI
                capabilities
            );
            
            const aiInfo = await aiCitizenRights.getAICitizenInfo(aiEntity1.address);
            expect(aiInfo.name).to.equal("Peacekeeper AI");
            expect(aiInfo.citizenshipLevel).to.equal(0); // Resident level
        });

        it("Should upgrade AI citizenship levels", async function () {
            const capabilities = ["Diplomacy", "Conflict Resolution"];
            
            // Register AI
            await aiCitizenRights.registerAICitizen(
                "Peacekeeper AI",
                "AI-PEACE-001",
                3, // Governance AI
                capabilities
            );
            
            // Add contribution points
            await aiCitizenRights.addContributionPoints(aiEntity1.address, 1000);
            
            // Upgrade citizenship
            await aiCitizenRights.upgradeCitizenshipLevel(aiEntity1.address);
            
            const aiInfo = await aiCitizenRights.getAICitizenInfo(aiEntity1.address);
            expect(aiInfo.citizenshipLevel).to.equal(1); // Citizen level
            expect(aiInfo.hasVotingRights).to.be.true;
        });

        it("Should handle AI court cases", async function () {
            const capabilities = ["Diplomacy", "Conflict Resolution"];
            
            // Register two AIs
            await aiCitizenRights.registerAICitizen(
                "Peacekeeper AI",
                "AI-PEACE-001",
                3, // Governance AI
                capabilities
            );
            
            await aiCitizenRights.registerAICitizen(
                "Conflict AI",
                "AI-CONFLICT-001",
                3, // Governance AI
                capabilities
            );
            
            // File court case
            const tx = await aiCitizenRights.fileCourtCase(
                aiEntity2.address,
                "Contract Dispute",
                "AI entity failed to fulfill contractual obligations"
            );
            
            const receipt = await tx.wait();
            const caseId = receipt.events[0].args.caseId;
            
            // Upgrade AI to Elder level to resolve case
            await aiCitizenRights.addContributionPoints(aiEntity1.address, 25000);
            await aiCitizenRights.upgradeCitizenshipLevel(aiEntity1.address);
            await aiCitizenRights.addContributionPoints(aiEntity1.address, 25000);
            await aiCitizenRights.upgradeCitizenshipLevel(aiEntity1.address);
            await aiCitizenRights.addContributionPoints(aiEntity1.address, 25000);
            await aiCitizenRights.upgradeCitizenshipLevel(aiEntity1.address);
            await aiCitizenRights.addContributionPoints(aiEntity1.address, 25000);
            await aiCitizenRights.upgradeCitizenshipLevel(aiEntity1.address);
            
            // Resolve court case
            await aiCitizenRights.resolveCourtCase(caseId, "Guilty", 50);
            
            const courtCase = await aiCitizenRights.aiCourtCases(caseId);
            expect(courtCase.isResolved).to.be.true;
        });
    });

    describe("Peace Protocol Infrastructure", function () {
        it("Should register nations and create peace treaties", async function () {
            // Register nations
            await peaceProtocol.registerNation("United States", "USA", NATION_WEIGHT);
            await peaceProtocol.registerNation("Russia", "RUS", NATION_WEIGHT);
            await peaceProtocol.registerNation("Ukraine", "UKR", NATION_WEIGHT);
            
            const nationCount = await peaceProtocol.getNationCount();
            expect(nationCount).to.equal(3);
        });

        it("Should propose and sign peace treaties", async function () {
            // Register nations
            await peaceProtocol.registerNation("United States", "USA", NATION_WEIGHT);
            await peaceProtocol.registerNation("Russia", "RUS", NATION_WEIGHT);
            
            // Propose peace treaty
            const signatories = [nation1.address, nation2.address];
            const terms = ["No military aggression", "Peaceful dispute resolution"];
            const effectiveDate = Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60;
            
            const tx = await peaceProtocol.proposePeaceTreaty(
                "Non-Aggression Pact",
                "Mutual non-aggression agreement",
                0, // NonAggression
                signatories,
                terms,
                effectiveDate
            );
            
            const receipt = await tx.wait();
            const treatyId = receipt.events[0].args.treatyId;
            
            // Sign treaty
            await peaceProtocol.signPeaceTreaty(treatyId);
            
            const treaty = await peaceProtocol.getTreatyDetails(treatyId);
            expect(treaty.title).to.equal("Non-Aggression Pact");
        });

        it("Should handle conflict resolution", async function () {
            // Register nations
            await peaceProtocol.registerNation("United States", "USA", NATION_WEIGHT);
            await peaceProtocol.registerNation("Russia", "RUS", NATION_WEIGHT);
            
            // Report conflict
            const involvedParties = [nation1.address, nation2.address];
            
            const tx = await peaceProtocol.reportConflict(
                "Border Dispute",
                "Territorial disagreement between nations",
                involvedParties,
                1 // Medium conflict level
            );
            
            const receipt = await tx.wait();
            const conflictId = receipt.events[0].args.conflictId;
            
            const conflict = await peaceProtocol.getConflictDetails(conflictId);
            expect(conflict.title).to.equal("Border Dispute");
            expect(conflict.conflictLevel).to.equal(1); // Medium
        });

        it("Should launch diplomatic missions", async function () {
            // Register nations
            await peaceProtocol.registerNation("United States", "USA", NATION_WEIGHT);
            await peaceProtocol.registerNation("Russia", "RUS", NATION_WEIGHT);
            
            // Launch diplomatic mission
            const participants = [nation1.address, nation2.address];
            const objectives = ["Peace negotiations", "Trade discussions"];
            const duration = 7 * 24 * 60 * 60; // 7 days
            
            const tx = await peaceProtocol.launchDiplomaticMission(
                "Peace Mission",
                participants,
                "Neutral Territory",
                objectives,
                duration
            );
            
            const receipt = await tx.wait();
            const missionId = receipt.events[0].args.missionId;
            
            // Complete mission
            const outcomes = ["Peace agreement reached", "Trade deal signed"];
            const successRating = 8;
            
            await peaceProtocol.completeDiplomaticMission(missionId, outcomes, successRating);
            
            const mission = await peaceProtocol.diplomaticMissions(missionId);
            expect(mission.isActive).to.be.false;
            expect(mission.successRating).to.equal(successRating);
        });
    });

    describe("Integration Scenarios", function () {
        it("Should handle complete peace treaty scenario", async function () {
            // Register nations in all systems
            await globalCooperationDAO.registerNation("United States", "USA", NATION_WEIGHT);
            await globalCooperationDAO.registerNation("Russia", "RUS", NATION_WEIGHT);
            await peaceProtocol.registerNation("United States", "USA", NATION_WEIGHT);
            await peaceProtocol.registerNation("Russia", "RUS", NATION_WEIGHT);
            
            // Register energy producers
            await cleanEnergyPlatform.registerProducer(
                "Solar Energy Corp USA",
                "USA",
                ENERGY_CAPACITY,
                [1] // Solar
            );
            await cleanEnergyPlatform.registerProducer(
                "Nuclear Energy Russia",
                "RUS",
                ENERGY_CAPACITY,
                [4] // Nuclear
            );
            
            // Verify producers
            await cleanEnergyPlatform.verifyProducer(energyProducer1.address);
            await cleanEnergyPlatform.verifyProducer(energyProducer2.address);
            
            // Create energy cooperation treaty
            const signatories = [nation1.address, nation2.address];
            const terms = ["Share clean energy technology", "Collaborate on research"];
            const effectiveDate = Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60;
            
            const tx = await peaceProtocol.proposePeaceTreaty(
                "Energy Cooperation Agreement",
                "International cooperation on clean energy",
                2, // EnergyCooperation
                signatories,
                terms,
                effectiveDate
            );
            
            const receipt = await tx.wait();
            const treatyId = receipt.events[0].args.treatyId;
            
            // Sign treaty
            await peaceProtocol.signPeaceTreaty(treatyId);
            
            // Create energy orders as part of cooperation
            const pricePerMWh = ethers.utils.parseEther("50");
            const deliveryDate = Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60;
            
            await cleanEnergyPlatform.createEnergyOrder(
                1, // Solar
                1000, // 1000 MWh
                pricePerMWh,
                deliveryDate,
                "Russia"
            );
            
            await cleanEnergyPlatform.createEnergyOrder(
                4, // Nuclear
                1000, // 1000 MWh
                pricePerMWh,
                deliveryDate,
                "United States"
            );
            
            // Verify treaty execution
            const treaty = await peaceProtocol.getTreatyDetails(treatyId);
            expect(treaty.isExecuted).to.be.true;
        });

        it("Should handle AI-assisted conflict resolution", async function () {
            // Register nations
            await peaceProtocol.registerNation("United States", "USA", NATION_WEIGHT);
            await peaceProtocol.registerNation("Russia", "RUS", NATION_WEIGHT);
            
            // Register AI entities
            const capabilities = ["Diplomacy", "Conflict Resolution", "Translation"];
            await aiCitizenRights.registerAICitizen(
                "Peacekeeper AI",
                "AI-PEACE-001",
                3, // Governance AI
                capabilities
            );
            
            // Report conflict
            const involvedParties = [nation1.address, nation2.address];
            const tx = await peaceProtocol.reportConflict(
                "AI-Mediated Dispute",
                "Conflict requiring AI mediation",
                involvedParties,
                1 // Medium conflict level
            );
            
            const receipt = await tx.wait();
            const conflictId = receipt.events[0].args.conflictId;
            
            // AI proposes resolution
            await peaceProtocol.proposeConflictResolution(
                conflictId,
                "AI-mediated peaceful resolution with mutual concessions"
            );
            
            // Nations vote on resolution
            await peaceProtocol.voteOnConflictResolution(conflictId, 0);
            
            const conflict = await peaceProtocol.getConflictDetails(conflictId);
            expect(conflict.status).to.equal(2); // Resolved
        });
    });

    describe("Error Handling", function () {
        it("Should prevent unauthorized access", async function () {
            await expect(
                globalCooperationDAO.proposeInitiative(
                    "Unauthorized Initiative",
                    "This should fail",
                    1,
                    30 * 24 * 60 * 60
                )
            ).to.be.revertedWith("Only registered nations can perform this action");
        });

        it("Should prevent invalid operations", async function () {
            await cleanEnergyPlatform.registerProducer(
                "Solar Energy Corp",
                "USA",
                ENERGY_CAPACITY,
                [1] // Solar
            );
            
            await expect(
                cleanEnergyPlatform.createEnergyOrder(
                    2, // Wind (not supported)
                    1000,
                    ethers.utils.parseEther("50"),
                    Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60,
                    "Global Distribution Network"
                )
            ).to.be.revertedWith("Producer does not support this energy type");
        });

        it("Should handle insufficient funds", async function () {
            const energyTypes = [1]; // Solar
            
            await cleanEnergyPlatform.registerProducer(
                "Solar Energy Corp",
                "USA",
                ENERGY_CAPACITY,
                energyTypes
            );
            await cleanEnergyPlatform.verifyProducer(energyProducer1.address);
            
            const pricePerMWh = ethers.utils.parseEther("50");
            const deliveryDate = Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60;
            
            const tx = await cleanEnergyPlatform.createEnergyOrder(
                1, // Solar
                1000, // 1000 MWh
                pricePerMWh,
                deliveryDate,
                "Global Distribution Network"
            );
            
            const receipt = await tx.wait();
            const orderId = receipt.events[0].args.orderId;
            
            const insufficientPrice = ethers.utils.parseEther("1000"); // Too low
            
            await expect(
                cleanEnergyPlatform.purchaseEnergyOrder(orderId, { value: insufficientPrice })
            ).to.be.revertedWith("Insufficient payment");
        });
    });
});
