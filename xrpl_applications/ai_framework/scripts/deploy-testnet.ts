import { ethers } from "hardhat";

async function main() {
  console.log("Deploying AI Framework contracts to Testnet...");

  // Get the contract factories
  const XRPToken = await ethers.getContractFactory("XRPToken");
  const AIDatasetMarketplace = await ethers.getContractFactory("AIDatasetMarketplace");
  const AIAgentFactory = await ethers.getContractFactory("AIAgentFactory");
  const AIAutomationEngine = await ethers.getContractFactory("AIAutomationEngine");

  // Deploy XRP Token
  console.log("Deploying XRP Token...");
  const xrpToken = await XRPToken.deploy();
  await xrpToken.deployed();
  console.log("XRP Token deployed to:", xrpToken.address);

  // Deploy AI Dataset Marketplace
  console.log("Deploying AI Dataset Marketplace...");
  const datasetMarketplace = await AIDatasetMarketplace.deploy(xrpToken.address);
  await datasetMarketplace.deployed();
  console.log("AI Dataset Marketplace deployed to:", datasetMarketplace.address);

  // Deploy AI Agent Factory
  console.log("Deploying AI Agent Factory...");
  const agentFactory = await AIAgentFactory.deploy(xrpToken.address, datasetMarketplace.address);
  await agentFactory.deployed();
  console.log("AI Agent Factory deployed to:", agentFactory.address);

  // Deploy AI Automation Engine
  console.log("Deploying AI Automation Engine...");
  const automationEngine = await AIAutomationEngine.deploy(agentFactory.address, xrpToken.address);
  await automationEngine.deployed();
  console.log("AI Automation Engine deployed to:", automationEngine.address);

  // Setup initial configuration
  console.log("Setting up initial configuration...");
  
  // Add deployer as Ripple approver
  const [deployer] = await ethers.getSigners();
  await datasetMarketplace.addRippleApprover(deployer.address);
  console.log("Added deployer as Ripple approver");

  // Set testnet fees and limits (lower for testing)
  await agentFactory.setFees(
    ethers.utils.parseUnits("10", 6),  // 10 XRP creation fee
    ethers.utils.parseUnits("2", 6),   // 2 XRP dataset access fee
    ethers.utils.parseUnits("20", 6)   // 20 XRP deployment fee
  );
  console.log("Set agent factory fees");

  await automationEngine.setFees(
    ethers.utils.parseUnits("2", 6),   // 2 XRP base execution fee
    ethers.utils.parseUnits("1", 6),   // 1 XRP per agent fee
    ethers.utils.parseUnits("5", 6),   // 5 XRP template creation fee
    5 // 5% platform fee
  );
  console.log("Set automation engine fees");

  // Set testnet price limits for datasets
  await datasetMarketplace.setPriceLimits(
    ethers.utils.parseUnits("10", 6),   // 10 XRP minimum
    ethers.utils.parseUnits("10000", 6) // 10K XRP maximum
  );
  console.log("Set dataset price limits");

  // Set testnet quality thresholds (lower for testing)
  await datasetMarketplace.setQualityThresholds(60, 512); // 60% quality, 512B minimum
  console.log("Set quality thresholds");

  // Mint test tokens to deployer for testing
  await xrpToken.mint(deployer.address, ethers.utils.parseUnits("100000", 6));
  console.log("Minted 100,000 test XRP tokens to deployer");

  console.log("\n=== Testnet Deployment Summary ===");
  console.log("Network:", await ethers.provider.getNetwork());
  console.log("XRP Token:", xrpToken.address);
  console.log("AI Dataset Marketplace:", datasetMarketplace.address);
  console.log("AI Agent Factory:", agentFactory.address);
  console.log("AI Automation Engine:", automationEngine.address);
  console.log("Deployer:", deployer.address);
  
  console.log("\n=== Testnet Setup Complete ===");
  console.log("1. Contracts deployed with testnet-friendly settings");
  console.log("2. Lower fees and thresholds for easier testing");
  console.log("3. Test tokens minted to deployer");
  console.log("4. Ready for testing and development");
  
  // Save deployment info to file
  const deploymentInfo = {
    network: (await ethers.provider.getNetwork()).name,
    chainId: (await ethers.provider.getNetwork()).chainId,
    timestamp: new Date().toISOString(),
    contracts: {
      XRPToken: xrpToken.address,
      AIDatasetMarketplace: datasetMarketplace.address,
      AIAgentFactory: agentFactory.address,
      AIAutomationEngine: automationEngine.address
    },
    deployer: deployer.address,
    transactionHashes: {
      XRPToken: xrpToken.deployTransaction.hash,
      AIDatasetMarketplace: datasetMarketplace.deployTransaction.hash,
      AIAgentFactory: agentFactory.deployTransaction.hash,
      AIAutomationEngine: automationEngine.deployTransaction.hash
    },
    testnetSettings: {
      agentCreationFee: "10 XRP",
      datasetAccessFee: "2 XRP",
      deploymentFee: "20 XRP",
      baseExecutionFee: "2 XRP",
      agentUsageFee: "1 XRP",
      templateCreationFee: "5 XRP",
      platformFeePercent: "5%",
      minDatasetPrice: "10 XRP",
      maxDatasetPrice: "10,000 XRP",
      minQualityScore: "60%",
      minDatasetSize: "512 bytes"
    }
  };

  const fs = require('fs');
  fs.writeFileSync(
    `deployments/testnet-${Date.now()}.json`,
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log("\nDeployment info saved to deployments/ directory");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
