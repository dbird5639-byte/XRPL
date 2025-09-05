import { ethers } from "hardhat";

async function main() {
  console.log("🚀 Starting XRPL EVM Sidechain deployment...");

  // Get the contract factories
  const XRPToken = await ethers.getContractFactory("XRPToken");
  const XRPLBridge = await ethers.getContractFactory("XRPLBridge");
  const DeFiProtocol = await ethers.getContractFactory("DeFiProtocol");

  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying contracts with account:", deployer.address);

  // Deploy XRP Token
  console.log("🪙 Deploying XRP Token...");
  const xrpToken = await XRPToken.deploy(
    "XRP Token",
    "XRP",
    18, // decimals
    ethers.parseEther("1000000") // initial supply
  );
  await xrpToken.waitForDeployment();
  const xrpTokenAddress = await xrpToken.getAddress();
  console.log("✅ XRP Token deployed to:", xrpTokenAddress);

  // Deploy XRPL Bridge
  console.log("🌉 Deploying XRPL Bridge...");
  const bridge = await XRPLBridge.deploy(
    xrpTokenAddress,
    1 // validator threshold
  );
  await bridge.waitForDeployment();
  const bridgeAddress = await bridge.getAddress();
  console.log("✅ XRPL Bridge deployed to:", bridgeAddress);

  // Update XRP Token bridge address
  console.log("🔗 Setting bridge address in XRP Token...");
  await xrpToken.updateBridge(bridgeAddress);
  console.log("✅ Bridge address updated");

  // Deploy DeFi Protocol
  console.log("💎 Deploying DeFi Protocol...");
  const defiProtocol = await DeFiProtocol.deploy(
    xrpTokenAddress,
    ethers.parseEther("1") // reward rate
  );
  await defiProtocol.waitForDeployment();
  const defiProtocolAddress = await defiProtocol.getAddress();
  console.log("✅ DeFi Protocol deployed to:", defiProtocolAddress);

  // Add deployer as validator
  console.log("👤 Adding deployer as validator...");
  await bridge.addValidator(deployer.address);
  console.log("✅ Deployer added as validator");

  // Create initial liquidity pools
  console.log("🏊 Creating initial liquidity pools...");
  
  // XRP/USDC pool (using XRP token as both for demo)
  await defiProtocol.createPool(
    xrpTokenAddress,
    xrpTokenAddress, // In real implementation, this would be a USDC token
    ethers.parseEther("10000"), // 10,000 XRP
    ethers.parseEther("10000"), // 10,000 USDC equivalent
    30 // 0.3% fee
  );
  console.log("✅ XRP/USDC pool created");

  // XRP/BTC pool
  await defiProtocol.createPool(
    xrpTokenAddress,
    xrpTokenAddress, // In real implementation, this would be a BTC token
    ethers.parseEther("5000"), // 5,000 XRP
    ethers.parseEther("5000"), // 5,000 BTC equivalent
    50 // 0.5% fee
  );
  console.log("✅ XRP/BTC pool created");

  // Print deployment summary
  console.log("\n🎉 Deployment completed successfully!");
  console.log("📋 Contract Addresses:");
  console.log(`   XRP Token: ${xrpTokenAddress}`);
  console.log(`   XRPL Bridge: ${bridgeAddress}`);
  console.log(`   DeFi Protocol: ${defiProtocolAddress}`);
  
  console.log("\n🔧 Configuration:");
  console.log(`   Validator: ${deployer.address}`);
  console.log(`   Initial XRP Supply: 1,000,000 XRP`);
  console.log(`   Validator Threshold: 1`);
  console.log(`   Reward Rate: 1 XRP/second`);

  console.log("\n📝 Next Steps:");
  console.log("1. Update environment variables with contract addresses");
  console.log("2. Start the validator service");
  console.log("3. Test bridge functionality");
  console.log("4. Deploy to production network");

  // Save deployment info to file
  const deploymentInfo = {
    network: await ethers.provider.getNetwork(),
    deployer: deployer.address,
    contracts: {
      xrpToken: xrpTokenAddress,
      bridge: bridgeAddress,
      defiProtocol: defiProtocolAddress
    },
    timestamp: new Date().toISOString()
  };

  const fs = require('fs');
  fs.writeFileSync(
    'deployment.json',
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("💾 Deployment info saved to deployment.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
