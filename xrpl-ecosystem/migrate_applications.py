#!/usr/bin/env python3
"""
XRPL Ecosystem Application Migration Script
Migrates existing applications to the new organized structure
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional

class ApplicationMigrator:
    """Migrates applications to the new organized structure"""
    
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.migration_log = []
        
        # Application mapping
        self.app_mapping = {
            # Trading applications
            "ai_trading": "applications/trading/ai-trading",
            "arbitrage_bot": "applications/trading/arbitrage-bot", 
            "yield_aggregator": "applications/trading/yield-aggregator",
            
            # Wallet applications
            "gaming_wallet_apps": "applications/wallets/gaming-wallet",
            "healthcare_app": "applications/wallets/healthcare-wallet",
            "crypto_tax_app": "applications/wallets/crypto-tax-wallet",
            
            # Marketplace applications
            "nft_marketplace": "applications/marketplaces/nft-marketplace",
            "fengshui_app": "applications/marketplaces/fengshui-nft",
            
            # Utility applications
            "inheritance_escrow": "applications/utilities/inheritance-escrow",
            "payment_processor": "applications/utilities/payment-processor",
            "staking_service": "applications/utilities/staking-service",
            "lending_platform": "applications/utilities/lending-platform",
            
            # Frontend applications
            "web_interface": "frontend/web-interface",
            "xaman_wallet_xapp": "frontend/xaman-wallet",
            "xrp_ai_ide_demo": "frontend/ai-ide",
            
            # Smart contracts
            "evm_sidechain": "smart-contracts/core",
            "ai_framework": "smart-contracts/applications/ai-framework",
            
            # Core components (already moved)
            "core": "core/xrpl-client",
            "dex": "core/dex-engine",
            "cross_chain_bridge": "core/bridge-engine",
            "security": "core/security"
        }
    
    def migrate_all(self) -> bool:
        """Migrate all applications to the new structure"""
        try:
            print("🚀 Starting XRPL Ecosystem Application Migration")
            print("=" * 60)
            
            # Create target directories
            self._create_target_directories()
            
            # Migrate applications
            self._migrate_applications()
            
            # Migrate smart contracts
            self._migrate_smart_contracts()
            
            # Migrate frontend applications
            self._migrate_frontend_applications()
            
            # Create application manifests
            self._create_application_manifests()
            
            # Generate migration report
            self._generate_migration_report()
            
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print(f"📊 Migrated {len(self.migration_log)} applications")
            print("📝 Check migration_report.md for details")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    def _create_target_directories(self):
        """Create target directory structure"""
        print("\n📁 Creating target directory structure...")
        
        directories = [
            "applications/trading",
            "applications/wallets", 
            "applications/marketplaces",
            "applications/utilities",
            "frontend",
            "smart-contracts/core",
            "smart-contracts/applications",
            "smart-contracts/deployment"
        ]
        
        for directory in directories:
            target_path = self.target_dir / directory
            target_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {directory}")
    
    def _migrate_applications(self):
        """Migrate applications to new structure"""
        print("\n📦 Migrating applications...")
        
        for source_name, target_path in self.app_mapping.items():
            if source_name in ["core", "dex", "cross_chain_bridge", "security"]:
                continue  # Skip core components (already moved)
                
            source_path = self.source_dir / source_name
            target_dir = self.target_dir / target_path
            
            if source_path.exists():
                self._migrate_application(source_path, target_dir, source_name)
            else:
                print(f"  ⚠️  Source not found: {source_name}")
    
    def _migrate_application(self, source_path: Path, target_dir: Path, app_name: str):
        """Migrate a single application"""
        try:
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy application files
            if source_path.is_dir():
                shutil.copytree(source_path, target_dir, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, target_dir)
            
            # Standardize application structure
            self._standardize_application_structure(target_dir, app_name)
            
            # Update package.json if it exists
            self._update_package_json(target_dir, app_name)
            
            # Create application README
            self._create_application_readme(target_dir, app_name)
            
            self.migration_log.append({
                "name": app_name,
                "source": str(source_path),
                "target": str(target_dir),
                "status": "success"
            })
            
            print(f"  ✓ Migrated: {app_name} -> {target_dir}")
            
        except Exception as e:
            print(f"  ❌ Failed to migrate {app_name}: {e}")
            self.migration_log.append({
                "name": app_name,
                "source": str(source_path),
                "target": str(target_dir),
                "status": "failed",
                "error": str(e)
            })
    
    def _standardize_application_structure(self, app_dir: Path, app_name: str):
        """Standardize application directory structure"""
        # Create standard directories
        standard_dirs = ["src", "tests", "docs", "contracts"]
        
        for dir_name in standard_dirs:
            dir_path = app_dir / dir_name
            if not dir_path.exists():
                dir_path.mkdir(exist_ok=True)
        
        # Move source files to src directory
        src_dir = app_dir / "src"
        for file_path in app_dir.iterdir():
            if file_path.is_file() and file_path.suffix in [".py", ".ts", ".tsx", ".js", ".jsx"]:
                if not any(file_path.name.startswith(prefix) for prefix in ["package.json", "README", "setup"]):
                    target_path = src_dir / file_path.name
                    if not target_path.exists():
                        shutil.move(str(file_path), str(target_path))
    
    def _update_package_json(self, app_dir: Path, app_name: str):
        """Update package.json for migrated applications"""
        package_json_path = app_dir / "package.json"
        
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                # Update package name
                package_data["name"] = f"@xrpl-ecosystem/{app_name.replace('_', '-')}"
                
                # Add ecosystem-specific scripts
                if "scripts" not in package_data:
                    package_data["scripts"] = {}
                
                package_data["scripts"].update({
                    "dev": "npm run start",
                    "build": "npm run build",
                    "test": "npm run test",
                    "lint": "npm run lint"
                })
                
                # Add ecosystem metadata
                package_data["xrpl-ecosystem"] = {
                    "type": self._get_application_type(app_name),
                    "category": self._get_application_category(app_name),
                    "version": "1.0.0"
                }
                
                with open(package_json_path, 'w') as f:
                    json.dump(package_data, f, indent=2)
                
            except Exception as e:
                print(f"    ⚠️  Failed to update package.json for {app_name}: {e}")
    
    def _get_application_type(self, app_name: str) -> str:
        """Get application type based on name"""
        if "trading" in app_name or "arbitrage" in app_name or "yield" in app_name:
            return "trading"
        elif "wallet" in app_name or "healthcare" in app_name or "tax" in app_name:
            return "wallet"
        elif "marketplace" in app_name or "nft" in app_name or "fengshui" in app_name:
            return "marketplace"
        elif "payment" in app_name or "staking" in app_name or "lending" in app_name:
            return "utility"
        else:
            return "application"
    
    def _get_application_category(self, app_name: str) -> str:
        """Get application category based on name"""
        if app_name in ["ai_trading", "arbitrage_bot", "yield_aggregator"]:
            return "trading"
        elif app_name in ["gaming_wallet_apps", "healthcare_app", "crypto_tax_app"]:
            return "wallets"
        elif app_name in ["nft_marketplace", "fengshui_app"]:
            return "marketplaces"
        elif app_name in ["inheritance_escrow", "payment_processor", "staking_service", "lending_platform"]:
            return "utilities"
        else:
            return "other"
    
    def _create_application_readme(self, app_dir: Path, app_name: str):
        """Create standardized README for application"""
        readme_path = app_dir / "README.md"
        
        if not readme_path.exists():
            readme_content = f"""# {app_name.replace('_', ' ').title()}

