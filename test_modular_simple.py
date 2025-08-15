# test_modular_simple.py
# Simplified test script for modular structure - no external dependencies

import sys
import os

def test_module_structure():
    """Test that all module files exist and have basic structure"""
    print("Testing module file structure...")
    
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
    
    missing_files = []
    for module_file in required_modules:
        if not os.path.exists(module_file):
            missing_files.append(module_file)
        else:
            print(f"✅ {module_file} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All module files exist")
    return True

def test_config_imports():
    """Test config module imports without Streamlit"""
    print("\nTesting config module imports...")
    
    try:
        # Mock streamlit for testing
        sys.modules['streamlit'] = type('MockStreamlit', (), {
            'set_page_config': lambda **kwargs: None
        })()
        
        from modules.config import (
            TAB_NAMES, TAB_FALLBACKS, REQUIRED_COLUMNS_CALLS, 
            ALLOWED_CALLS, CATEGORY_CALLS, PRACTICE_AREAS,
            DISPLAY_NAME_OVERRIDES, INITIALS_TO_ATTORNEY,
            INTAKE_SPECIALISTS, MONTHS_MAP, MONTHS_MAP_NAMES
        )
        
        # Test that all expected constants exist
        assert isinstance(TAB_NAMES, dict), "TAB_NAMES should be a dict"
        assert isinstance(TAB_FALLBACKS, dict), "TAB_FALLBACKS should be a dict"
        assert isinstance(REQUIRED_COLUMNS_CALLS, list), "REQUIRED_COLUMNS_CALLS should be a list"
        assert isinstance(ALLOWED_CALLS, list), "ALLOWED_CALLS should be a list"
        assert isinstance(CATEGORY_CALLS, dict), "CATEGORY_CALLS should be a dict"
        assert isinstance(PRACTICE_AREAS, dict), "PRACTICE_AREAS should be a dict"
        assert isinstance(DISPLAY_NAME_OVERRIDES, dict), "DISPLAY_NAME_OVERRIDES should be a dict"
        assert isinstance(INITIALS_TO_ATTORNEY, dict), "INITIALS_TO_ATTORNEY should be a dict"
        assert isinstance(INTAKE_SPECIALISTS, list), "INTAKE_SPECIALISTS should be a list"
        assert isinstance(MONTHS_MAP, dict), "MONTHS_MAP should be a dict"
        assert isinstance(MONTHS_MAP_NAMES, dict), "MONTHS_MAP_NAMES should be a dict"
        
        print("✅ All config constants are properly defined")
        return True
        
    except Exception as e:
        print(f"❌ Config import test failed: {e}")
        return False

