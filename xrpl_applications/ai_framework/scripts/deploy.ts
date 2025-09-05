import { ethers } from "hardhat";

async function main() {
  console.log("Deploying AI Framework contracts...");

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

  // Set initial fees and limits
  await agentFactory.setFees(
    ethers.utils.parseUnits("50", 6), // 50 XRP creation fee
    ethers.utils.parseUnits("10", 6), // 10 XRP dataset access fee
    ethers.utils.parseUnits("100", 6) // 100 XRP deployment fee
  );
  console.log("Set agent factory fees");

  await automationEngine.setFees(
    ethers.utils.parseUnits("10", 6), // 10 XRP base execution fee
    ethers.utils.parseUnits("5", 6),  // 5 XRP per agent fee
    ethers.utils.parseUnits("25", 6), // 25 XRP template creation fee
    10 // 10% platform fee
  );
  console.log("Set automation engine fees");

  // Set price limits for datasets
  await datasetMarketplace.setPriceLimits(
    ethers.utils.parseUnits("100", 6),  // 100 XRP minimum
    ethers.utils.parseUnits("1000000", 6) // 1M XRP maximum
  );
  console.log("Set dataset price limits");

  console.log("\n=== Deployment Summary ===");
  console.log("XRP Token:", xrpToken.address);
  console.log("AI Dataset Marketplace:", datasetMarketplace.address);
  console.log("AI Agent Factory:", agentFactory.address);
  console.log("AI Automation Engine:", automationEngine.address);
  console.log("Deployer:", deployer.address);
  
  console.log("\n=== Next Steps ===");
  console.log("1. Verify contracts on block explorer");
  console.log("2. Set up frontend to interact with contracts");
  console.log("3. Create initial datasets for testing");
  console.log("4. Deploy AI agents for automation");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
