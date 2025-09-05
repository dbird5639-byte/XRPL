import { expect } from "chai";
import { ethers } from "hardhat";
import { AIAgentFactory, AIDatasetMarketplace, XRPToken } from "../typechain-types";

describe("AIAgentFactory", function () {
  let agentFactory: AIAgentFactory;
  let datasetMarketplace: AIDatasetMarketplace;
  let xrpToken: XRPToken;
  let owner: any;
  let approver: any;
  let creator: any;
  let user: any;

  beforeEach(async function () {
    [owner, approver, creator, user] = await ethers.getSigners();

    // Deploy XRP Token
    const XRPToken = await ethers.getContractFactory("XRPToken");
    xrpToken = await XRPToken.deploy();
    await xrpToken.deployed();

    // Deploy Dataset Marketplace
    const AIDatasetMarketplace = await ethers.getContractFactory("AIDatasetMarketplace");
    datasetMarketplace = await AIDatasetMarketplace.deploy(xrpToken.address);
    await datasetMarketplace.deployed();

    // Deploy Agent Factory
    const AIAgentFactory = await ethers.getContractFactory("AIAgentFactory");
    agentFactory = await AIAgentFactory.deploy(xrpToken.address, datasetMarketplace.address);
    await agentFactory.deployed();

    // Setup
    await datasetMarketplace.addRippleApprover(approver.address);

    // Mint tokens
    await xrpToken.mint(creator.address, ethers.utils.parseUnits("10000", 6));
    await xrpToken.mint(user.address, ethers.utils.parseUnits("10000", 6));

    // Approve contracts
    await xrpToken.connect(creator).approve(agentFactory.address, ethers.utils.parseUnits("10000", 6));
    await xrpToken.connect(user).approve(agentFactory.address, ethers.utils.parseUnits("10000", 6));
  });

  describe("Agent Creation", function () {
    it("Should allow users to create agents", async function () {
      const tx = await agentFactory.connect(creator).createAgent(
        "Test Agent",
        "A test AI agent",
        "Automated trading",
        '{"model": "gpt-4", "temperature": 0.7}'
      );

      await expect(tx)
        .to.emit(agentFactory, "AgentCreated")
        .withArgs(1, creator.address, "Test Agent", "Automated trading");

      const agent = await agentFactory.getAgent(1);
      expect(agent.name).to.equal("Test Agent");
      expect(agent.creator).to.equal(creator.address);
      expect(agent.purpose).to.equal("Automated trading");
      expect(agent.isActive).to.be.true;
    });

    it("Should reject empty agent names", async function () {
      await expect(
        agentFactory.connect(creator).createAgent(
          "",
          "A test agent",
          "Automated trading",
          '{"model": "gpt-4"}'
        )
      ).to.be.revertedWith("Name cannot be empty");
    });

    it("Should enforce maximum agents per user", async function () {
      // Create 5 agents (max limit)
      for (let i = 0; i < 5; i++) {
        await agentFactory.connect(creator).createAgent(
          `Agent ${i}`,
          `Test agent ${i}`,
          "Testing",
          '{"model": "gpt-4"}'
        );
      }

      // 6th agent should fail
      await expect(
        agentFactory.connect(creator).createAgent(
          "Agent 6",
          "Test agent 6",
          "Testing",
          '{"model": "gpt-4"}'
        )
      ).to.be.revertedWith("Max agents per user exceeded");
    });
  });

  describe("Dataset Integration", function () {
    let datasetId: number;

    beforeEach(async function () {
      // Create and approve a dataset
      await datasetMarketplace.connect(creator).submitDataset(
        "Test Dataset",
        "A test dataset",
        "finance",
        "QmTestHash123",
        ethers.utils.parseUnits("500", 6),
        ethers.utils.parseUnits("1024", 0)
      );
      await datasetMarketplace.connect(approver).approveDataset(1, 85);
      datasetId = 1;

      // Create an agent
      await agentFactory.connect(creator).createAgent(
        "Test Agent",
        "A test agent",
        "Testing",
        '{"model": "gpt-4"}'
      );
    });

    it("Should allow adding datasets to agents", async function () {
      const tx = await agentFactory.connect(creator).addDatasetToAgent(1, datasetId, 1);

      await expect(tx)
        .to.emit(agentFactory, "DatasetAdded")
        .withArgs(1, datasetId, creator.address);

      const agentDatasets = await agentFactory.getAgentDatasets(1);
      expect(agentDatasets.length).to.equal(1);
      expect(agentDatasets[0]).to.equal(datasetId);
    });

    it("Should reject adding unapproved datasets", async function () {
      // Create unapproved dataset
      await datasetMarketplace.connect(creator).submitDataset(
        "Unapproved Dataset",
        "A test dataset",
        "finance",
        "QmTestHash456",
        ethers.utils.parseUnits("300", 6),
        ethers.utils.parseUnits("1024", 0)
      );

      await expect(
        agentFactory.connect(creator).addDatasetToAgent(1, 2, 1)
      ).to.be.revertedWith("Dataset not available");
    });

    it("Should enforce maximum datasets per agent", async function () {
      // Create and approve more datasets
      for (let i = 2; i <= 11; i++) {
        await datasetMarketplace.connect(creator).submitDataset(
          `Dataset ${i}`,
          `Test dataset ${i}`,
          "finance",
          `QmTestHash${i}`,
          ethers.utils.parseUnits("300", 6),
          ethers.utils.parseUnits("1024", 0)
        );
        await datasetMarketplace.connect(approver).approveDataset(i, 85);
      }

      // Add 10 datasets (max limit)
      for (let i = 1; i <= 10; i++) {
        await agentFactory.connect(creator).addDatasetToAgent(1, i, 1);
      }

      // 11th dataset should fail
      await expect(
        agentFactory.connect(creator).addDatasetToAgent(1, 11, 1)
      ).to.be.revertedWith("Max datasets per agent exceeded");
    });

    it("Should allow removing datasets from agents", async function () {
      await agentFactory.connect(creator).addDatasetToAgent(1, datasetId, 1);

      const tx = await agentFactory.connect(creator).removeDatasetFromAgent(1, datasetId);

      await expect(tx)
        .to.emit(agentFactory, "DatasetRemoved")
        .withArgs(1, datasetId, creator.address);

      const agentDatasets = await agentFactory.getAgentDatasets(1);
      expect(agentDatasets.length).to.equal(0);
    });
  });

  describe("Agent Deployment", function () {
    beforeEach(async function () {
      // Create and approve dataset
      await datasetMarketplace.connect(creator).submitDataset(
        "Test Dataset",
        "A test dataset",
        "finance",
        "QmTestHash123",
        ethers.utils.parseUnits("500", 6),
        ethers.utils.parseUnits("1024", 0)
      );
      await datasetMarketplace.connect(approver).approveDataset(1, 85);

      // Create agent and add dataset
      await agentFactory.connect(creator).createAgent(
        "Test Agent",
        "A test agent",
        "Testing",
        '{"model": "gpt-4"}'
      );
      await agentFactory.connect(creator).addDatasetToAgent(1, 1, 1);
    });

    it("Should allow deploying agents with datasets", async function () {
      const tx = await agentFactory.connect(creator).deployAgent(1);

      await expect(tx)
        .to.emit(agentFactory, "AgentDeployed");

      const agent = await agentFactory.getAgent(1);
      expect(agent.isDeployed).to.be.true;
      expect(agent.agentAddress).to.not.equal(ethers.constants.AddressZero);
    });

    it("Should not allow deploying agents without datasets", async function () {
      // Create agent without datasets
      await agentFactory.connect(creator).createAgent(
        "Empty Agent",
        "An agent without datasets",
        "Testing",
        '{"model": "gpt-4"}'
      );

      await expect(
        agentFactory.connect(creator).deployAgent(2)
      ).to.be.revertedWith("No datasets attached");
    });

    it("Should not allow deploying already deployed agents", async function () {
      await agentFactory.connect(creator).deployAgent(1);

      await expect(
        agentFactory.connect(creator).deployAgent(1)
      ).to.be.revertedWith("Agent already deployed");
    });
  });

  describe("Agent Management", function () {
    beforeEach(async function () {
      await agentFactory.connect(creator).createAgent(
        "Test Agent",
        "A test agent",
        "Testing",
        '{"model": "gpt-4"}'
      );
    });

    it("Should allow updating agent configuration", async function () {
      const newConfig = '{"model": "gpt-4-turbo", "temperature": 0.5}';
      const tx = await agentFactory.connect(creator).updateAgentConfiguration(1, newConfig);

      await expect(tx)
        .to.emit(agentFactory, "AgentUpdated")
        .withArgs(1, newConfig);

      const agent = await agentFactory.getAgent(1);
      expect(agent.configuration).to.equal(newConfig);
    });

    it("Should allow destroying agents", async function () {
      const tx = await agentFactory.connect(creator).destroyAgent(1);

      await expect(tx)
        .to.emit(agentFactory, "AgentDestroyed")
        .withArgs(1, creator.address);

      const agent = await agentFactory.getAgent(1);
      expect(agent.isActive).to.be.false;
    });

    it("Should not allow non-creators to manage agents", async function () {
      await expect(
        agentFactory.connect(user).updateAgentConfiguration(1, '{"model": "gpt-4"}')
      ).to.be.revertedWith("Not agent creator");

      await expect(
        agentFactory.connect(user).destroyAgent(1)
      ).to.be.revertedWith("Not agent creator");
    });
  });

  describe("Admin Functions", function () {
    it("Should allow owner to set fees", async function () {
      await agentFactory.setFees(
        ethers.utils.parseUnits("100", 6), // creation fee
        ethers.utils.parseUnits("20", 6),  // dataset access fee
        ethers.utils.parseUnits("200", 6)  // deployment fee
      );

      // Note: These would need to be public variables to test directly
      // For now, we test that the function doesn't revert
    });

    it("Should allow owner to set limits", async function () {
      await agentFactory.setLimits(15, 10); // max datasets, max agents
      // Note: These would need to be public variables to test directly
    });

    it("Should allow owner to pause and unpause", async function () {
      await agentFactory.pause();
      expect(await agentFactory.paused()).to.be.true;

      await agentFactory.unpause();
      expect(await agentFactory.paused()).to.be.false;
    });
  });

  describe("Agent Queries", function () {
    beforeEach(async function () {
      // Create multiple agents
      await agentFactory.connect(creator).createAgent(
        "Agent 1",
        "First agent",
        "Testing 1",
        '{"model": "gpt-4"}'
      );

      await agentFactory.connect(creator).createAgent(
        "Agent 2",
        "Second agent",
        "Testing 2",
        '{"model": "gpt-3.5"}'
      );
    });

    it("Should return user agents", async function () {
      const userAgents = await agentFactory.getUserAgents(creator.address);
      expect(userAgents.length).to.equal(2);
      expect(userAgents[0]).to.equal(1);
      expect(userAgents[1]).to.equal(2);
    });

    it("Should return total agent count", async function () {
      const totalAgents = await agentFactory.getTotalAgents();
      expect(totalAgents).to.equal(2);
    });
  });
});
