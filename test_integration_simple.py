#!/usr/bin/env python3
"""
Simplified Integration Test for Modular PJI Law Reports Application
Tests all modules working together with graceful dependency handling
"""

import sys
import os
import pandas as pd
from datetime import date, datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_structure():
    """Test that all module files exist and have correct structure"""
    print("🔍 Testing module structure...")
    
    required_modules = [
        "modules/__init__.py",
        "modules/config.py",
        "modules/auth.py",
        "modules/data_manager.py",
        "modules/batch_manager.py",
        "modules/ui_manager.py",
        "modules/visualizations.py",
        "modules/utils.py"
    ]
    
    missing_modules = []
    for module in required_modules:
        if not os.path.exists(module):
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing modules: {missing_modules}")
        return False
    
    print("✅ All module files exist")
    return True

def test_config_imports():
    """Test config module imports"""
    print("\n🔍 Testing config imports...")
    
    try:
        from modules.config import (
            TAB_NAMES, TAB_FALLBACKS, REQUIRED_COLUMNS_CALLS,
            ALLOWED_CALLS, CATEGORY_CALLS, RENAME_NAME_CALLS,
            PRACTICE_AREAS, MONTHS_MAP, MONTHS_MAP_NAMES
        )
        print("✅ Config module imports work")
        return True
    except Exception as e:
        print(f"❌ Config imports failed: {e}")
        return False

def test_utils_imports():
    """Test utils module imports"""
    print("\n🔍 Testing utils imports...")
    
    try:
        from modules.utils import (
            calculate_percentage, html_escape, normalize_string,
            month_key_from_range, validate_single_month_range
        )
        print("✅ Utils module imports work")
        return True
    except Exception as e:
        print(f"❌ Utils imports failed: {e}")
        return False

def test_utils_functionality():
    """Test utils functions work correctly"""
    print("\n🔍 Testing utils functionality...")
    
    try:
        from modules.utils import (
            calculate_percentage, html_escape, normalize_string,
            month_key_from_range, validate_single_month_range
        )
        
        # Test calculate_percentage
        result = calculate_percentage(25, 100)
        if result == 25.0:
            print("✅ calculate_percentage works")
        else:
            print(f"❌ calculate_percentage failed: {result}")
            return False
        
        # Test html_escape
        escaped = html_escape("<test>&")
        if escaped == "&lt;test&gt;&amp;":
            print("✅ html_escape works")
        else:
            print(f"❌ html_escape failed: {escaped}")
            return False
        
        # Test month_key_from_range
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        month_key = month_key_from_range(start_date, end_date)
        if month_key == "2024-01":
            print("✅ month_key_from_range works")
        else:
            print(f"❌ month_key_from_range failed: {month_key}")
            return False
        
        # Test validate_single_month_range
        is_valid, message = validate_single_month_range(start_date, end_date)
        if is_valid:
            print("✅ validate_single_month_range works")
        else:
            print(f"❌ validate_single_month_range failed: {message}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Utils functionality failed: {e}")
        return False

def test_manager_imports():
    """Test manager imports with dependency handling"""
    print("\n🔍 Testing manager imports...")
    
    results = []
    
    # Test Data Manager import
    try:
        from modules.data_manager import DataManager
        print("✅ DataManager import works")
        results.append(True)
    except ImportError as e:
        if "gspread" in str(e):
            print("⚠️  DataManager import skipped (gspread not available)")
            results.append(True)  # Not a failure, just missing dependency
        else:
            print(f"❌ DataManager import failed: {e}")
            results.append(False)
    except Exception as e:
        print(f"❌ DataManager import failed: {e}")
        results.append(False)
    
    # Test UI Manager import
    try:
        from modules.ui_manager import UIManager
        print("✅ UIManager import works")
        results.append(True)
    except Exception as e:
        print(f"❌ UIManager import failed: {e}")
        results.append(False)
    
    # Test Batch Manager import
    try:
        from modules.batch_manager import BatchManager
        print("✅ BatchManager import works")
        results.append(True)
    except Exception as e:
        print(f"❌ BatchManager import failed: {e}")
        results.append(False)
    
    # Test Visualization Manager import
    try:
        from modules.visualizations import VisualizationManager
        print("✅ VisualizationManager import works")
        results.append(True)
    except Exception as e:
        print(f"❌ VisualizationManager import failed: {e}")
        results.append(False)
    
    return all(results)

def test_data_processing_logic():
    """Test data processing logic without external dependencies"""
    print("\n🔍 Testing data processing logic...")
    
    try:
        # Test date validation logic
        from modules.utils import validate_single_month_range, month_key_from_range
        
        # Valid date range
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        is_valid, message = validate_single_month_range(start_date, end_date)
        if not is_valid:
            print(f"❌ Valid date range failed: {message}")
            return False
        
        # Invalid date range (different months)
        start_date = date(2024, 1, 1)
        end_date = date(2024, 2, 1)
        is_valid, message = validate_single_month_range(start_date, end_date)
        if is_valid:
            print("❌ Invalid date range should have failed")
            return False
        
        # Month key generation
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        month_key = month_key_from_range(start_date, end_date)
        if month_key != "2024-01":
            print(f"❌ Month key generation failed: {month_key}")
            return False
        
        print("✅ Data processing logic works")
        return True
        
    except Exception as e:
        print(f"❌ Data processing logic failed: {e}")
        return False

