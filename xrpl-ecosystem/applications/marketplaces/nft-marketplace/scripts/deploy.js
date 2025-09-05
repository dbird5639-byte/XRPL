const { ethers } = require("hardhat");

async function main() {
    console.log("Deploying XRPL NFT Marketplace...");

    // Get the contract factory
    const XRPLNFTMarketplace = await ethers.getContractFactory("XRPLNFTMarketplace");
    
    // Deploy the contract
    const feeCollector = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"; // Replace with your fee collector address
    const nftMarketplace = await XRPLNFTMarketplace.deploy(feeCollector);
    
    await nftMarketplace.deployed();
    
    console.log("XRPL NFT Marketplace deployed to:", nftMarketplace.address);
    
    // Authorize common payment tokens (replace with actual token addresses)
    const paymentTokens = [
        "0x1234567890123456789012345678901234567890", // XRP token
        "0x2345678901234567890123456789012345678901", // USDC token
        "0x3456789012345678901234567890123456789012"  // USDT token
    ];
    
    for (const token of paymentTokens) {
        await nftMarketplace.authorizeToken(token);
        console.log(`Payment token ${token} authorized`);
    }
    
    // Authorize some example NFT contracts (replace with actual NFT contract addresses)
    const nftContracts = [
        "0x4567890123456789012345678901234567890123", // Example NFT Contract 1
        "0x5678901234567890123456789012345678901234", // Example NFT Contract 2
        "0x6789012345678901234567890123456789012345"  // Example NFT Contract 3
    ];
    
    for (const nftContract of nftContracts) {
        await nftMarketplace.authorizeNFT(nftContract);
        console.log(`NFT contract ${nftContract} authorized`);
    }
    
    // Register some example collections
    const collections = [
        {
            nftContract: nftContracts[0],
            name: "XRPL Art Collection",
            symbol: "XRPLART",
            royaltyFee: 500 // 5% royalty
        },
        {
            nftContract: nftContracts[1],
            name: "Digital Collectibles",
            symbol: "DIGICOLL",
            royaltyFee: 250 // 2.5% royalty
        },
        {
            nftContract: nftContracts[2],
            name: "Gaming NFTs",
            symbol: "GAMENFT",
            royaltyFee: 750 // 7.5% royalty
        }
    ];
    
    for (const collection of collections) {
        await nftMarketplace.registerCollection(
            collection.nftContract,
            collection.name,
            collection.symbol,
            collection.royaltyFee
        );
        console.log(`Collection ${collection.name} registered with ${collection.royaltyFee/100}% royalty`);
    }
    
    console.log("Deployment completed successfully!");
    console.log("Contract address:", nftMarketplace.address);
    console.log("Fee collector:", feeCollector);
    console.log("Authorized payment tokens:", paymentTokens.length);
    console.log("Authorized NFT contracts:", nftContracts.length);
    console.log("Registered collections:", collections.length);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
