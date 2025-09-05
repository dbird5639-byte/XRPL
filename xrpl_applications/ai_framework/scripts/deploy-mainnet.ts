import { ethers } from "hardhat";

async function main() {
  console.log("Deploying AI Framework contracts to Mainnet...");

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

  // Set production fees and limits
  await agentFactory.setFees(
    ethers.utils.parseUnits("100", 6), // 100 XRP creation fee
    ethers.utils.parseUnits("20", 6),  // 20 XRP dataset access fee
    ethers.utils.parseUnits("200", 6)  // 200 XRP deployment fee
  );
  console.log("Set agent factory fees");

  await automationEngine.setFees(
    ethers.utils.parseUnits("20", 6),  // 20 XRP base execution fee
    ethers.utils.parseUnits("10", 6),  // 10 XRP per agent fee
    ethers.utils.parseUnits("50", 6),  // 50 XRP template creation fee
    15 // 15% platform fee
  );
  console.log("Set automation engine fees");

  // Set production price limits for datasets
  await datasetMarketplace.setPriceLimits(
    ethers.utils.parseUnits("200", 6),   // 200 XRP minimum
    ethers.utils.parseUnits("2000000", 6) // 2M XRP maximum
  );
  console.log("Set dataset price limits");

  // Set production quality thresholds
  await datasetMarketplace.setQualityThresholds(80, 2048); // 80% quality, 2KB minimum
  console.log("Set quality thresholds");

  console.log("\n=== Mainnet Deployment Summary ===");
  console.log("Network:", await ethers.provider.getNetwork());
  console.log("XRP Token:", xrpToken.address);
  console.log("AI Dataset Marketplace:", datasetMarketplace.address);
  console.log("AI Agent Factory:", agentFactory.address);
  console.log("AI Automation Engine:", automationEngine.address);
  console.log("Deployer:", deployer.address);
  
  console.log("\n=== Next Steps ===");
  console.log("1. Verify contracts on block explorer");
  console.log("2. Update frontend configuration with contract addresses");
  console.log("3. Set up monitoring and alerting");
  console.log("4. Create initial datasets for the marketplace");
  console.log("5. Deploy initial AI agents");
  console.log("6. Set up IPFS infrastructure");
  console.log("7. Configure Ripple approver accounts");
  
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
    }
  };

  const fs = require('fs');
  fs.writeFileSync(
    `deployments/mainnet-${Date.now()}.json`,
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