## Overview

This application is part of the XRPL Ecosystem.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
npm install
```

## Usage

```bash
npm run dev
```

## API

Documentation coming soon.

## Contributing

Please see the main ecosystem [Contributing Guide](../../docs/guides/CONTRIBUTING.md).

## License

MIT License - see [LICENSE](../../LICENSE) file for details.
"""
            
            readme_path.write_text(readme_content)
    
    def _migrate_smart_contracts(self):
        """Migrate smart contracts to new structure"""
        print("\n🔗 Migrating smart contracts...")
        
        # Migrate EVM sidechain contracts
        evm_source = self.source_dir / "evm_sidechain" / "contracts"
        if evm_source.exists():
            target_dir = self.target_dir / "smart-contracts" / "core"
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for contract_file in evm_source.iterdir():
                if contract_file.suffix == ".sol":
                    shutil.copy2(contract_file, target_dir)
                    print(f"  ✓ Migrated contract: {contract_file.name}")
        
        # Migrate AI framework contracts
        ai_source = self.source_dir / "ai_framework" / "contracts"
        if ai_source.exists():
            target_dir = self.target_dir / "smart-contracts" / "applications" / "ai-framework"
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for contract_file in ai_source.iterdir():
                if contract_file.suffix == ".sol":
                    shutil.copy2(contract_file, target_dir)
                    print(f"  ✓ Migrated AI contract: {contract_file.name}")
    
    def _migrate_frontend_applications(self):
        """Migrate frontend applications"""
        print("\n🎨 Migrating frontend applications...")
        
        # Web interface
        web_source = self.source_dir / "web_interface"
        if web_source.exists():
            target_dir = self.target_dir / "frontend" / "web-interface"
            self._migrate_application(web_source, target_dir, "web-interface")
        
        # Xaman wallet
        xaman_source = self.source_dir / "xaman_wallet_xapp"
        if xaman_source.exists():
            target_dir = self.target_dir / "frontend" / "xaman-wallet"
            self._migrate_application(xaman_source, target_dir, "xaman-wallet")
        
        # AI IDE
        ai_ide_source = self.source_dir / "xrp_ai_ide_demo"
        if ai_ide_source.exists():
            target_dir = self.target_dir / "frontend" / "ai-ide"
            self._migrate_application(ai_ide_source, target_dir, "ai-ide")
    
    def _create_application_manifests(self):
        """Create application manifests for the ecosystem"""
        print("\n📋 Creating application manifests...")
        
        manifest = {
            "ecosystem": "xrpl-ecosystem",
            "version": "1.0.0",
            "applications": []
        }
        
        for migration in self.migration_log:
            if migration["status"] == "success":
                app_info = {
                    "name": migration["name"],
                    "type": self._get_application_type(migration["name"]),
                    "category": self._get_application_category(migration["name"]),
                    "path": migration["target"],
                    "status": "active"
                }
                manifest["applications"].append(app_info)
        
        manifest_path = self.target_dir / "applications" / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"  ✓ Created application manifest: {manifest_path}")
    
    def _generate_migration_report(self):
        """Generate migration report"""
        report_path = self.target_dir / "migration_report.md"
        
        report_content = f"""# XRPL Ecosystem Migration Report

## Migration Summary

- **Total Applications**: {len(self.migration_log)}
- **Successful Migrations**: {len([m for m in self.migration_log if m['status'] == 'success'])}
- **Failed Migrations**: {len([m for m in self.migration_log if m['status'] == 'failed'])}

## Migration Details

### Successful Migrations

"""
        
        for migration in self.migration_log:
            if migration["status"] == "success":
                report_content += f"- **{migration['name']}**: {migration['source']} -> {migration['target']}\n"
        
        report_content += "\n### Failed Migrations\n\n"
        
        for migration in self.migration_log:
            if migration["status"] == "failed":
                report_content += f"- **{migration['name']}**: {migration.get('error', 'Unknown error')}\n"
        
        report_content += f"""
## Next Steps

1. Review migrated applications
2. Update import paths in code
3. Test applications in new structure
4. Update documentation
5. Deploy to production

## Application Structure

```
xrpl-ecosystem/
├── applications/
│   ├── trading/
│   ├── wallets/
│   ├── marketplaces/
│   └── utilities/
├── frontend/
│   ├── web-interface/
│   ├── xaman-wallet/
│   └── ai-ide/
├── smart-contracts/
│   ├── core/
│   └── applications/
└── core/
    ├── xrpl-client/
    ├── dex-engine/
    ├── bridge-engine/
    └── security/
```

---
*Migration completed on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        report_path.write_text(report_content)
        print(f"  ✓ Generated migration report: {report_path}")

def main():
    """Main migration function"""
    import sys
    
    # Get source and target directories
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = input("Enter source directory path (default: ../): ").strip() or "../"
    
    if len(sys.argv) > 2:
        target_dir = sys.argv[2]
    else:
        target_dir = input("Enter target directory path (default: .): ").strip() or "."
    
    # Validate paths
    if not Path(source_dir).exists():
        print(f"❌ Source directory does not exist: {source_dir}")
        return
    
    if not Path(target_dir).exists():
        print(f"❌ Target directory does not exist: {target_dir}")
        return
    
    # Run migration
    migrator = ApplicationMigrator(source_dir, target_dir)
    success = migrator.migrate_all()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("📝 Check migration_report.md for details")
    else:
        print("\n❌ Migration failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