def test_utils_functions():
    """Test utility functions without external dependencies"""
    print("\nTesting utility functions...")
    
    try:
        from modules.utils import (
            calculate_percentage, html_escape, normalize_string,
            month_key_from_range, validate_single_month_range
        )
        
        # Test calculate_percentage
        assert calculate_percentage(50, 100) == 50, "calculate_percentage(50, 100) should return 50"
        assert calculate_percentage(0, 100) == 0, "calculate_percentage(0, 100) should return 0"
        assert calculate_percentage(50, 0) == 0, "calculate_percentage(50, 0) should return 0"
        print("✅ calculate_percentage works correctly")
        
        # Test html_escape
        assert html_escape("<test>") == "&lt;test&gt;", "html_escape should escape HTML"
        assert html_escape("&") == "&amp;", "html_escape should escape &"
        print("✅ html_escape works correctly")
        
        # Test normalize_string
        assert normalize_string("  Test String  ") == "test string", "normalize_string should normalize"
        assert normalize_string("Test_String") == "test string", "normalize_string should handle underscores"
        print("✅ normalize_string works correctly")
        
        # Test month_key_from_range (mock datetime)
        from datetime import date
        test_start = date(2024, 1, 1)
        test_end = date(2024, 1, 31)
        assert month_key_from_range(test_start, test_end) == "2024-01", "month_key_from_range should work"
        print("✅ month_key_from_range works correctly")
        
        # Test validate_single_month_range
        valid, msg = validate_single_month_range(test_start, test_end)
        assert valid, "validate_single_month_range should return True for valid range"
        
        invalid_start = date(2024, 2, 1)
        valid, msg = validate_single_month_range(test_start, invalid_start)
        assert not valid, "validate_single_month_range should return False for invalid range"
        print("✅ validate_single_month_range works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False

def test_class_imports():
    """Test that all classes can be imported (without initialization)"""
    print("\nTesting class imports...")
    
    try:
        # Mock streamlit for class imports
        if 'streamlit' not in sys.modules:
            sys.modules['streamlit'] = type('MockStreamlit', (), {
                'session_state': {},
                'set_page_config': lambda **kwargs: None,
                'sidebar': type('MockSidebar', (), {})(),
                'expander': lambda **kwargs: type('MockExpander', (), {})(),
                'button': lambda **kwargs: False,
                'selectbox': lambda **kwargs: "All",
                'columns': lambda n: [type('MockCol', (), {})() for _ in range(n)],
                'subheader': lambda **kwargs: None,
                'markdown': lambda **kwargs: None,
                'info': lambda **kwargs: None,
                'success': lambda **kwargs: None,
                'warning': lambda **kwargs: None,
                'error': lambda **kwargs: None,
                'cache_data': lambda **kwargs: lambda f: f,
                'cache_resource': lambda **kwargs: lambda f: f,
                'file_uploader': lambda **kwargs: None,
                'date_input': lambda **kwargs: None,
                'checkbox': lambda **kwargs: False,
                'number_input': lambda **kwargs: 2024,
                'container': lambda **kwargs: type('MockContainer', (), {})(),
                'divider': lambda **kwargs: None,
                'caption': lambda **kwargs: None,
                'dataframe': lambda **kwargs: None,
                'download_button': lambda **kwargs: None,
                'plotly_chart': lambda **kwargs: None,
                'stop': lambda: None,
                'rerun': lambda: None,
                'secrets': type('MockSecrets', (), {
                    'get': lambda key, default=None: default
                })(),
            })()
        
        # Test class imports
        from modules.data_manager import DataManager
        print("✅ DataManager class imported")
        
        from modules.batch_manager import BatchManager
        print("✅ BatchManager class imported")
        
        from modules.ui_manager import UIManager
        print("✅ UIManager class imported")
        
        from modules.visualizations import VisualizationManager
        print("✅ VisualizationManager class imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Class import test failed: {e}")
        return False

def test_main_app_import():
    """Test that the main app can be imported"""
    print("\nTesting main app import...")
    
    try:
        # Mock streamlit for main app
        if 'streamlit' not in sys.modules:
            sys.modules['streamlit'] = type('MockStreamlit', (), {
                'set_page_config': lambda **kwargs: None,
                'title': lambda **kwargs: None,
                'session_state': {},
                'sidebar': type('MockSidebar', (), {})(),
                'expander': lambda **kwargs: type('MockExpander', (), {})(),
                'secrets': type('MockSecrets', (), {
                    'get': lambda key, default=None: default
                })(),
            })()
        
        # Mock datetime
        sys.modules['datetime'] = type('MockDatetime', (), {
            'date': type('MockDate', (), {
                'today': lambda: type('MockDateObj', (), {'year': 2024, 'month': 1, 'day': 1})()
            })()
        })()
        
        # Try to import the main app
        import app_modular
        print("✅ app_modular.py imported successfully")
        
        # Check that main function exists
        assert hasattr(app_modular, 'main'), "app_modular should have a main function"
        print("✅ main function exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Main app import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Modular PJI Law Reports Application (Simplified)")
    print("=" * 60)
    
    # Run tests
    structure_ok = test_module_structure()
    config_ok = test_config_imports()
    utils_ok = test_utils_functions()
    classes_ok = test_class_imports()
    main_ok = test_main_app_import()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"Module Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    print(f"Config Imports:   {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Utility Functions: {'✅ PASS' if utils_ok else '❌ FAIL'}")
    print(f"Class Imports:    {'✅ PASS' if classes_ok else '❌ FAIL'}")
    print(f"Main App Import:  {'✅ PASS' if main_ok else '❌ FAIL'}")
    
    all_passed = all([structure_ok, config_ok, utils_ok, classes_ok, main_ok])
    
    if all_passed:
        print("\n🎉 All tests passed! The modular structure is working correctly.")
        print("\n📝 Next steps:")
        print("1. Run 'streamlit run app_modular.py' to test the full application")
        print("2. Configure your Streamlit secrets for Google Sheets access")
        print("3. Test with real data uploads")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("- Ensure all module files exist in the modules/ directory")
        print("- Check that imports are correct in each module")
        print("- Verify that all required constants are defined in config.py")

if __name__ == "__main__":
    main()
