#!/usr/bin/env python3
"""
🔍 Deployment Package Verification Script
Verify that all required files are present in the deployment package
"""

import os
import sys

def verify_deployment_package():
    """Verify all required files are present"""
    print("🔍 PJI Law Reports - Deployment Package Verification")
    print("=" * 60)
    
    # Required files in root directory
    required_root_files = [
        "app_modular.py",
        "app_modular_alternative.py",
        "requirements.txt",
        ".gitignore",
        "README.md",
        "README_MODULAR.md",
        "MODULAR_DOCUMENTATION.md",
        "SECURITY_GUIDE.md",
        "NOVICE_SECURITY_GUIDE.md",
        "TESTING_GUIDE.md",
        "TROUBLESHOOTING.md",
        "IMPORT_FIX_GUIDE.md",
        "TOML_SETUP_GUIDE.md",
        "secrets_template.toml",
        "generate_password.py",
        "debug_imports.py",
        "test_modular_simple.py",
        "test_integration_simple.py",
        "test_app_integration.py",
        "test_data_generator.py",
    ]
    
    # Required files in modules directory
    required_module_files = [
        "modules/__init__.py",
        "modules/auth.py",
        "modules/config.py",
        "modules/data_manager.py",
        "modules/ui_manager.py",
        "modules/batch_manager.py",
        "modules/visualizations.py",
        "modules/utils.py",
    ]
    
    all_required_files = required_root_files + required_module_files
    
    print("📁 Checking Required Files:")
    print("-" * 40)
    
    missing_files = []
    present_files = []
    
    for file_path in all_required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            present_files.append(file_path)
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"✅ Present files: {len(present_files)}")
    print(f"❌ Missing files: {len(missing_files)}")
    print(f"📦 Total required: {len(all_required_files)}")
    
    if missing_files:
        print(f"\n❌ Missing files ({len(missing_files)}):")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("\n🎉 All required files are present!")
        return True

def check_file_sizes():
    """Check that files have reasonable sizes (not empty)"""
    print("\n📏 Checking File Sizes:")
    print("-" * 40)
    
    critical_files = [
        "app_modular.py",
        "modules/__init__.py",
        "modules/auth.py",
        "modules/config.py",
        "modules/data_manager.py",
        "modules/ui_manager.py",
        "modules/batch_manager.py",
        "modules/visualizations.py",
        "modules/utils.py",
        "requirements.txt",
    ]
    
    empty_files = []
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size == 0:
                print(f"⚠️  {file_path} - EMPTY (0 bytes)")
                empty_files.append(file_path)
            elif size < 100:
                print(f"⚠️  {file_path} - VERY SMALL ({size} bytes)")
            else:
                print(f"✅ {file_path} - {size} bytes")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            empty_files.append(file_path)
    
    if empty_files:
        print(f"\n⚠️  Empty or missing critical files: {len(empty_files)}")
        return False
    else:
        print("\n✅ All critical files have content")
        return True

def main():
    """Main verification function"""
    print("🚀 PJI Law Reports - Deployment Verification")
    print("=" * 60)
    
    # Check file presence
    files_ok = verify_deployment_package()
    
    # Check file sizes
    sizes_ok = check_file_sizes()
    
    print("\n" + "=" * 60)
    print("🎯 Final Results:")
    print(f"📁 File presence: {'✅ OK' if files_ok else '❌ ISSUES'}")
    print(f"📏 File sizes: {'✅ OK' if sizes_ok else '❌ ISSUES'}")
    
    if files_ok and sizes_ok:
        print("\n🎉 Deployment package is complete and ready!")
        print("✅ You can now upload this to GitHub and deploy to Streamlit")
    else:
        print("\n⚠️  Issues detected. Please fix the problems above.")
        print("❌ Do not deploy until all issues are resolved")
    
    return files_ok and sizes_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
