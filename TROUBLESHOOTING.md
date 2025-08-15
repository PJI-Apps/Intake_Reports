# 🔧 Troubleshooting Guide

## 🚨 Common Errors and Solutions

### **Error: KeyError - logs not in session state**

**Problem**: The app crashes with a KeyError about missing 'logs' in session state.

**Solution**: ✅ **FIXED** - This has been resolved in the latest version of `data_manager.py`.

**If you still see this error**:
1. Make sure you're using the latest version from the deployment package
2. Clear your browser cache and refresh
3. Restart your Streamlit app

### **Error: Google Sheets not configured**

**Problem**: App shows "Google Sheets not configured" message.

**Solution**:
1. **Check your TOML secrets configuration**:
   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   # ... other service account fields
   
   [google_sheets]
   spreadsheet_id = "your-spreadsheet-id"
   ```

2. **Verify your Google Cloud setup**:
   - Service account JSON is complete
   - Google Sheets API is enabled
   - Spreadsheet is shared with service account email

3. **Check spreadsheet ID**:
   - Extract from URL: `https://docs.google.com/spreadsheets/d/YOUR_ID_HERE/edit`
   - Make sure it's correct and the sheet exists

### **Error: Authentication failed**

**Problem**: Users can't log in.

**Solution**:
1. **Check password hashing**:
   - Use `generate_password.py` to create hashed passwords
   - Make sure passwords in TOML are hashed, not plain text

2. **Verify TOML structure**:
   ```toml
   [auth_config]
   config = """
   credentials:
     usernames:
       admin:
         email: admin@pji-law.com
         name: Admin Name
         password: $2b$12$hashed_password_here
   cookie:
     name: pji_law_auth
     key: your_secret_key
     expiry_days: 30
   """
   ```

### **Error: Module not found**

**Problem**: Import errors for modules (ModuleNotFoundError).

**Solution**: ✅ **FIXED** - This has been resolved in the latest version of `app_modular.py`.

**If you still see this error**:
1. **Use the alternative app file**: Try `app_modular_alternative.py` instead
2. **Run the diagnostic script**: Use `python debug_imports.py` to check your setup
3. **Check file structure**:
   ```
   your-repo/
   ├── app_modular.py
   ├── modules/
   │   ├── __init__.py
   │   ├── config.py
   │   ├── auth.py
   │   └── ...
   ```

4. **Verify all files are uploaded** to GitHub
5. **Clear browser cache** and restart your Streamlit app

### **Error: Dependencies not found**

**Problem**: Missing Python packages.

**Solution**:
1. **Check requirements.txt** is in your repo
2. **Verify Python version** is 3.11 in Streamlit
3. **Check Streamlit logs** for specific missing packages

## 🔍 Debugging Steps

### **1. Check Streamlit Logs**

1. Go to your Streamlit app
2. Click "Manage app" in bottom right
3. Go to "Logs" tab
4. Look for error messages

### **2. Test Locally First**

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app_modular.py
```

### **3. Verify Secrets Configuration**

Create a test script to check your secrets:

```python
import streamlit as st

# Check if secrets are loaded
if "gcp_service_account" in st.secrets:
    print("✅ Service account configured")
else:
    print("❌ Service account missing")

if "google_sheets" in st.secrets:
    print("✅ Google Sheets configured")
else:
    print("❌ Google Sheets missing")

if "auth_config" in st.secrets:
    print("✅ Auth configured")
else:
    print("❌ Auth missing")
```

## 🛠️ Quick Fixes

### **Reset Session State**

If you're having session state issues:

```python
# Add this to your app temporarily
if st.button("Reset Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

### **Test Google Sheets Connection**

Add this to debug Google Sheets:

```python
# Test connection
try:
    data_manager = DataManager()
    if data_manager.gsheet:
        st.success("✅ Google Sheets connected!")
    else:
        st.error("❌ Google Sheets not connected")
except Exception as e:
    st.error(f"❌ Error: {e}")
```

## 📞 Getting Help

### **Before Asking for Help**

1. **Check this troubleshooting guide**
2. **Review the logs** in Streamlit Cloud
3. **Test locally** if possible
4. **Verify your TOML configuration**

### **When Reporting Issues**

Include:
- **Error message** (full traceback)
- **Your TOML configuration** (with sensitive data removed)
- **Steps to reproduce**
- **What you've already tried**

### **Common Solutions**

| Problem | Solution |
|---------|----------|
| Session state errors | Clear browser cache, restart app |
| Google Sheets errors | Check service account and sharing |
| Authentication errors | Verify password hashing |
| Import errors | Check file structure and uploads |
| Dependency errors | Verify requirements.txt and Python version |

## ✅ Success Checklist

Before deploying, ensure:
- [ ] All files uploaded to GitHub
- [ ] TOML secrets configured correctly
- [ ] Google Sheets created and shared
- [ ] Service account JSON complete
- [ ] Passwords properly hashed
- [ ] Python version set to 3.11
- [ ] App runs locally without errors

**Most issues can be resolved by following this guide!** 🔧
