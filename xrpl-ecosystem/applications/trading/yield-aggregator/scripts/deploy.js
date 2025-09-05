const { ethers } = require("hardhat");

async function main() {
    console.log("Deploying XRPL Yield Aggregator...");

    // Get the contract factory
    const XRPLYieldAggregator = await ethers.getContractFactory("XRPLYieldAggregator");
    
    // Deploy the contract
    const feeCollector = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"; // Replace with your fee collector address
    const yieldAggregator = await XRPLYieldAggregator.deploy(feeCollector);
    
    await yieldAggregator.deployed();
    
    console.log("XRPL Yield Aggregator deployed to:", yieldAggregator.address);
    
    // Authorize common tokens (replace with actual token addresses)
    const tokens = [
        "0x1234567890123456789012345678901234567890", // XRP token
        "0x2345678901234567890123456789012345678901", // USDC token
        "0x3456789012345678901234567890123456789012", // USDT token
        "0x4567890123456789012345678901234567890123"  // WETH token
    ];
    
    for (const token of tokens) {
        await yieldAggregator.authorizeToken(token);
        console.log(`Token ${token} authorized`);
    }
    
    // Add example strategies (replace with actual strategy addresses)
    const strategies = [
        {
            address: "0x5678901234567890123456789012345678901234",
            name: "XRPL Staking Strategy",
            supportedTokens: [tokens[0]], // XRP
            minDeposit: ethers.utils.parseEther("100"),
            maxDeposit: ethers.utils.parseEther("10000")
        },
        {
            address: "0x6789012345678901234567890123456789012345",
            name: "Liquidity Pool Strategy",
            supportedTokens: [tokens[1], tokens[2]], // USDC, USDT
            minDeposit: ethers.utils.parseUnits("1000", 6),
            maxDeposit: ethers.utils.parseUnits("100000", 6)
        },
        {
            address: "0x7890123456789012345678901234567890123456",
            name: "Lending Protocol Strategy",
            supportedTokens: [tokens[0], tokens[1], tokens[2]], // XRP, USDC, USDT
            minDeposit: ethers.utils.parseEther("50"),
            maxDeposit: ethers.utils.parseEther("50000")
        }
    ];
    
    for (const strategy of strategies) {
        await yieldAggregator.addStrategy(
            strategy.address,
            strategy.name,
            strategy.supportedTokens,
            strategy.minDeposit,
            strategy.maxDeposit
        );
        console.log(`Strategy ${strategy.name} added`);
    }
    
    // Create example vaults
    const vaults = [
        {
            name: "XRP Staking Vault",
            token: tokens[0], // XRP
            strategy: strategies[0].address,
            feeRate: 100 // 1%
        },
        {
            name: "USDC Liquidity Vault",
            token: tokens[1], // USDC
            strategy: strategies[1].address,
            feeRate: 150 // 1.5%
        },
        {
            name: "Multi-Token Lending Vault",
            token: tokens[0], // XRP
            strategy: strategies[2].address,
            feeRate: 200 // 2%
        }
    ];
    
    for (const vault of vaults) {
        const tx = await yieldAggregator.createVault(
            vault.name,
            vault.token,
            vault.strategy,
            vault.feeRate
        );
        await tx.wait();
        console.log(`Vault ${vault.name} created with ${vault.feeRate/100}% fee rate`);
    }
    
    console.log("Deployment completed successfully!");
    console.log("Contract address:", yieldAggregator.address);
    console.log("Fee collector:", feeCollector);
    console.log("Authorized tokens:", tokens.length);
    console.log("Added strategies:", strategies.length);
    console.log("Created vaults:", vaults.length);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
