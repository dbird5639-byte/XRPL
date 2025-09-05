const { ethers, upgrades } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Starting XRPL Ecosystem Smart Contract Deployment");
  console.log("=" * 60);

  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  const network = await ethers.provider.getNetwork();
  console.log("Network:", network.name, "Chain ID:", network.chainId);

  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {}
  };

  try {
    // Deploy Core Contracts
    console.log("\n📦 Deploying Core Contracts...");
    
    // 1. XRP Token
    console.log("Deploying XRP Token...");
    const XRPToken = await ethers.getContractFactory("XRPToken");
    const xrpToken = await XRPToken.deploy();
    await xrpToken.deployed();
    console.log("✅ XRP Token deployed to:", xrpToken.address);
    deploymentInfo.contracts.XRPToken = xrpToken.address;

    // 2. XRPL Bridge
    console.log("Deploying XRPL Bridge...");
    const XRPLBridge = await ethers.getContractFactory("XRPLBridge");
    const xrplBridge = await XRPLBridge.deploy(xrpToken.address);
    await xrplBridge.deployed();
    console.log("✅ XRPL Bridge deployed to:", xrplBridge.address);
    deploymentInfo.contracts.XRPLBridge = xrplBridge.address;

    // 3. DeFi Protocol
    console.log("Deploying DeFi Protocol...");
    const DeFiProtocol = await ethers.getContractFactory("DeFiProtocol");
    const defiProtocol = await DeFiProtocol.deploy(xrpToken.address);
    await defiProtocol.deployed();
    console.log("✅ DeFi Protocol deployed to:", defiProtocol.address);
    deploymentInfo.contracts.DeFiProtocol = defiProtocol.address;

    // 4. NFT Marketplace
    console.log("Deploying NFT Marketplace...");
    const NFTMarketplace = await ethers.getContractFactory("NFTMarketplace");
    const nftMarketplace = await NFTMarketplace.deploy();
    await nftMarketplace.deployed();
    console.log("✅ NFT Marketplace deployed to:", nftMarketplace.address);
    deploymentInfo.contracts.NFTMarketplace = nftMarketplace.address;

    // Deploy Application Contracts
    console.log("\n🎯 Deploying Application Contracts...");

    // 5. AI Agent Factory
    console.log("Deploying AI Agent Factory...");
    const AIAgentFactory = await ethers.getContractFactory("AIAgentFactory");
    const aiAgentFactory = await AIAgentFactory.deploy();
    await aiAgentFactory.deployed();
    console.log("✅ AI Agent Factory deployed to:", aiAgentFactory.address);
    deploymentInfo.contracts.AIAgentFactory = aiAgentFactory.address;

    // 6. AI Automation Engine
    console.log("Deploying AI Automation Engine...");
    const AIAutomationEngine = await ethers.getContractFactory("AIAutomationEngine");
    const aiAutomationEngine = await AIAutomationEngine.deploy(aiAgentFactory.address);
    await aiAutomationEngine.deployed();
    console.log("✅ AI Automation Engine deployed to:", aiAutomationEngine.address);
    deploymentInfo.contracts.AIAutomationEngine = aiAutomationEngine.address;

    // 7. AI Dataset Marketplace
    console.log("Deploying AI Dataset Marketplace...");
    const AIDatasetMarketplace = await ethers.getContractFactory("AIDatasetMarketplace");
    const aiDatasetMarketplace = await AIDatasetMarketplace.deploy();
    await aiDatasetMarketplace.deployed();
    console.log("✅ AI Dataset Marketplace deployed to:", aiDatasetMarketplace.address);
    deploymentInfo.contracts.AIDatasetMarketplace = aiDatasetMarketplace.address;

    // 8. AI Citizen Rights Framework
    console.log("Deploying AI Citizen Rights Framework...");
    const AICitizenRightsFramework = await ethers.getContractFactory("AICitizenRightsFramework");
    const aiCitizenRights = await AICitizenRightsFramework.deploy();
    await aiCitizenRights.deployed();
    console.log("✅ AI Citizen Rights Framework deployed to:", aiCitizenRights.address);
    deploymentInfo.contracts.AICitizenRightsFramework = aiCitizenRights.address;

    // 9. Clean Energy Trading Platform
    console.log("Deploying Clean Energy Trading Platform...");
    const CleanEnergyTradingPlatform = await ethers.getContractFactory("CleanEnergyTradingPlatform");
    const cleanEnergyPlatform = await CleanEnergyTradingPlatform.deploy();
    await cleanEnergyPlatform.deployed();
    console.log("✅ Clean Energy Trading Platform deployed to:", cleanEnergyPlatform.address);
    deploymentInfo.contracts.CleanEnergyTradingPlatform = cleanEnergyPlatform.address;

    // 10. Global Cooperation DAO
    console.log("Deploying Global Cooperation DAO...");
    const GlobalCooperationDAO = await ethers.getContractFactory("GlobalCooperationDAO");
    const globalCooperationDAO = await GlobalCooperationDAO.deploy();
    await globalCooperationDAO.deployed();
    console.log("✅ Global Cooperation DAO deployed to:", globalCooperationDAO.address);
    deploymentInfo.contracts.GlobalCooperationDAO = globalCooperationDAO.address;

    // 11. Peace Protocol Infrastructure
    console.log("Deploying Peace Protocol Infrastructure...");
    const PeaceProtocolInfrastructure = await ethers.getContractFactory("PeaceProtocolInfrastructure");
    const peaceProtocol = await PeaceProtocolInfrastructure.deploy();
    await peaceProtocol.deployed();
    console.log("✅ Peace Protocol Infrastructure deployed to:", peaceProtocol.address);
    deploymentInfo.contracts.PeaceProtocolInfrastructure = peaceProtocol.address;

    // Save deployment information
    const deploymentDir = path.join(__dirname, "../deployment");
    if (!fs.existsSync(deploymentDir)) {
      fs.mkdirSync(deploymentDir, { recursive: true });
    }

    const deploymentFile = path.join(deploymentDir, `${network.name}-${network.chainId}.json`);
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
    console.log(`\n📝 Deployment info saved to: ${deploymentFile}`);

    // Create deployment summary
    const summaryFile = path.join(deploymentDir, "DEPLOYMENT_SUMMARY.md");
    const summaryContent = `# XRPL Ecosystem Smart Contract Deployment Summary

## Network Information
- **Network**: ${network.name}
- **Chain ID**: ${network.chainId}
- **Deployer**: ${deployer.address}
- **Timestamp**: ${new Date().toISOString()}

## Deployed Contracts

### Core Contracts
- **XRPToken**: ${xrpToken.address}
- **XRPLBridge**: ${xrplBridge.address}
- **DeFiProtocol**: ${defiProtocol.address}
- **NFTMarketplace**: ${nftMarketplace.address}

### Application Contracts
- **AIAgentFactory**: ${aiAgentFactory.address}
- **AIAutomationEngine**: ${aiAutomationEngine.address}
- **AIDatasetMarketplace**: ${aiDatasetMarketplace.address}
- **AICitizenRightsFramework**: ${aiCitizenRights.address}
- **CleanEnergyTradingPlatform**: ${cleanEnergyPlatform.address}
- **GlobalCooperationDAO**: ${globalCooperationDAO.address}
- **PeaceProtocolInfrastructure**: ${peaceProtocol.address}

## Next Steps
1. Verify contracts on block explorer
2. Update frontend applications with new contract addresses
3. Configure cross-chain bridge parameters
4. Test contract interactions
5. Deploy to production networks

## Verification Commands
\`\`\`bash
# Verify all contracts
npm run verify:${network.name === "localhost" ? "testnet" : network.name}
\`\`\`
`;

    fs.writeFileSync(summaryFile, summaryContent);
    console.log(`📋 Deployment summary saved to: ${summaryFile}`);

    console.log("\n" + "=" * 60);
    console.log("✅ All contracts deployed successfully!");
    console.log(`📊 Total contracts deployed: ${Object.keys(deploymentInfo.contracts).length}`);
    console.log("🔗 Contract addresses saved to deployment directory");

  } catch (error) {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
