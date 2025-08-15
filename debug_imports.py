#!/usr/bin/env python3
"""
🔍 Import Diagnostic Script
Test module imports to identify issues
"""

import sys
import os

def test_imports():
    """Test all module imports"""
    print("🔍 Testing Module Imports")
    print("=" * 50)
    
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")
    
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print("✅ Added current directory to Python path")
    
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    # Test each module import
    modules_to_test = [
        ("modules.auth", "auth module"),
        ("modules.config", "config module"),
        ("modules.data_manager", "data_manager module"),
        ("modules.ui_manager", "ui_manager module"),
        ("modules.batch_manager", "batch_manager module"),
        ("modules.visualizations", "visualizations module"),
        ("modules.utils", "utils module"),
    ]
    
    results = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}: SUCCESS")
            results.append((description, "SUCCESS", None))
        except ImportError as e:
            print(f"❌ {description}: FAILED - {e}")
            results.append((description, "FAILED", str(e)))
        except Exception as e:
            print(f"⚠️  {description}: ERROR - {e}")
            results.append((description, "ERROR", str(e)))
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    success_count = sum(1 for _, status, _ in results if status == "SUCCESS")
    total_count = len(results)
    
    print(f"✅ Successful imports: {success_count}/{total_count}")
    
    if success_count < total_count:
        print("\n❌ Failed imports:")
        for description, status, error in results:
            if status != "SUCCESS":
                print(f"  - {description}: {error}")
    
    return success_count == total_count

def check_file_structure():
    """Check if all required files exist"""
    print("\n📁 Checking File Structure")
    print("=" * 50)
    
    required_files = [
        "modules/__init__.py",
        "modules/auth.py",
        "modules/config.py",
        "modules/data_manager.py",
        "modules/ui_manager.py",
        "modules/batch_manager.py",
        "modules/visualizations.py",
        "modules/utils.py",
        "app_modular.py",
        "requirements.txt",
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {len(missing_files)}")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def main():
    """Main diagnostic function"""
    print("🚀 PJI Law Reports - Import Diagnostics")
    print("=" * 60)
    
    # Check file structure
    files_ok = check_file_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    print("\n" + "=" * 60)
    print("🎯 Final Results:")
    print(f"📁 File structure: {'✅ OK' if files_ok else '❌ ISSUES'}")
    print(f"📦 Module imports: {'✅ OK' if imports_ok else '❌ ISSUES'}")
    
    if files_ok and imports_ok:
        print("\n🎉 All checks passed! Your modules should work correctly.")
    else:
        print("\n⚠️  Issues detected. Please fix the problems above.")
    
    return files_ok and imports_ok

if __name__ == "__main__":
    main()
