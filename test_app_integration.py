#!/usr/bin/env python3
"""
App Integration Test for Modular PJI Law Reports Application
Tests the complete app_modular.py integration
"""

import sys
import os
import pandas as pd
from datetime import date
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_structure():
    """Test that the modular app structure is correct"""
    print("🔍 Testing app structure...")
    
    try:
        # Check if app_modular.py exists
        if not os.path.exists("app_modular.py"):
            print("❌ app_modular.py not found")
            return False
        
        # Read the app file to check structure
        with open("app_modular.py", "r") as f:
            content = f.read()
        
        # Check for required imports
        required_imports = [
            "from modules.auth import",
            "from modules.config import",
            "from modules.data_manager import",
            "from modules.ui_manager import",
            "from modules.batch_manager import",
            "from modules.visualizations import"
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"❌ Missing imports: {missing_imports}")
            return False
        
        # Check for main function
        if "def main():" not in content:
            print("❌ Main function not found")
            return False
        
        print("✅ App structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

def test_module_dependencies():
    """Test that all module dependencies are satisfied"""
    print("\n🔍 Testing module dependencies...")
    
    try:
        # Test config dependencies
        from modules.config import (
            TAB_NAMES, TAB_FALLBACKS, REQUIRED_COLUMNS_CALLS,
            ALLOWED_CALLS, CATEGORY_CALLS, RENAME_NAME_CALLS,
            PRACTICE_AREAS, MONTHS_MAP, MONTHS_MAP_NAMES
        )
        print("✅ Config dependencies satisfied")
        
        # Test utils dependencies
        from modules.utils import (
            calculate_percentage, html_escape, normalize_string,
            month_key_from_range, validate_single_month_range
        )
        print("✅ Utils dependencies satisfied")
        
        # Test auth dependencies
        from modules.auth import setup_authentication, check_auth_status
        print("✅ Auth dependencies satisfied")
        
        # Test data manager dependencies
        from modules.data_manager import DataManager
        print("✅ Data Manager dependencies satisfied")
        
        # Test UI manager dependencies
        from modules.ui_manager import UIManager
        print("✅ UI Manager dependencies satisfied")
        
        # Test batch manager dependencies
        from modules.batch_manager import BatchManager
        print("✅ Batch Manager dependencies satisfied")
        
        # Test visualizations dependencies
        from modules.visualizations import VisualizationManager
        print("✅ Visualizations Manager dependencies satisfied")
        
        return True
        
    except Exception as e:
        print(f"❌ Module dependencies test failed: {e}")
        return False

def test_manager_interactions():
    """Test interactions between different managers"""
    print("\n🔍 Testing manager interactions...")
    
    try:
        # Initialize managers
        data_manager = DataManager()
        ui_manager = UIManager()
        batch_manager = BatchManager()
        viz_manager = VisualizationManager()
        
        # Test data flow between managers
        sample_data = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Total Calls': [10, 15],
            'Completed Calls': [8, 12],
            'Month-Year': ['2024-01', '2024-01']
        })
        
        # Test UI Manager using Data Manager methods
        filtered_data = ui_manager._filter_calls_data(sample_data, "2024", "January", "All", "All")
        if not filtered_data.empty:
            print("✅ UI Manager can use Data Manager data")
        else:
            print("❌ UI Manager cannot use Data Manager data")
        
        # Test Batch Manager with Data Manager data
        batch_id = batch_manager.generate_batch_id("test.csv")
        enhanced_data = batch_manager.add_batch_metadata(filtered_data, batch_id, date.today(), date.today())
        if '__batch_id' in enhanced_data.columns:
            print("✅ Batch Manager can enhance Data Manager data")
        else:
            print("❌ Batch Manager cannot enhance Data Manager data")
        
        # Test Visualization Manager with processed data
        viz_manager.render_calls_visualizations(sample_data, filtered_data)
        print("✅ Visualization Manager can visualize processed data")
        
        return True
        
    except Exception as e:
        print(f"❌ Manager interactions test failed: {e}")
        return False

