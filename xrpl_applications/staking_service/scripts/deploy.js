const { ethers } = require("hardhat");

async function main() {
    console.log("Deploying XRPL Staking Service...");

    // Get the contract factory
    const XRPLStaking = await ethers.getContractFactory("XRPLStaking");
    
    // Deploy the contract
    const feeCollector = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"; // Replace with your fee collector address
    const stakingService = await XRPLStaking.deploy(feeCollector);
    
    await stakingService.deployed();
    
    console.log("XRPL Staking Service deployed to:", stakingService.address);
    
    // Authorize some validators (replace with actual validator addresses)
    const validators = [
        "0x1234567890123456789012345678901234567890",
        "0x2345678901234567890123456789012345678901",
        "0x3456789012345678901234567890123456789012"
    ];
    
    for (const validator of validators) {
        await stakingService.authorizeValidator(validator);
        console.log(`Validator ${validator} authorized`);
    }
    
    // Create staking pools for each validator
    const poolConfigs = [
        {
            validator: validators[0],
            name: "XRPL Validator Alpha",
            rewardRate: 800, // 8% APR
            minStake: ethers.utils.parseEther("100"),
            maxStake: ethers.utils.parseEther("10000"),
            lockPeriod: 30 * 24 * 60 * 60 // 30 days
        },
        {
            validator: validators[1],
            name: "XRPL Validator Beta",
            rewardRate: 1000, // 10% APR
            minStake: ethers.utils.parseEther("500"),
            maxStake: ethers.utils.parseEther("50000"),
            lockPeriod: 60 * 24 * 60 * 60 // 60 days
        },
        {
            validator: validators[2],
            name: "XRPL Validator Gamma",
            rewardRate: 1200, // 12% APR
            minStake: ethers.utils.parseEther("1000"),
            maxStake: ethers.utils.parseEther("100000"),
            lockPeriod: 90 * 24 * 60 * 60 // 90 days
        }
    ];
    
    for (const config of poolConfigs) {
        const tx = await stakingService.createStakingPool(
            config.validator,
            config.name,
            config.rewardRate,
            config.minStake,
            config.maxStake,
            config.lockPeriod
        );
        await tx.wait();
        console.log(`Staking pool created for ${config.name}`);
    }
    
    console.log("Deployment completed successfully!");
    console.log("Contract address:", stakingService.address);
    console.log("Fee collector:", feeCollector);
    console.log("Total pools created:", poolConfigs.length);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
