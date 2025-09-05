const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Starting XRPL Agent Ecosystem deployment...");

  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy XRPL Agent Token
  console.log("\n📝 Deploying XRPL Agent Token...");
  const XRPLAgentToken = await ethers.getContractFactory("XRPLAgentToken");
  const xatToken = await XRPLAgentToken.deploy();
  await xatToken.deployed();
  console.log("XRPL Agent Token deployed to:", xatToken.address);

  // Deploy Agent Registry
  console.log("\n📝 Deploying Agent Registry...");
  const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
  const agentRegistry = await AgentRegistry.deploy(
    deployer.address, // feeCollector
    xatToken.address  // nativeToken
  );
  await agentRegistry.deployed();
  console.log("Agent Registry deployed to:", agentRegistry.address);

  // Deploy Agent Execution Engine
  console.log("\n📝 Deploying Agent Execution Engine...");
  const AgentExecutionEngine = await ethers.getContractFactory("AgentExecutionEngine");
  const executionEngine = await AgentExecutionEngine.deploy(
    agentRegistry.address, // agentRegistry
    deployer.address,      // feeCollector
    xatToken.address       // nativeToken
  );
  await executionEngine.deployed();
  console.log("Agent Execution Engine deployed to:", executionEngine.address);

  // Deploy XRPL Bridge
  console.log("\n📝 Deploying XRPL Bridge...");
  const XRPLBridge = await ethers.getContractFactory("XRPLBridge");
  const xrplBridge = await XRPLBridge.deploy(
    deployer.address, // feeCollector
    deployer.address, // xrplValidator
    xatToken.address  // nativeToken
  );
  await xrplBridge.deployed();
  console.log("XRPL Bridge deployed to:", xrplBridge.address);

  // Deploy Agent Governance
  console.log("\n📝 Deploying Agent Governance...");
  const AgentGovernance = await ethers.getContractFactory("AgentGovernance");
  const governance = await AgentGovernance.deploy(
    xatToken.address,     // governanceToken
    agentRegistry.address, // agentRegistry
    deployer.address,      // treasury
    deployer.address       // emergencyMultisig
  );
  await governance.deployed();
  console.log("Agent Governance deployed to:", governance.address);

  // Deploy Agent Marketplace
  console.log("\n📝 Deploying Agent Marketplace...");
  const AgentMarketplace = await ethers.getContractFactory("AgentMarketplace");
  const marketplace = await AgentMarketplace.deploy(
    agentRegistry.address, // agentRegistry
    xatToken.address,      // nativeToken
    deployer.address,      // agentNFT (placeholder)
    deployer.address,      // feeCollector
    deployer.address       // curatorRewardPool
  );
  await marketplace.deployed();
  console.log("Agent Marketplace deployed to:", marketplace.address);

  // Deploy Oracle Network
  console.log("\n📝 Deploying Oracle Network...");
  const OracleNetwork = await ethers.getContractFactory("OracleNetwork");
  const oracleNetwork = await OracleNetwork.deploy(
    deployer.address, // feeCollector
    xatToken.address  // nativeToken
  );
  await oracleNetwork.deployed();
  console.log("Oracle Network deployed to:", oracleNetwork.address);

  // Configure contracts
  console.log("\n⚙️ Configuring contracts...");

  // Authorize execution engine in agent registry
  await agentRegistry.authorizeExecutor(executionEngine.address);
  console.log("✅ Authorized execution engine in agent registry");

  // Authorize oracle network in execution engine
  await executionEngine.authorizeOracle(oracleNetwork.address);
  console.log("✅ Authorized oracle network in execution engine");

  // Authorize governance in agent registry
  await agentRegistry.authorizeExecutor(governance.address);
  console.log("✅ Authorized governance in agent registry");

  // Set up initial token distribution
  console.log("\n💰 Setting up initial token distribution...");
  
  // Transfer some tokens to governance treasury
  const treasuryAmount = ethers.utils.parseEther("10000000"); // 10M tokens
  await xatToken.transfer(governance.address, treasuryAmount);
  console.log("✅ Transferred 10M tokens to governance treasury");

  // Transfer some tokens to bridge for liquidity
  const bridgeAmount = ethers.utils.parseEther("5000000"); // 5M tokens
  await xatToken.transfer(xrplBridge.address, bridgeAmount);
  console.log("✅ Transferred 5M tokens to bridge for liquidity");

  // Transfer some tokens to oracle network for rewards
  const oracleAmount = ethers.utils.parseEther("2000000"); // 2M tokens
  await xatToken.transfer(oracleNetwork.address, oracleAmount);
  console.log("✅ Transferred 2M tokens to oracle network for rewards");

  // Create default execution environment
  console.log("\n🌍 Creating default execution environment...");
  await executionEngine.createExecutionEnvironment(
    ethers.utils.parseUnits("10000000", 0), // maxGas: 10M
    ethers.utils.parseUnits("100000000", 0), // maxMemory: 100MB
    ethers.utils.parseUnits("10000000", 0), // maxStorage: 10MB
    300, // timeout: 5 minutes
    true, // allowExternalCalls
    true, // allowStateChanges
    [], // allowedContracts
    [] // allowedTokens
  );
  console.log("✅ Created default execution environment");

  // Deploy summary
  console.log("\n🎉 Deployment completed successfully!");
  console.log("\n📋 Contract Addresses:");
  console.log("XRPL Agent Token:", xatToken.address);
  console.log("Agent Registry:", agentRegistry.address);
  console.log("Agent Execution Engine:", executionEngine.address);
  console.log("XRPL Bridge:", xrplBridge.address);
  console.log("Agent Governance:", governance.address);
  console.log("Agent Marketplace:", marketplace.address);
  console.log("Oracle Network:", oracleNetwork.address);

  console.log("\n🔗 Network Information:");
  const network = await ethers.provider.getNetwork();
  console.log("Network:", network.name);
  console.log("Chain ID:", network.chainId);

  console.log("\n📊 Token Information:");
  const totalSupply = await xatToken.totalSupply();
  console.log("Total Supply:", ethers.utils.formatEther(totalSupply), "XAT");
  
  const deployerBalance = await xatToken.balanceOf(deployer.address);
  console.log("Deployer Balance:", ethers.utils.formatEther(deployerBalance), "XAT");

  console.log("\n✨ XRPL Agent Ecosystem is ready for use!");
  console.log("\nNext steps:");
  console.log("1. Verify contracts on block explorer");
  console.log("2. Set up frontend application");
  console.log("3. Deploy sample agents");
  console.log("4. Configure oracles");
  console.log("5. Launch governance proposals");

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId,
    deployer: deployer.address,
    contracts: {
      XRPLAgentToken: xatToken.address,
      AgentRegistry: agentRegistry.address,
      AgentExecutionEngine: executionEngine.address,
      XRPLBridge: xrplBridge.address,
      AgentGovernance: governance.address,
      AgentMarketplace: marketplace.address,
      OracleNetwork: oracleNetwork.address
    },
    timestamp: new Date().toISOString()
  };

  const fs = require('fs');
  fs.writeFileSync(
    `deployments/${network.name}-${network.chainId}.json`,
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log(`\n💾 Deployment info saved to deployments/${network.name}-${network.chainId}.json`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
