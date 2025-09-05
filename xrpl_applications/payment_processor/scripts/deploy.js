const { ethers } = require("hardhat");

async function main() {
    console.log("Deploying XRPL Payment Processor...");

    // Get the contract factory
    const XRPLPaymentProcessor = await ethers.getContractFactory("XRPLPaymentProcessor");
    
    // Deploy the contract
    const feeCollector = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"; // Replace with your fee collector address
    const paymentProcessor = await XRPLPaymentProcessor.deploy(feeCollector);
    
    await paymentProcessor.deployed();
    
    console.log("XRPL Payment Processor deployed to:", paymentProcessor.address);
    
    // Authorize common tokens (replace with actual token addresses)
    const tokens = [
        "0x1234567890123456789012345678901234567890", // XRP token
        "0x2345678901234567890123456789012345678901", // USDC token
        "0x3456789012345678901234567890123456789012"  // USDT token
    ];
    
    for (const token of tokens) {
        await paymentProcessor.authorizeToken(token);
        console.log(`Token ${token} authorized`);
    }
    
    // Register some example merchants
    const merchants = [
        {
            address: "0x4567890123456789012345678901234567890123",
            name: "XRPL Store",
            description: "Official XRPL merchandise store",
            feeRate: 100 // 1%
        },
        {
            address: "0x5678901234567890123456789012345678901234",
            name: "Crypto Coffee Shop",
            description: "Coffee shop accepting XRP payments",
            feeRate: 150 // 1.5%
        },
        {
            address: "0x6789012345678901234567890123456789012345",
            name: "Digital Services Co",
            description: "Digital marketing and web services",
            feeRate: 200 // 2%
        }
    ];
    
    for (const merchant of merchants) {
        // Note: In production, merchants would register themselves
        // This is just for demonstration
        console.log(`Example merchant: ${merchant.name} (${merchant.feeRate/100}% fee rate)`);
    }
    
    console.log("Deployment completed successfully!");
    console.log("Contract address:", paymentProcessor.address);
    console.log("Fee collector:", feeCollector);
    console.log("Authorized tokens:", tokens.length);
    console.log("Example merchants:", merchants.length);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
