const { ethers } = require("hardhat");

async function main() {
    console.log("Deploying XRPL Lending Platform...");

    // Get the contract factory
    const XRPLLending = await ethers.getContractFactory("XRPLLending");
    
    // Deploy the contract
    const feeCollector = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"; // Replace with your fee collector address
    const lendingPlatform = await XRPLLending.deploy(feeCollector);
    
    await lendingPlatform.deployed();
    
    console.log("XRPL Lending Platform deployed to:", lendingPlatform.address);
    
    // Authorize XRP token (replace with actual XRP token address)
    const xrpTokenAddress = "0x1234567890123456789012345678901234567890"; // Replace with actual XRP token address
    await lendingPlatform.authorizeToken(xrpTokenAddress);
    console.log("XRP token authorized");
    
    // Set up collateral pool for XRP
    await lendingPlatform.setCollateralPool(
        xrpTokenAddress,
        500, // 5% base interest rate
        1000 // 10% liquidation penalty
    );
    console.log("XRP collateral pool configured");
    
    console.log("Deployment completed successfully!");
    console.log("Contract address:", lendingPlatform.address);
    console.log("Fee collector:", feeCollector);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
