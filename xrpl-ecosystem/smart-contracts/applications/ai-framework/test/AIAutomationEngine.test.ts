import { expect } from "chai";
import { ethers } from "hardhat";
import { AIAutomationEngine, AIAgentFactory, AIDatasetMarketplace, XRPToken } from "../typechain-types";

describe("AIAutomationEngine", function () {
  let automationEngine: AIAutomationEngine;
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

    // Deploy Automation Engine
    const AIAutomationEngine = await ethers.getContractFactory("AIAutomationEngine");
    automationEngine = await AIAutomationEngine.deploy(agentFactory.address, xrpToken.address);
    await automationEngine.deployed();

    // Setup
    await datasetMarketplace.addRippleApprover(approver.address);

    // Mint tokens
    await xrpToken.mint(creator.address, ethers.utils.parseUnits("10000", 6));
    await xrpToken.mint(user.address, ethers.utils.parseUnits("10000", 6));

    // Approve contracts
    await xrpToken.connect(creator).approve(automationEngine.address, ethers.utils.parseUnits("10000", 6));
    await xrpToken.connect(user).approve(automationEngine.address, ethers.utils.parseUnits("10000", 6));
  });

  describe("Task Creation", function () {
    let agentIds: number[];

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

      // Create agents
      await agentFactory.connect(creator).createAgent(
        "Agent 1",
        "First agent",
        "Testing",
        '{"model": "gpt-4"}'
      );
      await agentFactory.connect(creator).createAgent(
        "Agent 2",
        "Second agent",
        "Testing",
        '{"model": "gpt-3.5"}'
      );

      agentIds = [1, 2];
    });

    it("Should allow creating automation tasks", async function () {
      const tx = await automationEngine.connect(creator).createTask(
        "smart_contract",
        "Generate smart contract code",
        '{"language": "solidity", "version": "0.8.19"}',
        agentIds,
        Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
        false,
        0
      );

      await expect(tx)
        .to.emit(automationEngine, "AutomationTaskCreated")
        .withArgs(1, creator.address, "smart_contract", "Generate smart contract code");

      const task = await automationEngine.getTask(1);
      expect(task.taskType).to.equal("smart_contract");
      expect(task.creator).to.equal(creator.address);
      expect(task.agentIds.length).to.equal(2);
      expect(task.status).to.equal(1); // Scheduled
    });

    it("Should allow creating immediate tasks", async function () {
      const tx = await automationEngine.connect(creator).createTask(
        "data_analysis",
        "Analyze market data",
        '{"timeframe": "1d", "indicators": ["RSI", "MACD"]}',
        [1],
        Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
        false,
        0
      );

      const task = await automationEngine.getTask(1);
      expect(task.status).to.equal(0); // Created
    });

    it("Should reject empty task types", async function () {
      await expect(
        automationEngine.connect(creator).createTask(
          "",
          "Test task",
          '{}',
          agentIds,
          Math.floor(Date.now() / 1000) + 3600,
          false,
          0
        )
      ).to.be.revertedWith("Task type cannot be empty");
    });

    it("Should reject tasks with no agents", async function () {
      await expect(
        automationEngine.connect(creator).createTask(
          "smart_contract",
          "Test task",
          '{}',
          [],
          Math.floor(Date.now() / 1000) + 3600,
          false,
          0
        )
      ).to.be.revertedWith("Invalid agent count");
    });

    it("Should enforce maximum agents per task", async function () {
      // Create more agents
      for (let i = 3; i <= 7; i++) {
        await agentFactory.connect(creator).createAgent(
          `Agent ${i}`,
          `Test agent ${i}`,
          "Testing",
          '{"model": "gpt-4"}'
        );
      }

      const tooManyAgents = [1, 2, 3, 4, 5, 6]; // 6 agents, max is 5

      await expect(
        automationEngine.connect(creator).createTask(
          "smart_contract",
          "Test task",
          '{}',
          tooManyAgents,
          Math.floor(Date.now() / 1000) + 3600,
          false,
          0
        )
      ).to.be.revertedWith("Invalid agent count");
    });

    it("Should enforce maximum tasks per user", async function () {
      // Create 20 tasks (max limit)
      for (let i = 0; i < 20; i++) {
        await automationEngine.connect(creator).createTask(
          "data_analysis",
          `Task ${i}`,
          '{}',
          [1],
          Math.floor(Date.now() / 1000) + 3600,
          false,
          0
        );
      }

      // 21st task should fail
      await expect(
        automationEngine.connect(creator).createTask(
          "data_analysis",
          "Task 21",
          '{}',
          [1],
          Math.floor(Date.now() / 1000) + 3600,
          false,
          0
        )
      ).to.be.revertedWith("Max tasks per user exceeded");
    });
  });

  describe("Task Execution", function () {
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

      // Create agent
      await agentFactory.connect(creator).createAgent(
        "Test Agent",
        "Test agent",
        "Testing",
        '{"model": "gpt-4"}'
      );

      // Create task
      await automationEngine.connect(creator).createTask(
        "smart_contract",
        "Generate smart contract",
        '{"language": "solidity"}',
        [1],
        Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
        false,
        0
      );
    });

    it("Should allow owner to execute tasks", async function () {
      const tx = await automationEngine.connect(owner).executeTask(1, "Contract generated successfully");

      await expect(tx)
        .to.emit(automationEngine, "TaskExecuted")
        .withArgs(1, owner.address, true, "Contract generated successfully");

      const task = await automationEngine.getTask(1);
      expect(task.status).to.equal(3); // Completed
      expect(task.result).to.equal("Contract generated successfully");
    });

    it("Should not allow non-owners to execute tasks", async function () {
      await expect(
        automationEngine.connect(creator).executeTask(1, "Result")
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("Should not execute tasks that are not ready", async function () {
      // Create a scheduled task
      await automationEngine.connect(creator).createTask(
        "data_analysis",
        "Analyze data",
        '{}',
        [1],
        Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
        false,
        0
      );

      await expect(
        automationEngine.connect(owner).executeTask(2, "Result")
      ).to.be.revertedWith("Task not scheduled yet");
    });
  });

  describe("Task Cancellation", function () {
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

      // Create agent
      await agentFactory.connect(creator).createAgent(
        "Test Agent",
        "Test agent",
        "Testing",
        '{"model": "gpt-4"}'
      );

      // Create task
      await automationEngine.connect(creator).createTask(
        "smart_contract",
        "Generate smart contract",
        '{"language": "solidity"}',
        [1],
        Math.floor(Date.now() / 1000) + 3600,
        false,
        0
      );
    });

    it("Should allow task creators to cancel tasks", async function () {
      const tx = await automationEngine.connect(creator).cancelTask(1);

      await expect(tx)
        .to.emit(automationEngine, "TaskCancelled")
        .withArgs(1, creator.address);

      const task = await automationEngine.getTask(1);
      expect(task.status).to.equal(5); // Cancelled
    });

    it("Should not allow non-creators to cancel tasks", async function () {
      await expect(
        automationEngine.connect(user).cancelTask(1)
      ).to.be.revertedWith("Not task creator");
    });

    it("Should not allow cancelling completed tasks", async function () {
      // Execute the task first
      await automationEngine.connect(owner).executeTask(1, "Result");

      await expect(
        automationEngine.connect(creator).cancelTask(1)
      ).to.be.revertedWith("Cannot cancel");
    });
  });

  describe("Template Management", function () {
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

      // Create agents
      await agentFactory.connect(creator).createAgent(
        "Agent 1",
        "Test agent",
        "Testing",
        '{"model": "gpt-4"}'
      );
    });

    it("Should allow creating automation templates", async function () {
      const tx = await automationEngine.connect(creator).createTemplate(
        "DeFi Strategy Template",
        "Template for DeFi strategies",
        "defi_strategy",
        '{"protocol": "uniswap", "strategy": "arbitrage"}',
        [1],
        true,
        ethers.utils.parseUnits("50", 6)
      );

      await expect(tx)
        .to.emit(automationEngine, "AutomationTemplateCreated")
        .withArgs(1, creator.address, "DeFi Strategy Template");

      const template = await automationEngine.getTemplate(1);
      expect(template.name).to.equal("DeFi Strategy Template");
      expect(template.creator).to.equal(creator.address);
      expect(template.isPublic).to.be.true;
    });

    it("Should allow using public templates", async function () {
      // Create template
      await automationEngine.connect(creator).createTemplate(
        "Public Template",
        "A public template",
        "data_analysis",
        '{"timeframe": "1d"}',
        [1],
        true,
        ethers.utils.parseUnits("25", 6)
      );

      // Use template
      const tx = await automationEngine.connect(user).useTemplate(
        1,
        '{"timeframe": "7d", "custom": "value"}',
        Math.floor(Date.now() / 1000) + 3600
      );

      const task = await automationEngine.getTask(1);
      expect(task.taskType).to.equal("data_analysis");
      expect(task.description).to.equal("Template: Public Template");
    });

    it("Should not allow using private templates from other users", async function () {
      // Create private template
      await automationEngine.connect(creator).createTemplate(
        "Private Template",
        "A private template",
        "data_analysis",
        '{"timeframe": "1d"}',
        [1],
        false, // private
        ethers.utils.parseUnits("25", 6)
      );

      // Try to use template as different user
      await expect(
        automationEngine.connect(user).useTemplate(
          1,
          '{"timeframe": "7d"}',
          Math.floor(Date.now() / 1000) + 3600
        )
      ).to.be.revertedWith("Template not accessible");
    });
  });

  describe("Admin Functions", function () {
    it("Should allow owner to set fees", async function () {
      await automationEngine.setFees(
        ethers.utils.parseUnits("20", 6), // base execution fee
        ethers.utils.parseUnits("10", 6), // agent usage fee
        ethers.utils.parseUnits("50", 6), // template creation fee
        15 // platform fee percent
      );
      // Note: These would need to be public variables to test directly
    });

    it("Should allow owner to set limits", async function () {
      await automationEngine.setLimits(10, 50); // max agents per task, max tasks per user
      // Note: These would need to be public variables to test directly
    });

    it("Should allow owner to pause and unpause", async function () {
      await automationEngine.pause();
      expect(await automationEngine.paused()).to.be.true;

      await automationEngine.unpause();
      expect(await automationEngine.paused()).to.be.false;
    });
  });

  describe("Task Queries", function () {
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

      // Create agent
      await agentFactory.connect(creator).createAgent(
        "Test Agent",
        "Test agent",
        "Testing",
        '{"model": "gpt-4"}'
      );

      // Create multiple tasks
      await automationEngine.connect(creator).createTask(
        "smart_contract",
        "Generate contract",
        '{}',
        [1],
        Math.floor(Date.now() / 1000) + 3600,
        false,
        0
      );

      await automationEngine.connect(creator).createTask(
        "data_analysis",
        "Analyze data",
        '{}',
        [1],
        Math.floor(Date.now() / 1000) + 3600,
        false,
        0
      );
    });

    it("Should return user tasks", async function () {
      const userTasks = await automationEngine.getUserTasks(creator.address);
      expect(userTasks.length).to.equal(2);
      expect(userTasks[0]).to.equal(1);
      expect(userTasks[1]).to.equal(2);
    });

    it("Should return tasks by type", async function () {
      const smartContractTasks = await automationEngine.getTasksByType("smart_contract");
      const dataAnalysisTasks = await automationEngine.getTasksByType("data_analysis");

      expect(smartContractTasks.length).to.equal(1);
      expect(dataAnalysisTasks.length).to.equal(1);
      expect(smartContractTasks[0]).to.equal(1);
      expect(dataAnalysisTasks[0]).to.equal(2);
    });
  });
});
