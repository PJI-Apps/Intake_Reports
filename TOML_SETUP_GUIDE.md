# 🔐 TOML Secrets Setup Guide

## 📋 What You Need to Configure

Your Streamlit app requires three main configuration sections:

1. **Authentication** (`[auth_config]`) - User login credentials
2. **Google Cloud Service Account** (`[gcp_service_account]`) - Google Sheets access
3. **Google Sheets** (`[google_sheets]`) - Your spreadsheet ID

## 🎯 Step-by-Step Setup

### **Step 1: Generate Secure Passwords**

1. **Install bcrypt** (if not already installed):
   ```bash
   pip install bcrypt
   ```

2. **Run the password generator**:
   ```bash
   python generate_password.py
   ```

3. **Enter your desired passwords** when prompted
4. **Copy the hashed passwords** that are generated

### **Step 2: Get Google Cloud Service Account**

1. **Go to Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Create a new project** or select existing one
3. **Enable Google Sheets API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create
5. **Generate JSON Key**:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose JSON format
   - Download the JSON file

### **Step 3: Get Google Sheets ID**

1. **Open your Google Sheet**
2. **Copy the URL** from your browser
3. **Extract the ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID_HERE/edit
   ```

### **Step 4: Configure TOML File**

Use the `secrets_template.toml` file as your starting point:

#### **Authentication Section**
```toml
[auth_config]
config = """
credentials:
  usernames:
    admin:
      email: admin@pji-law.com
      name: PJI Law Admin
      password: $2b$12$hashed_password_from_generator
    user1:
      email: user1@pji-law.com
      name: User One
      password: $2b$12$another_hashed_password
cookie:
  name: pji_law_auth
  key: your_super_secret_cookie_key_here
  expiry_days: 30
"""
```

#### **Google Cloud Service Account Section**
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id-from-json"
private_key_id = "your-private-key-id-from-json"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id-from-json"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

#### **Google Sheets Section**
```toml
[google_sheets]
spreadsheet_id = "your-spreadsheet-id-from-url"
```

### **Step 5: Add to Streamlit Secrets**

1. **Go to Streamlit Cloud**: [share.streamlit.io](https://share.streamlit.io)
2. **Select your app**
3. **Go to Settings** > **Secrets**
4. **Paste your complete TOML configuration**
5. **Save**

## 🔑 Key Values to Replace

### **Authentication**
- `admin@pji-law.com` → Your admin email
- `PJI Law Admin` → Your admin name
- `$2b$12$hashed_password_from_generator` → Hashed password from generator
- `your_super_secret_cookie_key_here` → Random secret string (32+ characters)

### **Google Cloud**
- `your-project-id-from-json` → From your JSON service account file
- `your-private-key-id-from-json` → From your JSON service account file
- `your-private-key-from-json` → The entire private key from JSON (with \n for line breaks)
- `your-service-account@your-project.iam.gserviceaccount.com` → From your JSON service account file
- `your-client-id-from-json` → From your JSON service account file

### **Google Sheets**
- `your-spreadsheet-id-from-url` → The ID from your Google Sheets URL

## 🔒 Security Checklist

Before deploying:
- [ ] All passwords are hashed (not plain text)
- [ ] Cookie key is a random secret string
- [ ] Service account JSON is complete and accurate
- [ ] Spreadsheet ID is correct
- [ ] No sensitive data in the TOML file
- [ ] TOML file is not committed to Git

## 🧪 Testing Your Configuration

1. **Test locally first**:
   ```bash
   streamlit run app_modular.py
   ```

2. **Test authentication**:
   - Try logging in with your credentials
   - Verify session persistence

3. **Test Google Sheets connection**:
   - Check if data loads correctly
   - Verify upload functionality

## 📞 Troubleshooting

### **Common Issues**

1. **"Invalid credentials" error**:
   - Check password hashing
   - Verify username spelling

2. **"Google Sheets access denied"**:
   - Verify service account JSON
   - Check spreadsheet sharing permissions
   - Ensure Google Sheets API is enabled

3. **"Spreadsheet not found"**:
   - Verify spreadsheet ID
   - Check if spreadsheet is shared with service account email

### **Getting Help**

If you encounter issues:
1. Check Streamlit logs for error messages
2. Verify all TOML values are correct
3. Test each section individually
4. Review the comprehensive documentation

## ✅ Success!

Once configured correctly, your app will have:
- ✅ Secure user authentication
- ✅ Google Sheets integration
- ✅ Protected sensitive data
- ✅ Ready for production deployment

**Your TOML configuration is now complete and secure!** 🔐
