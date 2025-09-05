import { expect } from "chai";
import { ethers } from "hardhat";
import { AIDatasetMarketplace, XRPToken } from "../typechain-types";

describe("AIDatasetMarketplace", function () {
  let datasetMarketplace: AIDatasetMarketplace;
  let xrpToken: XRPToken;
  let owner: any;
  let approver: any;
  let submitter: any;
  let buyer: any;

  beforeEach(async function () {
    [owner, approver, submitter, buyer] = await ethers.getSigners();

    // Deploy XRP Token
    const XRPToken = await ethers.getContractFactory("XRPToken");
    xrpToken = await XRPToken.deploy();
    await xrpToken.deployed();

    // Deploy Dataset Marketplace
    const AIDatasetMarketplace = await ethers.getContractFactory("AIDatasetMarketplace");
    datasetMarketplace = await AIDatasetMarketplace.deploy(xrpToken.address);
    await datasetMarketplace.deployed();

    // Add approver
    await datasetMarketplace.addRippleApprover(approver.address);

    // Mint tokens to users
    await xrpToken.mint(submitter.address, ethers.utils.parseUnits("10000", 6));
    await xrpToken.mint(buyer.address, ethers.utils.parseUnits("10000", 6));

    // Approve marketplace to spend tokens
    await xrpToken.connect(submitter).approve(datasetMarketplace.address, ethers.utils.parseUnits("10000", 6));
    await xrpToken.connect(buyer).approve(datasetMarketplace.address, ethers.utils.parseUnits("10000", 6));
  });

  describe("Dataset Submission", function () {
    it("Should allow users to submit datasets", async function () {
      const tx = await datasetMarketplace.connect(submitter).submitDataset(
        "Test Dataset",
        "A test dataset for AI training",
        "finance",
        "QmTestHash123",
        ethers.utils.parseUnits("500", 6),
        ethers.utils.parseUnits("1024", 0)
      );

      await expect(tx)
        .to.emit(datasetMarketplace, "DatasetSubmitted")
        .withArgs(1, submitter.address, "Test Dataset", "finance");

      const dataset = await datasetMarketplace.getDataset(1);
      expect(dataset.name).to.equal("Test Dataset");
      expect(dataset.submitter).to.equal(submitter.address);
      expect(dataset.status).to.equal(0); // Pending
    });

    it("Should reject empty dataset names", async function () {
      await expect(
        datasetMarketplace.connect(submitter).submitDataset(
          "",
          "A test dataset",
          "finance",
          "QmTestHash123",
          ethers.utils.parseUnits("500", 6),
          ethers.utils.parseUnits("1024", 0)
        )
      ).to.be.revertedWith("Name cannot be empty");
    });

    it("Should reject datasets below minimum price", async function () {
      await expect(
        datasetMarketplace.connect(submitter).submitDataset(
          "Test Dataset",
          "A test dataset",
          "finance",
          "QmTestHash123",
          ethers.utils.parseUnits("50", 6), // Below minimum
          ethers.utils.parseUnits("1024", 0)
        )
      ).to.be.revertedWith("Invalid price range");
    });

    it("Should reject datasets above maximum price", async function () {
      await expect(
        datasetMarketplace.connect(submitter).submitDataset(
          "Test Dataset",
          "A test dataset",
          "finance",
          "QmTestHash123",
          ethers.utils.parseUnits("2000000", 6), // Above maximum
          ethers.utils.parseUnits("1024", 0)
        )
      ).to.be.revertedWith("Invalid price range");
    });
  });

  describe("Dataset Approval", function () {
    beforeEach(async function () {
      await datasetMarketplace.connect(submitter).submitDataset(
        "Test Dataset",
        "A test dataset",
        "finance",
        "QmTestHash123",
        ethers.utils.parseUnits("500", 6),
        ethers.utils.parseUnits("1024", 0)
      );
    });

    it("Should allow Ripple approvers to approve datasets", async function () {
      const tx = await datasetMarketplace.connect(approver).approveDataset(1, 85);

      await expect(tx)
        .to.emit(datasetMarketplace, "DatasetApproved")
        .withArgs(1, approver.address);

      const dataset = await datasetMarketplace.getDataset(1);
      expect(dataset.status).to.equal(1); // Approved
      expect(dataset.qualityScore).to.equal(85);
      expect(dataset.isActive).to.be.true;
    });

    it("Should reject datasets with low quality scores", async function () {
      await expect(
        datasetMarketplace.connect(approver).approveDataset(1, 60) // Below minimum
      ).to.be.revertedWith("Quality score too low");
    });

    it("Should allow Ripple approvers to reject datasets", async function () {
      const tx = await datasetMarketplace.connect(approver).rejectDataset(1, "Poor quality data");

      await expect(tx)
        .to.emit(datasetMarketplace, "DatasetRejected")
        .withArgs(1, approver.address, "Poor quality data");

      const dataset = await datasetMarketplace.getDataset(1);
      expect(dataset.status).to.equal(2); // Rejected
      expect(dataset.rejectionReason).to.equal("Poor quality data");
    });

    it("Should not allow non-approvers to approve datasets", async function () {
      await expect(
        datasetMarketplace.connect(submitter).approveDataset(1, 85)
      ).to.be.revertedWith("Not a Ripple approver");
    });
  });

  describe("Dataset Purchase", function () {
    beforeEach(async function () {
      await datasetMarketplace.connect(submitter).submitDataset(
        "Test Dataset",
        "A test dataset",
        "finance",
        "QmTestHash123",
        ethers.utils.parseUnits("500", 6),
        ethers.utils.parseUnits("1024", 0)
      );
      await datasetMarketplace.connect(approver).approveDataset(1, 85);
    });

    it("Should allow users to purchase approved datasets", async function () {
      const buyerBalanceBefore = await xrpToken.balanceOf(buyer.address);
      const submitterBalanceBefore = await xrpToken.balanceOf(submitter.address);

      const tx = await datasetMarketplace.connect(buyer).purchaseDataset(1);

      await expect(tx)
        .to.emit(datasetMarketplace, "DatasetPurchased")
        .withArgs(1, buyer.address, ethers.utils.parseUnits("500", 6));

      const dataset = await datasetMarketplace.getDataset(1);
      expect(dataset.purchaseCount).to.equal(1);
      expect(dataset.totalRevenue).to.equal(ethers.utils.parseUnits("475", 6)); // 95% to submitter

      const buyerBalanceAfter = await xrpToken.balanceOf(buyer.address);
      const submitterBalanceAfter = await xrpToken.balanceOf(submitter.address);

      expect(buyerBalanceBefore.sub(buyerBalanceAfter)).to.equal(ethers.utils.parseUnits("500", 6));
      expect(submitterBalanceAfter.sub(submitterBalanceBefore)).to.equal(ethers.utils.parseUnits("475", 6));
    });

    it("Should not allow purchasing own datasets", async function () {
      await expect(
        datasetMarketplace.connect(submitter).purchaseDataset(1)
      ).to.be.revertedWith("Cannot purchase own dataset");
    });

    it("Should not allow purchasing unapproved datasets", async function () {
      await datasetMarketplace.connect(submitter).submitDataset(
        "Unapproved Dataset",
        "A test dataset",
        "finance",
        "QmTestHash456",
        ethers.utils.parseUnits("300", 6),
        ethers.utils.parseUnits("1024", 0)
      );

      await expect(
        datasetMarketplace.connect(buyer).purchaseDataset(2)
      ).to.be.revertedWith("Dataset not approved");
    });
  });

  describe("Admin Functions", function () {
    it("Should allow owner to add Ripple approvers", async function () {
      await datasetMarketplace.addRippleApprover(buyer.address);
      expect(await datasetMarketplace.rippleApprovers(buyer.address)).to.be.true;
    });

    it("Should allow owner to remove Ripple approvers", async function () {
      await datasetMarketplace.removeRippleApprover(approver.address);
      expect(await datasetMarketplace.rippleApprovers(approver.address)).to.be.false;
    });

    it("Should allow owner to set platform fee", async function () {
      await datasetMarketplace.setPlatformFee(10); // 10%
      expect(await datasetMarketplace.platformFeePercent()).to.equal(10);
    });

    it("Should not allow platform fee above 20%", async function () {
      await expect(
        datasetMarketplace.setPlatformFee(25)
      ).to.be.revertedWith("Fee too high");
    });

    it("Should allow owner to set price limits", async function () {
      await datasetMarketplace.setPriceLimits(
        ethers.utils.parseUnits("200", 6),
        ethers.utils.parseUnits("2000000", 6)
      );
      expect(await datasetMarketplace.minimumDatasetPrice()).to.equal(ethers.utils.parseUnits("200", 6));
      expect(await datasetMarketplace.maximumDatasetPrice()).to.equal(ethers.utils.parseUnits("2000000", 6));
    });

    it("Should allow owner to pause and unpause", async function () {
      await datasetMarketplace.pause();
      expect(await datasetMarketplace.paused()).to.be.true;

      await datasetMarketplace.unpause();
      expect(await datasetMarketplace.paused()).to.be.false;
    });
  });

  describe("Dataset Queries", function () {
    beforeEach(async function () {
      // Submit multiple datasets
      await datasetMarketplace.connect(submitter).submitDataset(
        "Finance Dataset",
        "Financial data",
        "finance",
        "QmFinance123",
        ethers.utils.parseUnits("500", 6),
        ethers.utils.parseUnits("1024", 0)
      );

      await datasetMarketplace.connect(submitter).submitDataset(
        "Healthcare Dataset",
        "Healthcare data",
        "healthcare",
        "QmHealth123",
        ethers.utils.parseUnits("750", 6),
        ethers.utils.parseUnits("2048", 0)
      );
    });

    it("Should return datasets by category", async function () {
      const financeDatasets = await datasetMarketplace.getDatasetsByCategory("finance");
      const healthcareDatasets = await datasetMarketplace.getDatasetsByCategory("healthcare");

      expect(financeDatasets.length).to.equal(1);
      expect(healthcareDatasets.length).to.equal(1);
      expect(financeDatasets[0]).to.equal(1);
      expect(healthcareDatasets[0]).to.equal(2);
    });

    it("Should return user datasets", async function () {
      const userDatasets = await datasetMarketplace.getUserDatasets(submitter.address);
      expect(userDatasets.length).to.equal(2);
      expect(userDatasets[0]).to.equal(1);
      expect(userDatasets[1]).to.equal(2);
    });

    it("Should return total dataset count", async function () {
      const totalDatasets = await datasetMarketplace.getTotalDatasets();
      expect(totalDatasets).to.equal(2);
    });
  });
});
