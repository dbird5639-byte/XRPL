const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");

describe("XRPL Ecosystem Smart Contracts", function () {
  async function deployXRPLEcosystemFixture() {
    const [owner, user1, user2, user3] = await ethers.getSigners();

    // Deploy XRP Token
    const XRPToken = await ethers.getContractFactory("XRPToken");
    const xrpToken = await XRPToken.deploy();
    await xrpToken.deployed();

    // Deploy XRPL Bridge
    const XRPLBridge = await ethers.getContractFactory("XRPLBridge");
    const xrplBridge = await XRPLBridge.deploy(xrpToken.address);
    await xrplBridge.deployed();

    // Deploy DeFi Protocol
    const DeFiProtocol = await ethers.getContractFactory("DeFiProtocol");
    const defiProtocol = await DeFiProtocol.deploy(xrpToken.address);
    await defiProtocol.deployed();

    // Deploy NFT Marketplace
    const NFTMarketplace = await ethers.getContractFactory("NFTMarketplace");
    const nftMarketplace = await NFTMarketplace.deploy();
    await nftMarketplace.deployed();

    // Deploy AI Agent Factory
    const AIAgentFactory = await ethers.getContractFactory("AIAgentFactory");
    const aiAgentFactory = await AIAgentFactory.deploy();
    await aiAgentFactory.deployed();

    // Deploy AI Automation Engine
    const AIAutomationEngine = await ethers.getContractFactory("AIAutomationEngine");
    const aiAutomationEngine = await AIAutomationEngine.deploy(aiAgentFactory.address);
    await aiAutomationEngine.deployed();

    return {
      xrpToken,
      xrplBridge,
      defiProtocol,
      nftMarketplace,
      aiAgentFactory,
      aiAutomationEngine,
      owner,
      user1,
      user2,
      user3,
    };
  }

  describe("XRP Token", function () {
    it("Should deploy with correct name and symbol", async function () {
      const { xrpToken } = await loadFixture(deployXRPLEcosystemFixture);
      
      expect(await xrpToken.name()).to.equal("XRP Token");
      expect(await xrpToken.symbol()).to.equal("XRP");
      expect(await xrpToken.decimals()).to.equal(18);
    });

    it("Should mint tokens to owner", async function () {
      const { xrpToken, owner } = await loadFixture(deployXRPLEcosystemFixture);
      
      const mintAmount = ethers.utils.parseEther("1000000");
      await xrpToken.mint(owner.address, mintAmount);
      
      expect(await xrpToken.balanceOf(owner.address)).to.equal(mintAmount);
    });

    it("Should allow transfers between users", async function () {
      const { xrpToken, owner, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      const transferAmount = ethers.utils.parseEther("1000");
      await xrpToken.mint(owner.address, transferAmount);
      await xrpToken.transfer(user1.address, transferAmount);
      
      expect(await xrpToken.balanceOf(user1.address)).to.equal(transferAmount);
    });
  });

  describe("XRPL Bridge", function () {
    it("Should deploy with correct XRP token address", async function () {
      const { xrplBridge, xrpToken } = await loadFixture(deployXRPLEcosystemFixture);
      
      expect(await xrplBridge.xrpToken()).to.equal(xrpToken.address);
    });

    it("Should allow locking tokens for bridge", async function () {
      const { xrplBridge, xrpToken, owner } = await loadFixture(deployXRPLEcosystemFixture);
      
      const lockAmount = ethers.utils.parseEther("1000");
      await xrpToken.mint(owner.address, lockAmount);
      await xrpToken.approve(xrplBridge.address, lockAmount);
      
      await xrplBridge.lockTokens(lockAmount);
      expect(await xrpToken.balanceOf(xrplBridge.address)).to.equal(lockAmount);
    });

    it("Should emit BridgeLocked event", async function () {
      const { xrplBridge, xrpToken, owner } = await loadFixture(deployXRPLEcosystemFixture);
      
      const lockAmount = ethers.utils.parseEther("1000");
      await xrpToken.mint(owner.address, lockAmount);
      await xrpToken.approve(xrplBridge.address, lockAmount);
      
      await expect(xrplBridge.lockTokens(lockAmount))
        .to.emit(xrplBridge, "BridgeLocked")
        .withArgs(owner.address, lockAmount);
    });
  });

  describe("DeFi Protocol", function () {
    it("Should deploy with correct XRP token address", async function () {
      const { defiProtocol, xrpToken } = await loadFixture(deployXRPLEcosystemFixture);
      
      expect(await defiProtocol.xrpToken()).to.equal(xrpToken.address);
    });

    it("Should allow users to deposit tokens", async function () {
      const { defiProtocol, xrpToken, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      const depositAmount = ethers.utils.parseEther("1000");
      await xrpToken.mint(user1.address, depositAmount);
      await xrpToken.connect(user1).approve(defiProtocol.address, depositAmount);
      
      await defiProtocol.connect(user1).deposit(depositAmount);
      expect(await defiProtocol.getUserBalance(user1.address)).to.equal(depositAmount);
    });

    it("Should allow users to withdraw tokens", async function () {
      const { defiProtocol, xrpToken, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      const depositAmount = ethers.utils.parseEther("1000");
      await xrpToken.mint(user1.address, depositAmount);
      await xrpToken.connect(user1).approve(defiProtocol.address, depositAmount);
      await defiProtocol.connect(user1).deposit(depositAmount);
      
      const withdrawAmount = ethers.utils.parseEther("500");
      await defiProtocol.connect(user1).withdraw(withdrawAmount);
      expect(await defiProtocol.getUserBalance(user1.address)).to.equal(depositAmount.sub(withdrawAmount));
    });
  });

  describe("NFT Marketplace", function () {
    it("Should allow users to create NFT listings", async function () {
      const { nftMarketplace, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      const tokenId = 1;
      const price = ethers.utils.parseEther("1");
      
      await nftMarketplace.connect(user1).createListing(tokenId, price);
      
      const listing = await nftMarketplace.getListing(tokenId);
      expect(listing.seller).to.equal(user1.address);
      expect(listing.price).to.equal(price);
      expect(listing.active).to.be.true;
    });

    it("Should allow users to buy NFTs", async function () {
      const { nftMarketplace, user1, user2 } = await loadFixture(deployXRPLEcosystemFixture);
      
      const tokenId = 1;
      const price = ethers.utils.parseEther("1");
      
      await nftMarketplace.connect(user1).createListing(tokenId, price);
      await nftMarketplace.connect(user2).buyNFT(tokenId, { value: price });
      
      const listing = await nftMarketplace.getListing(tokenId);
      expect(listing.active).to.be.false;
    });
  });

  describe("AI Agent Factory", function () {
    it("Should allow users to create AI agents", async function () {
      const { aiAgentFactory, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      const agentName = "Test Agent";
      const agentDescription = "A test AI agent";
      
      await aiAgentFactory.connect(user1).createAgent(agentName, agentDescription);
      
      const agentCount = await aiAgentFactory.getAgentCount();
      expect(agentCount).to.equal(1);
    });

    it("Should return correct agent information", async function () {
      const { aiAgentFactory, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      const agentName = "Test Agent";
      const agentDescription = "A test AI agent";
      
      await aiAgentFactory.connect(user1).createAgent(agentName, agentDescription);
      
      const agent = await aiAgentFactory.getAgent(0);
      expect(agent.name).to.equal(agentName);
      expect(agent.description).to.equal(agentDescription);
      expect(agent.owner).to.equal(user1.address);
    });
  });

  describe("AI Automation Engine", function () {
    it("Should deploy with correct AI Agent Factory address", async function () {
      const { aiAutomationEngine, aiAgentFactory } = await loadFixture(deployXRPLEcosystemFixture);
      
      expect(await aiAutomationEngine.aiAgentFactory()).to.equal(aiAgentFactory.address);
    });

    it("Should allow users to create automation workflows", async function () {
      const { aiAutomationEngine, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      const workflowName = "Test Workflow";
      const workflowDescription = "A test automation workflow";
      
      await aiAutomationEngine.connect(user1).createWorkflow(workflowName, workflowDescription);
      
      const workflowCount = await aiAutomationEngine.getWorkflowCount();
      expect(workflowCount).to.equal(1);
    });
  });

  describe("Integration Tests", function () {
    it("Should allow complete DeFi workflow", async function () {
      const { xrpToken, defiProtocol, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      // Mint tokens
      const amount = ethers.utils.parseEther("1000");
      await xrpToken.mint(user1.address, amount);
      
      // Deposit to DeFi
      await xrpToken.connect(user1).approve(defiProtocol.address, amount);
      await defiProtocol.connect(user1).deposit(amount);
      
      // Check balance
      expect(await defiProtocol.getUserBalance(user1.address)).to.equal(amount);
      
      // Withdraw
      await defiProtocol.connect(user1).withdraw(amount.div(2));
      expect(await defiProtocol.getUserBalance(user1.address)).to.equal(amount.div(2));
    });

    it("Should allow complete bridge workflow", async function () {
      const { xrpToken, xrplBridge, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      // Mint tokens
      const amount = ethers.utils.parseEther("1000");
      await xrpToken.mint(user1.address, amount);
      
      // Lock tokens for bridge
      await xrpToken.connect(user1).approve(xrplBridge.address, amount);
      await xrplBridge.connect(user1).lockTokens(amount);
      
      // Check bridge balance
      expect(await xrpToken.balanceOf(xrplBridge.address)).to.equal(amount);
    });
  });

  describe("Security Tests", function () {
    it("Should prevent unauthorized access to admin functions", async function () {
      const { xrpToken, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      await expect(
        xrpToken.connect(user1).mint(user1.address, ethers.utils.parseEther("1000"))
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("Should prevent zero amount transfers", async function () {
      const { xrpToken, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      await expect(
        xrpToken.transfer(user1.address, 0)
      ).to.be.revertedWith("Transfer amount must be greater than zero");
    });

    it("Should prevent insufficient balance transfers", async function () {
      const { xrpToken, user1 } = await loadFixture(deployXRPLEcosystemFixture);
      
      await expect(
        xrpToken.transfer(user1.address, ethers.utils.parseEther("1000"))
      ).to.be.revertedWith("ERC20: transfer amount exceeds balance");
    });
  });
});