def test_ui_logic():
    """Test UI logic without Streamlit dependencies"""
    print("\n🔍 Testing UI logic...")
    
    try:
        from modules.ui_manager import UIManager
        
        # Create UI manager
        ui_manager = UIManager()
        
        # Test HTML escaping
        escaped = ui_manager._html_escape("<test>&")
        if escaped == "&lt;test&gt;&amp;":
            print("✅ HTML escaping works")
        else:
            print(f"❌ HTML escaping failed: {escaped}")
            return False
        
        # Test date parsing
        test_series = pd.Series(["2024-01-01", "2024-01-02"])
        parsed = ui_manager._to_ts(test_series)
        if len(parsed) == 2:
            print("✅ Date parsing works")
        else:
            print("❌ Date parsing failed")
            return False
        
        # Test data filtering logic
        sample_data = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Total Calls': [10, 15],
            'Completed Calls': [8, 12],
            'Month-Year': ['2024-01', '2024-01']
        })
        
        filtered = ui_manager._filter_calls_data(sample_data, "2024", "January", "All", "All")
        if len(filtered) == 2:
            print("✅ Data filtering works")
        else:
            print(f"❌ Data filtering failed: got {len(filtered)} rows")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ UI logic failed: {e}")
        return False

def test_visualization_logic():
    """Test visualization logic without Plotly dependencies"""
    print("\n🔍 Testing visualization logic...")
    
    try:
        from modules.visualizations import VisualizationManager
        
        # Create visualization manager
        viz_manager = VisualizationManager()
        
        # Test plotly availability check
        if hasattr(viz_manager, 'plotly_available'):
            print("✅ Plotly availability check works")
        else:
            print("❌ Plotly availability check missing")
            return False
        
        # Test data generation logic
        x_labels, retention_rates, scheduled_rates, show_up_rates, x_label = viz_manager._generate_viz_data(
            "Year to date", 2024, 1, "Q1"
        )
        
        if len(x_labels) == 12 and len(retention_rates) == 12:
            print("✅ Data generation logic works")
        else:
            print(f"❌ Data generation logic failed: {len(x_labels)} labels, {len(retention_rates)} rates")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization logic failed: {e}")
        return False

def test_batch_management_logic():
    """Test batch management logic"""
    print("\n🔍 Testing batch management logic...")
    
    try:
        from modules.batch_manager import BatchManager
        
        # Create batch manager
        batch_manager = BatchManager()
        
        # Test batch ID generation
        batch_id = batch_manager.generate_batch_id()
        if batch_id and len(batch_id) > 0:
            print("✅ Batch ID generation works")
        else:
            print("❌ Batch ID generation failed")
            return False
        
        # Test metadata addition
        sample_data = pd.DataFrame({'col1': [1, 2, 3]})
        enhanced_data = batch_manager.add_batch_metadata(sample_data, batch_id, date.today(), date.today(), date.today())
        
        if '__batch_id' in enhanced_data.columns:
            print("✅ Batch metadata addition works")
        else:
            print("❌ Batch metadata addition failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Batch management logic failed: {e}")
        return False

def test_end_to_end_logic():
    """Test end-to-end logic without external dependencies"""
    print("\n🔍 Testing end-to-end logic...")
    
    try:
        # Import all managers
        from modules.batch_manager import BatchManager
        from modules.ui_manager import UIManager
        from modules.visualizations import VisualizationManager
        
        # Create managers
        batch_manager = BatchManager()
        ui_manager = UIManager()
        viz_manager = VisualizationManager()
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Total Calls': [10, 15],
            'Completed Calls': [8, 12],
            'Month-Year': ['2024-01', '2024-01']
        })
        
        # Test workflow steps
        # 1. Data filtering
        filtered_data = ui_manager._filter_calls_data(sample_data, "2024", "January", "All", "All")
        if len(filtered_data) == 2:
            print("✅ Step 1: Data filtering works")
        else:
            print("❌ Step 1: Data filtering failed")
            return False
        
        # 2. Batch processing
        batch_id = batch_manager.generate_batch_id()
        enhanced_data = batch_manager.add_batch_metadata(filtered_data, batch_id, date.today(), date.today(), date.today())
        if '__batch_id' in enhanced_data.columns:
            print("✅ Step 2: Batch processing works")
        else:
            print("❌ Step 2: Batch processing failed")
            return False
        
        # 3. Visualization preparation
        viz_manager.render_calls_visualizations(sample_data, filtered_data)
        print("✅ Step 3: Visualization preparation works")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end logic failed: {e}")
        return False

def main():
    """Run all simplified integration tests"""
    print("🧪 Simplified Integration Testing for Modular PJI Law Reports Application")
    print("=" * 70)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Module Structure", test_module_structure()))
    test_results.append(("Config Imports", test_config_imports()))
    test_results.append(("Utils Imports", test_utils_imports()))
    test_results.append(("Utils Functionality", test_utils_functionality()))
    test_results.append(("Manager Imports", test_manager_imports()))
    test_results.append(("Data Processing Logic", test_data_processing_logic()))
    test_results.append(("UI Logic", test_ui_logic()))
    test_results.append(("Visualization Logic", test_visualization_logic()))
    test_results.append(("Batch Management Logic", test_batch_management_logic()))
    test_results.append(("End-to-End Logic", test_end_to_end_logic()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Simplified Integration Test Results Summary")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 70)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All simplified integration tests passed!")
        print("🚀 The modular system logic is working correctly.")
        print("💡 External dependencies (gspread, plotly) can be added later.")
    else:
        print("⚠️  Some tests failed. Check the errors above for details.")
        print("💡 You can debug these issues later as mentioned.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
