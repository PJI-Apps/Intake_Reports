# Testing Guide for Modular PJI Law Reports

This guide explains how to test the modular application structure at different levels.

## 🧪 Testing Levels

### Level 1: Basic Structure Test (No Dependencies)
**File:** `test_modular_simple.py`

This test verifies the basic modular structure without requiring any external dependencies.

```bash
python test_modular_simple.py
```

**What it tests:**
- ✅ Module file structure
- ✅ Configuration imports
- ✅ Utility functions
- ❌ Class imports (requires external dependencies)
- ❌ Main app import (requires external dependencies)

**Expected Results:**
- Module Structure: ✅ PASS
- Config Imports: ✅ PASS  
- Utility Functions: ✅ PASS
- Class Imports: ❌ FAIL (expected - missing gspread)
- Main App Import: ❌ FAIL (expected - missing dependencies)

### Level 2: Streamlit Test (Minimal Configuration)
**File:** `test_streamlit_modular.py`

This test runs in Streamlit and tests the modular structure with mock configurations.

```bash
streamlit run test_streamlit_modular.py
```

**What it tests:**
- ✅ All module imports
- ✅ Configuration values
- ✅ Utility functions
- ✅ Class initialization (with mock secrets)
- ✅ Module structure display

**Expected Results:**
- All tests should pass
- Google Sheets connection will fail gracefully
- Authentication will use mock configuration

### Level 3: Full Application Test (With Dependencies)
**File:** `app_modular.py`

This is the complete application with all dependencies.

```bash
streamlit run app_modular.py
```

**Requirements:**
- All dependencies installed (`pip install -r requirements.txt`)
- Streamlit secrets configured
- Google Sheets access configured

## 📋 Prerequisites

### For Level 1 (Basic Test)
- Python 3.7+
- No additional dependencies required

### For Level 2 (Streamlit Test)
- Python 3.7+
- Streamlit (`pip install streamlit`)
- Basic dependencies (`pip install pandas`)

### For Level 3 (Full App)
- All dependencies from `requirements.txt`
- Streamlit secrets configuration
- Google Sheets access

## 🔧 Installation Steps

### 1. Install Basic Dependencies
```bash
pip install streamlit pandas
```

### 2. Install Full Dependencies (for complete app)
```bash
pip install -r requirements.txt
```

### 3. Configure Streamlit Secrets (for full app)
Create `.streamlit/secrets.toml`:
```toml
[gcp_service_account]
client_email = "your-service-account@project.iam.gserviceaccount.com"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"

[master_store]
sheet_url = "https://docs.google.com/spreadsheets/d/your-sheet-id"

[auth_config]
config = """
credentials:
  usernames:
    your_username:
      email: your_email@example.com
      name: Your Name
      password: $2b$12$hashed_password
cookie:
  expiry_days: 30
  key: your_cookie_key
  name: your_cookie_name
preauthorized:
  emails:
  - your_email@example.com
"""
```

## 🚀 Testing Workflow

### Step 1: Basic Structure Test
```bash
python test_modular_simple.py
```
**Expected:** 3/5 tests pass (structure, config, utils)

### Step 2: Streamlit Test
```bash
streamlit run test_streamlit_modular.py
```
**Expected:** All tests pass with mock configurations

### Step 3: Full App Test (Optional)
```bash
streamlit run app_modular.py
```
**Expected:** Full application with real data (if configured)

## 📊 Understanding Test Results

### ✅ Passing Tests
- **Module Structure:** All required files exist
- **Config Imports:** Configuration constants are properly defined
- **Utility Functions:** Helper functions work correctly
- **Class Imports:** Classes can be imported (with dependencies)
- **Main App Import:** Main application can be imported

### ❌ Failing Tests (Expected Without Dependencies)
- **Class Imports:** Missing `gspread`, `streamlit_authenticator`, etc.
- **Main App Import:** Missing external dependencies

### 🔧 Common Issues

#### Import Errors
```
ModuleNotFoundError: No module named 'gspread'
```
**Solution:** Install dependencies or use Level 1/2 tests

#### Configuration Errors
```
KeyError: 'gcp_service_account'
```
**Solution:** Configure Streamlit secrets or use mock configuration

#### Google Sheets Errors
```
Authentication failed
```
**Solution:** Check service account credentials and permissions

## 🎯 Testing Checklist

### Before Running Tests
- [ ] All module files exist in `modules/` directory
- [ ] Python environment is activated
- [ ] Basic dependencies installed (for Level 2+)

### Level 1 Test Results
- [ ] Module Structure: ✅ PASS
- [ ] Config Imports: ✅ PASS
- [ ] Utility Functions: ✅ PASS

### Level 2 Test Results
- [ ] Module Imports: ✅ PASS
- [ ] Configuration: ✅ PASS
- [ ] Utility Functions: ✅ PASS
- [ ] Class Initialization: ✅ PASS

### Level 3 Test Results (Full App)
- [ ] Application loads without errors
- [ ] Authentication works
- [ ] Google Sheets connection established
- [ ] Data upload functionality works
- [ ] Reports generate correctly

## 🐛 Troubleshooting

### Module Import Errors
```python
# Check if modules directory exists
import os
print(os.listdir('modules'))
```

### Configuration Issues
```python
# Test config import directly
from modules.config import TAB_NAMES
print(TAB_NAMES)
```

### Streamlit Issues
```bash
# Check Streamlit version
streamlit --version

# Clear Streamlit cache
streamlit cache clear
```

### Google Sheets Issues
```python
# Test connection in isolation
from modules.data_manager import DataManager
dm = DataManager()
print(f"Google Sheets connected: {dm.gsheet is not None}")
```

## 📝 Next Steps After Testing

### If All Tests Pass
1. Configure Streamlit secrets for production
2. Set up Google Sheets access
3. Test with real data uploads
4. Deploy to production environment

### If Tests Fail
1. Check error messages for specific issues
2. Verify module structure and imports
3. Install missing dependencies
4. Configure required secrets
5. Re-run tests

## 🔄 Continuous Testing

### Automated Testing (Future)
- Unit tests for individual modules
- Integration tests for module interactions
- End-to-end tests for complete workflows

### Manual Testing Checklist
- [ ] Run basic structure test
- [ ] Test Streamlit interface
- [ ] Verify data upload functionality
- [ ] Check report generation
- [ ] Test authentication flow

This testing approach allows you to verify the modular structure at different levels, from basic functionality to full application testing.
