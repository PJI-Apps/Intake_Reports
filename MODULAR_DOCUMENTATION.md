# PJI Law Reports - Modular System Documentation

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Module Documentation](#module-documentation)
   - [Config Module](#config-module)
   - [Utils Module](#utils-module)
   - [Auth Module](#auth-module)
   - [Data Manager Module](#data-manager-module)
   - [Batch Manager Module](#batch-manager-module)
   - [UI Manager Module](#ui-manager-module)
   - [Visualizations Module](#visualizations-module)
4. [Main Application](#main-application)
5. [Deployment Guide](#deployment-guide)
6. [Testing Guide](#testing-guide)
7. [Troubleshooting](#troubleshooting)
8. [Security](#security)

---

## 🏗️ System Overview

The PJI Law Reports application has been refactored from a monolithic structure into a modular, maintainable system. This documentation covers every aspect of the modular architecture.

### **Key Benefits:**
- **Maintainability**: Each module has a single responsibility
- **Testability**: Individual modules can be tested in isolation
- **Scalability**: Easy to add new features or modify existing ones
- **Debugging**: Issues can be isolated to specific modules
- **Code Reuse**: Modules can be reused across different parts of the application

### **System Flow:**
```
User Input → Auth Module → UI Manager → Data Manager → Batch Manager → Visualizations → Output
```

---

## 🏛️ Architecture

### **Module Structure:**
```
modules/
├── __init__.py          # Makes modules a Python package
├── config.py           # Configuration constants and mappings
├── utils.py            # Common utility functions
├── auth.py             # Authentication and user management
├── data_manager.py     # Google Sheets operations and data processing
├── batch_manager.py    # Batch operations and metadata management
├── ui_manager.py       # User interface components and rendering
└── visualizations.py   # Chart generation and plotting
```

### **Dependencies:**
- **Core**: `streamlit`, `pandas`, `datetime`
- **External**: `gspread`, `plotly`, `streamlit_authenticator`, `yaml`
- **Internal**: All modules depend on `config.py` and `utils.py`

---

## 📚 Module Documentation

### **Config Module** (`modules/config.py`)

**Purpose**: Centralized configuration management for all constants, mappings, and settings.

**Key Components:**

#### **Tab Configuration:**
```python
TAB_NAMES = {
    "calls": "📞 Calls Report",
    "conversion": "📊 Conversion Report", 
    "practice_area": "⚖️ Practice Area Report",
    "intake": "👥 Intake Report",
    "debug": "🔧 Debug"
}
```

#### **Data Processing Mappings:**
```python
REQUIRED_COLUMNS_CALLS = ["Name", "Total Calls", "Completed Calls", "Month-Year"]
ALLOWED_CALLS = ["Staff", "Attorney", "Admin"]
CATEGORY_CALLS = ["Staff", "Attorney", "Admin"]
```

#### **Practice Areas:**
```python
PRACTICE_AREAS = [
    "ALL", "Personal Injury", "Medical Malpractice", 
    "Workers Compensation", "Social Security Disability"
]
```

#### **Month Mappings:**
```python
MONTHS_MAP = {
    1: "January", 2: "February", 3: "March", ...
}
```

**Usage Examples:**
```python
from modules.config import TAB_NAMES, PRACTICE_AREAS

# Get tab display name
tab_name = TAB_NAMES["calls"]  # Returns "📞 Calls Report"

# Check if practice area is valid
is_valid = practice_area in PRACTICE_AREAS
```

**What to Expect:**
- All configuration is centralized here
- Easy to modify settings without touching other modules
- Consistent naming across the application

---

### **Utils Module** (`modules/utils.py`)

**Purpose**: Common utility functions used across multiple modules.

**Key Functions:**

#### **Data Processing:**
```python
def calculate_percentage(numerator: float, denominator: float) -> float:
    """Calculate percentage with safe division"""
    
def normalize_string(s: str) -> str:
    """Normalize string for consistent comparison"""
    
def html_escape(s: str) -> str:
    """Escape HTML characters for safe display"""
```

#### **Date Handling:**
```python
def month_key_from_range(start: date, end: date) -> str:
    """Generate month key from date range (e.g., '2024-01')"""
    
def validate_single_month_range(start: date, end: date) -> Tuple[bool, str]:
    """Validate if date range falls within a single calendar month"""
```

**Usage Examples:**
```python
from modules.utils import calculate_percentage, month_key_from_range

# Calculate completion rate
rate = calculate_percentage(8, 10)  # Returns 80.0

# Generate month key
key = month_key_from_range(date(2024, 1, 1), date(2024, 1, 31))  # Returns "2024-01"
```

**What to Expect:**
- Reusable functions across the application
- Consistent data processing logic
- Safe handling of edge cases (division by zero, invalid dates)

---

### **Auth Module** (`modules/auth.py`)

**Purpose**: Handle user authentication and session management.

**Key Functions:**

#### **Authentication Setup:**
```python
def setup_authentication():
    """Initialize authentication from Streamlit secrets"""
    
def check_auth_status(authenticator):
    """Check if user is authenticated and handle login/logout"""
```

**Configuration (in Streamlit secrets):**
```toml
[auth_config]
config = """
credentials:
  usernames:
    your_username:
      email: your_email@example.com
      name: Your Name
      password: $2b$12$hashed_password_here
cookie:
  name: pji_law_auth
  key: your_secret_key
  expiry_days: 30
"""
```

**What to Expect:**
- Login form appears if user is not authenticated
- Sidebar shows logout button and user name when authenticated
- App stops execution if authentication fails
- Session management with cookies

**Common Issues:**
- Missing or incorrect secrets configuration
- Password hashing issues
- Cookie configuration problems

---

### **Data Manager Module** (`modules/data_manager.py`)

**Purpose**: Handle all Google Sheets operations and data processing logic.

**Key Components:**

#### **Google Sheets Connection:**
```python
def _gsheet_client_cached(self):
    """Get cached Google Sheets client"""
    
def _get_worksheet(self, sheet_name: str):
    """Get specific worksheet by name"""
    
def read_worksheet_by_name(self, sheet_name: str) -> pd.DataFrame:
    """Read data from specific worksheet"""
    
def write_worksheet_by_name(self, sheet_name: str, df: pd.DataFrame):
    """Write data to specific worksheet"""
```

#### **Data Processing:**
```python
def process_calls_csv(self, raw: pd.DataFrame, period_key: str) -> pd.DataFrame:
    """Process raw calls CSV data with normalization and aggregation"""
    
def validate_single_month_range(self, start: date, end: date) -> Tuple[bool, str]:
    """Validate date range for data processing"""
    
def file_md5(self, uploaded_file) -> str:
    """Generate MD5 hash for file deduplication"""
```

#### **Data Loading:**
```python
def load_all_data(self):
    """Load all data from Google Sheets into memory"""
    
def sync_from_master_sheet(self):
    """Sync data from master sheet to individual sheets"""
```

**Configuration (in Streamlit secrets):**
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
# ... other GCP credentials

[google_sheets]
spreadsheet_id = "your-spreadsheet-id"
```

**What to Expect:**
- Automatic connection to Google Sheets
- Data caching for performance
- Error handling for connection issues
- Data validation and processing
- File deduplication based on MD5 hashes

**Common Issues:**
- Missing or incorrect GCP credentials
- Google Sheets API not enabled
- Permission issues with spreadsheet
- Network connectivity problems

---

### **Batch Manager Module** (`modules/batch_manager.py`)

**Purpose**: Manage batch operations and metadata for data uploads.

**Key Functions:**

#### **Batch Operations:**
```python
def generate_batch_id(self) -> str:
    """Generate unique batch ID with timestamp and random component"""
    
def add_batch_metadata(self, df: pd.DataFrame, batch_id: str, 
                      upload_date: date, start_date: date, end_date: date) -> pd.DataFrame:
    """Add batch metadata columns to dataframe"""
```

#### **Sheet Management:**
```python
def create_empty_sheet_with_headers(self, sheet_name: str) -> pd.DataFrame:
    """Create empty DataFrame with proper headers for each sheet type"""
    
def master_reset(self, data_manager) -> bool:
    """Complete master reset - removes all data but preserves headers"""
```

#### **Batch Tracking:**
```python
def get_available_batches(self, data_manager) -> List[str]:
    """Get list of available batch IDs from data"""
    
def remove_batch_from_sheet(self, sheet_name: str, batch_id: str, data_manager) -> bool:
    """Remove specific batch from sheet"""
```

**What to Expect:**
- Unique batch IDs for each upload
- Metadata tracking (upload date, date range, timestamp)
- Batch history management
- Data cleanup and reset capabilities

**Common Issues:**
- Batch ID conflicts (very rare due to timestamp + random)
- Metadata column conflicts
- Sheet header mismatches

---

### **UI Manager Module** (`modules/ui_manager.py`)

**Purpose**: Handle all user interface components and report rendering.

**Key Components:**

#### **Admin Interface:**
```python
def render_admin_sidebar(self, data_manager, batch_manager):
    """Render admin controls in sidebar"""
    
def render_upload_section(self, data_manager, batch_manager):
    """Render file upload interface"""
```

#### **Report Rendering:**
```python
def render_calls_report(self, data_manager, viz_manager):
    """Render calls report with filtering and display"""
    
def render_conversion_report(self, data_manager, viz_manager):
    """Render conversion report with practice area filtering"""
    
def render_practice_area_report(self, data_manager, viz_manager):
    """Render practice area specific report"""
    
def render_intake_report(self, data_manager, viz_manager):
    """Render intake specialist report"""
```

#### **Data Filtering:**
```python
def _filter_calls_data(self, df: pd.DataFrame, year: str, month: str, 
                      category: str, name: str) -> pd.DataFrame:
    """Filter calls data based on user selections"""
    
def _filter_conversion_data(self, df: pd.DataFrame, start_date: date, 
                           end_date: date, practice_area: str) -> pd.DataFrame:
    """Filter conversion data based on date range and practice area"""
```

#### **Helper Functions:**
```python
def _html_escape(self, s: str) -> str:
    """Escape HTML characters for safe display"""
    
def _to_ts(self, series: pd.Series) -> pd.Series:
    """Convert series to timestamp format"""
    
def _find_col(self, df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """Find column in dataframe from list of candidates"""
```

**What to Expect:**
- Clean, responsive user interface
- Interactive filtering and selection
- Safe HTML rendering
- Error handling for missing data
- Consistent styling across reports

**Common Issues:**
- Missing data columns
- Date parsing errors
- Filter logic issues
- UI responsiveness problems

---

### **Visualizations Module** (`modules/visualizations.py`)

**Purpose**: Generate charts and visualizations using Plotly.

**Key Components:**

#### **Chart Generation:**
```python
def render_calls_visualizations(self, df_calls: pd.DataFrame, filtered_calls: pd.DataFrame):
    """Render calls report visualizations"""
    
def render_conversion_trends(self, start_date: date, end_date: date, practice_area: str = "ALL"):
    """Render conversion trend visualizations"""
    
def render_conversion_trend_visualizations(self, viz_period_mode: str, viz_year: int, 
                                         viz_month: int, viz_quarter: str, viz_practice_area: str):
    """Render advanced conversion trend visualizations"""
```

#### **Chart Types:**
- **Call Volume Trends**: Line charts showing call volume over time
- **Completion Rates**: Bar charts showing staff performance
- **Call Duration**: Horizontal bar charts showing average call times
- **Conversion Trends**: Line charts showing retention and scheduling rates
- **Practice Area Comparisons**: Bar charts comparing practice areas
- **Intake Specialist Performance**: Performance metrics by specialist

#### **Data Generation:**
```python
def _generate_viz_data(self, viz_period_mode: str, viz_year: int, 
                      viz_month: int, viz_quarter: str) -> tuple:
    """Generate visualization data based on period mode"""
    
def _get_viz_date_range(self, viz_period_mode: str, viz_year: int, 
                       viz_month: int, viz_quarter: str) -> tuple:
    """Get date range for visualization based on period mode"""
```

**Dependencies:**
```python
# Required in requirements.txt
plotly>=5.22
```

**What to Expect:**
- Interactive charts with hover information
- Responsive design that adapts to screen size
- Graceful degradation when Plotly is not available
- Consistent styling across all visualizations

**Common Issues:**
- Plotly not installed
- Missing data for charts
- Chart rendering errors
- Performance issues with large datasets

---

## 🚀 Main Application (`app_modular.py`)

**Purpose**: Main entry point that orchestrates all modules.

**Key Components:**

#### **Application Flow:**
```python
def main():
    """Main application entry point"""
    
    # 1. Setup page configuration
    setup_page_config()
    
    # 2. Setup authentication
    authenticator = setup_authentication()
    name, auth_status, username = check_auth_status(authenticator)
    
    # 3. Initialize managers
    data_manager = DataManager()
    ui_manager = UIManager()
    batch_manager = BatchManager()
    viz_manager = VisualizationManager()
    
    # 4. Load data
    data_manager.load_all_data()
    
    # 5. Render interface
    ui_manager.render_main_interface(data_manager, batch_manager, viz_manager)
```

#### **Page Configuration:**
```python
def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="PJI Law - Conversion & Call Reports",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
```

**What to Expect:**
- Clean application startup
- Proper error handling
- Consistent user experience
- Modular architecture benefits

**Common Issues:**
- Module import errors
- Authentication configuration problems
- Data loading failures
- Memory issues with large datasets

---

## 🚀 Deployment Guide

### **Prerequisites:**
1. **GitHub Repository**: Public repository (required by Streamlit)
2. **Streamlit Account**: Free account at streamlit.io
3. **Google Cloud Project**: For Google Sheets API access

### **Step 1: Prepare Your Repository**
```bash
# Ensure all files are committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

### **Step 2: Configure Streamlit Secrets**
In your Streamlit Cloud dashboard:

1. **Authentication Configuration:**
```toml
[auth_config]
config = """
credentials:
  usernames:
    your_username:
      email: your_email@example.com
      name: Your Name
      password: $2b$12$hashed_password_here
cookie:
  name: pji_law_auth
  key: your_secret_key
  expiry_days: 30
"""
```

2. **Google Cloud Configuration:**
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

3. **Google Sheets Configuration:**
```toml
[google_sheets]
spreadsheet_id = "your-spreadsheet-id"
```

### **Step 3: Deploy to Streamlit**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set the main file path to `app_modular.py`
4. Deploy

### **Step 4: Verify Deployment**
1. Test authentication
2. Test data loading
3. Test file uploads
4. Test all reports and visualizations

---

## 🧪 Testing Guide

### **Available Test Scripts:**

1. **`test_modular_simple.py`**: Basic module structure and imports
2. **`test_integration_simple.py`**: Comprehensive integration testing
3. **`test_app_integration.py`**: Complete app integration testing

### **Running Tests:**
```bash
# Basic structure test
python test_modular_simple.py

# Integration test
python test_integration_simple.py

# App integration test
python test_app_integration.py
```

### **Test Results Interpretation:**
- **✅ PASS**: Module/function working correctly
- **❌ FAIL**: Issue that needs attention
- **⚠️ SKIP**: Expected failure due to missing dependencies

### **What Tests Cover:**
- Module imports and structure
- Function functionality
- Data processing logic
- UI components
- Error handling
- Performance characteristics

---

## 🔧 Troubleshooting

### **Common Issues and Solutions:**

#### **1. Authentication Issues**
**Symptoms:**
- Login form not appearing
- Authentication always fails
- Session not persisting

**Solutions:**
- Check Streamlit secrets configuration
- Verify password hashing
- Check cookie configuration
- Clear browser cache

#### **2. Google Sheets Connection Issues**
**Symptoms:**
- "No module named 'gspread'" error
- Connection timeout
- Permission denied errors

**Solutions:**
- Install gspread: `pip install gspread`
- Check GCP service account credentials
- Verify Google Sheets API is enabled
- Check spreadsheet permissions

#### **3. Data Processing Issues**
**Symptoms:**
- Missing columns error
- Date parsing errors
- Filter not working

**Solutions:**
- Check data format in Google Sheets
- Verify column names match expected format
- Check date format consistency
- Review filter logic in UI manager

#### **4. Visualization Issues**
**Symptoms:**
- Charts not displaying
- "Charts unavailable" message
- Performance issues

**Solutions:**
- Install plotly: `pip install plotly>=5.22`
- Check data availability for charts
- Reduce dataset size for performance
- Verify chart configuration

#### **5. Module Import Issues**
**Symptoms:**
- ImportError for modules
- Missing dependencies
- Circular import errors

**Solutions:**
- Check module file structure
- Verify `__init__.py` files exist
- Check import statements
- Review dependency installation

### **Debugging Steps:**

1. **Check Logs**: Look for error messages in Streamlit
2. **Test Individual Modules**: Run specific module tests
3. **Verify Configuration**: Check all secrets and settings
4. **Test Data**: Ensure sample data works correctly
5. **Check Dependencies**: Verify all required packages are installed

### **Getting Help:**

When requesting debugging assistance, provide:
1. **Error Message**: Exact error text
2. **Module Affected**: Which module is causing issues
3. **Steps to Reproduce**: How to trigger the error
4. **Environment**: Local vs deployed, Python version
5. **Test Results**: Output from test scripts

---

## 🔒 Security

### **Security Measures:**

1. **Authentication**: User login required
2. **Secrets Management**: Sensitive data in Streamlit secrets
3. **Input Validation**: All user inputs validated
4. **Data Sanitization**: HTML escaping for safe display
5. **Access Control**: Authentication-based access

### **What's Protected:**
- Google Sheets credentials
- User passwords
- API keys
- Real data files
- Service account information

### **What's Safe to Share:**
- Application code
- Module structure
- Configuration constants
- Test data
- Documentation

### **Security Checklist:**
- [ ] `.gitignore` configured correctly
- [ ] Streamlit secrets set up
- [ ] Authentication working
- [ ] No sensitive data in code
- [ ] Input validation implemented
- [ ] Error messages don't expose sensitive info

---

## 📈 Performance Considerations

### **Optimization Tips:**

1. **Data Caching**: Use Streamlit caching for expensive operations
2. **Batch Processing**: Process data in chunks for large datasets
3. **Lazy Loading**: Load data only when needed
4. **Chart Optimization**: Limit chart data points for better performance

### **Memory Management:**
- Clear unused data from memory
- Use efficient data structures
- Monitor memory usage in Streamlit

### **Network Optimization:**
- Cache Google Sheets API calls
- Use efficient data transfer formats
- Implement retry logic for network issues

---

## 🔄 Maintenance

### **Regular Tasks:**

1. **Update Dependencies**: Keep packages up to date
2. **Monitor Performance**: Check for performance degradation
3. **Review Logs**: Look for errors or issues
4. **Test Functionality**: Run tests regularly
5. **Backup Data**: Ensure data is backed up

### **Adding New Features:**

1. **Create New Module**: If functionality is substantial
2. **Extend Existing Module**: For related functionality
3. **Update Configuration**: Add new constants to config
4. **Add Tests**: Create tests for new functionality
5. **Update Documentation**: Keep docs current

---

## 📞 Support

### **When You Need Help:**

1. **Check This Documentation**: Most issues are covered here
2. **Run Test Scripts**: Identify specific problems
3. **Check Streamlit Logs**: Look for error messages
4. **Review Module Code**: Understand the specific module
5. **Search Online**: Many issues have known solutions

### **Providing Debug Information:**

When asking for help, include:
- **Error Message**: Exact text
- **Module**: Which module is affected
- **Test Results**: Output from test scripts
- **Environment**: Local/deployed, Python version
- **Steps**: How to reproduce the issue

---

## 🎯 Conclusion

This modular system provides a robust, maintainable, and scalable foundation for the PJI Law Reports application. The documentation above should help you understand, deploy, and maintain the system effectively.

**Key Takeaways:**
- Each module has a single, clear responsibility
- The system is well-tested and documented
- Security measures are comprehensive
- Performance considerations are built-in
- The architecture supports future enhancements

**Next Steps:**
1. Review this documentation thoroughly
2. Test the system locally
3. Deploy to Streamlit
4. Monitor and maintain as needed

Good luck with your deployment! 🚀