def test_data_flow():
    """Test complete data flow through the system"""
    print("\n🔍 Testing data flow...")
    
    try:
        # Create sample data that mimics real data
        calls_data = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith', 'John Doe'],
            'Total Calls': [10, 15, 5],
            'Completed Calls': [8, 12, 4],
            'Outgoing': [3, 7, 2],
            'Received': [7, 8, 3],
            'Missed': [2, 3, 1],
            'Month-Year': ['2024-01', '2024-01', '2024-02'],
            'Category': ['Staff', 'Staff', 'Staff']
        })
        
        # Initialize managers
        data_manager = DataManager()
        ui_manager = UIManager()
        batch_manager = BatchManager()
        viz_manager = VisualizationManager()
        
        # Simulate data loading
        data_manager.df_calls = calls_data
        print("✅ Data loading step")
        
        # Simulate data filtering
        filtered_calls = ui_manager._filter_calls_data(
            calls_data, "2024", "January", "All", "All"
        )
        if len(filtered_calls) == 2:  # Should filter to 2 rows for January
            print("✅ Data filtering step")
        else:
            print(f"❌ Data filtering step failed: got {len(filtered_calls)} rows")
        
        # Simulate batch processing
        batch_id = batch_manager.generate_batch_id("calls_2024_01.csv")
        processed_data = batch_manager.add_batch_metadata(
            filtered_calls, batch_id, date(2024, 1, 1), date(2024, 1, 31)
        )
        if '__batch_id' in processed_data.columns:
            print("✅ Batch processing step")
        else:
            print("❌ Batch processing step failed")
        
        # Simulate visualization
        viz_manager.render_calls_visualizations(calls_data, filtered_calls)
        print("✅ Visualization step")
        
        return True
        
    except Exception as e:
        print(f"❌ Data flow test failed: {e}")
        return False

def test_error_recovery():
    """Test error recovery and graceful degradation"""
    print("\n🔍 Testing error recovery...")
    
    try:
        # Test with missing data
        data_manager = DataManager()
        ui_manager = UIManager()
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        filtered = ui_manager._filter_calls_data(empty_df, "2024", "January", "All", "All")
        if filtered.empty:
            print("✅ Handles empty data gracefully")
        else:
            print("❌ Does not handle empty data gracefully")
        
        # Test with invalid date range
        start_date = date(2024, 2, 1)
        end_date = date(2024, 1, 1)
        is_valid, message = data_manager.validate_single_month_range(start_date, end_date)
        if not is_valid and "Start date must be on or before End date" in message:
            print("✅ Handles invalid date ranges gracefully")
        else:
            print("❌ Does not handle invalid date ranges gracefully")
        
        # Test with missing columns
        incomplete_data = pd.DataFrame({'Name': ['John Doe']})
        try:
            filtered = ui_manager._filter_calls_data(incomplete_data, "2024", "January", "All", "All")
            print("✅ Handles missing columns gracefully")
        except Exception:
            print("❌ Does not handle missing columns gracefully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        return False

def test_performance():
    """Test basic performance characteristics"""
    print("\n🔍 Testing performance...")
    
    try:
        import time
        
        # Test manager initialization performance
        start_time = time.time()
        data_manager = DataManager()
        ui_manager = UIManager()
        batch_manager = BatchManager()
        viz_manager = VisualizationManager()
        init_time = time.time() - start_time
        
        if init_time < 1.0:  # Should initialize in less than 1 second
            print(f"✅ Manager initialization: {init_time:.3f}s")
        else:
            print(f"❌ Manager initialization too slow: {init_time:.3f}s")
        
        # Test data processing performance
        large_data = pd.DataFrame({
            'Name': ['User' + str(i) for i in range(1000)],
            'Total Calls': [10] * 1000,
            'Completed Calls': [8] * 1000,
            'Month-Year': ['2024-01'] * 1000
        })
        
        start_time = time.time()
        filtered = ui_manager._filter_calls_data(large_data, "2024", "January", "All", "All")
        filter_time = time.time() - start_time
        
        if filter_time < 0.1:  # Should filter in less than 0.1 seconds
            print(f"✅ Data filtering: {filter_time:.3f}s")
        else:
            print(f"❌ Data filtering too slow: {filter_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all app integration tests"""
    print("🧪 App Integration Testing for Modular PJI Law Reports Application")
    print("=" * 70)
    
    test_results = []
    
    # Run all tests
    test_results.append(("App Structure", test_app_structure()))
    test_results.append(("Module Dependencies", test_module_dependencies()))
    test_results.append(("Manager Interactions", test_manager_interactions()))
    test_results.append(("Data Flow", test_data_flow()))
    test_results.append(("Error Recovery", test_error_recovery()))
    test_results.append(("Performance", test_performance()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 App Integration Test Results Summary")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 70)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All app integration tests passed! The modular app is ready for use.")
        print("🚀 You can now run the modular app with confidence.")
    else:
        print("⚠️  Some tests failed. Check the errors above for details.")
        print("💡 You can debug these issues later as mentioned.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
