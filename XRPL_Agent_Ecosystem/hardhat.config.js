require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    hardhat: {
      chainId: 1337
    },
    testnet: {
      url: "https://testnet.xrpl-evm-sidechain.com",
      chainId: 1440002,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      gasPrice: 20000000000, // 20 gwei
      gas: 8000000
    },
    mainnet: {
      url: "https://mainnet.xrpl-evm-sidechain.com",
      chainId: 1440001,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      gasPrice: 20000000000, // 20 gwei
      gas: 8000000
    }
  },
  etherscan: {
    apiKey: {
      testnet: process.env.ETHERSCAN_API_KEY,
      mainnet: process.env.ETHERSCAN_API_KEY
    },
    customChains: [
      {
        network: "testnet",
        chainId: 1440002,
        urls: {
          apiURL: "https://api-testnet.xrpl-evm-sidechain.com/api",
          browserURL: "https://testnet.xrpl-evm-sidechain.com"
        }
      },
      {
        network: "mainnet",
        chainId: 1440001,
        urls: {
          apiURL: "https://api-mainnet.xrpl-evm-sidechain.com/api",
          browserURL: "https://mainnet.xrpl-evm-sidechain.com"
        }
      }
    ]
  },
  paths: {
    sources: "./contracts",
    tests: "./tests",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};
