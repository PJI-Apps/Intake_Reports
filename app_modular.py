# app_modular.py
# PJI Law - Conversion and Call Report (Streamlit) - Modular Version

import streamlit as st
import sys
import os
from datetime import date

# Add the current directory to Python path to ensure modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import our modular components with error handling
try:
    from modules.auth import setup_authentication, check_auth_status
    from modules.config import setup_page_config
    from modules.data_manager import DataManager
    from modules.ui_manager import UIManager
    from modules.batch_manager import BatchManager
    from modules.visualizations import VisualizationManager
except ImportError as e:
    st.error(f"Failed to import modules: {e}")
    st.error("Please ensure all module files are present in the modules/ directory")
    st.stop()

def main():
    """Main application entry point"""
    
    # Setup page configuration
    setup_page_config()
    
    # Setup authentication
    authenticator = setup_authentication()
    name, auth_status, username = check_auth_status(authenticator)
    
    # Initialize managers
    data_manager = DataManager()
    ui_manager = UIManager()
    batch_manager = BatchManager()
    viz_manager = VisualizationManager()
    
    # Main application title
    st.title("📊 Conversion and Call Report")
    
    # Render admin sidebar
    ui_manager.render_admin_sidebar(data_manager)
    
    # Main application sections
    with st.expander("🧾 Data Upload & Management", expanded=st.session_state.get("exp_upload_open", False)):
        batch_manager.render_batch_management_ui()
        ui_manager.render_upload_section(data_manager, batch_manager)
    
    # Load and process data
    data_manager.load_all_data()
    
    # Render main reports
    ui_manager.render_calls_report(data_manager)
    ui_manager.render_conversion_report(data_manager)
    ui_manager.render_practice_area_report(data_manager)
    ui_manager.render_intake_report(data_manager)
    ui_manager.render_visualizations(data_manager, viz_manager)
    
    # Debug section (admin only)
    if auth_status:
        ui_manager.render_debug_section(data_manager)

if __name__ == "__main__":
    main()
