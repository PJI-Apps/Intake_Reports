# modules/batch_manager.py
# Batch management module for handling data batches and metadata

import streamlit as st
import pandas as pd
import time
import random
from datetime import date, datetime
from typing import Optional

class BatchManager:
    """Manages batch operations and metadata for data uploads"""
    
    def __init__(self):
        # Initialize batch management
        if "current_batch_id" not in st.session_state:
            st.session_state["current_batch_id"] = self.generate_batch_id()
        
        if "upload_history" not in st.session_state:
            st.session_state["upload_history"] = {}
    
    def generate_batch_id(self) -> str:
        """Generate a unique batch ID with timestamp and random component"""
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"batch_{timestamp}_{random_suffix}"
    
    def add_batch_metadata(self, df: pd.DataFrame, batch_id: str, upload_date: date, 
                          start_date: date, end_date: date) -> pd.DataFrame:
        """Add batch metadata to dataframe"""
        df = df.copy()
        df["__batch_id"] = batch_id
        df["__upload_date"] = upload_date
        df["__batch_start"] = start_date
        df["__batch_end"] = end_date
        df["__upload_timestamp"] = datetime.now().isoformat()
        return df
    
    def create_empty_sheet_with_headers(self, sheet_name: str) -> pd.DataFrame:
        """Create an empty DataFrame with proper headers for each sheet type"""
        if sheet_name == "CALLS":
            headers = [
                "Name", "Total Calls", "Completed Calls", "Outgoing", "Received", 
                "Forwarded to Voicemail", "Answered by Other", "Missed", 
                "Avg Call Time", "Total Call Time", "Total Hold Time", "Month-Year",
                "__batch_id", "__upload_date", "__batch_start", "__batch_end", "__upload_timestamp"
            ]
        elif sheet_name == "LEADS":
            headers = [
                "First Name", "Last Name", "Email", "Stage", "Assigned Intake Specialist", 
                "Status", "Sub Status", "Matter ID", "Reason for Rescheduling", 
                "No Follow Up (Reason)", "Refer Out?", "Lead Attorney", 
                "Initial Consultation With Pji Law", "Initial Consultation Rescheduled With Pji Law", 
                "Discovery Meeting Rescheduled With Pji Law", "Discovery Meeting With Pji Law", 
                "Practice Area",
                "__batch_id", "__upload_date", "__batch_start", "__batch_end", "__upload_timestamp"
            ]
        elif sheet_name == "INIT":
            headers = [
                "First Name", "Last Name", "Email", "Matter ID", "Assigned Intake Specialist", 
                "Sub Status", "Reason for Rescheduling", "Initial Consultation With Pji Law", 
                "Initial Consultation Rescheduled With Pji Law", "Practice Area", "Lead Attorney", 
                "Status", "Reason", "Initial Consultation With Pji Law",
                "__batch_id", "__upload_date", "__batch_start", "__batch_end", "__upload_timestamp"
            ]
        elif sheet_name == "DISC":
            headers = [
                "First Name", "Last Name", "Email", "Matter ID", "Assigned Intake Specialist", 
                "Sub Status", "Reason for Rescheduling", "Discovery Meeting With Pji Law", 
                "Discovery Meeting Rescheduled With Pji Law", "Practice Area", "Lead Attorney", 
                "Status", "Reason", "Discovery Meeting With Pji Law",
                "__batch_id", "__upload_date", "__batch_start", "__batch_end", "__upload_timestamp"
            ]
        elif sheet_name == "NCL":
            headers = [
                "First Name", "Last Name", "Email", "Matter ID", "Practice Area", 
                "Initial Consultation With Pji Law", "Date we had BOTH the signed CLA and full payment", 
                "Lead Attorney", "Primary Intake?",
                "__batch_id", "__upload_date", "__batch_start", "__batch_end", "__upload_timestamp"
            ]
        else:
            return pd.DataFrame()
        
        return pd.DataFrame(columns=headers)
    
    def master_reset(self, data_manager) -> bool:
        """Complete master reset - removes all data from all sheets but preserves headers"""
        try:
            for sheet_name in ["CALLS", "LEADS", "INIT", "DISC", "NCL"]:
                empty_df = self.create_empty_sheet_with_headers(sheet_name)
                data_manager.write_worksheet_by_name(sheet_name, empty_df)
            
            # Clear file uploader session state to reset the displayed file names
            file_uploader_keys = [
                "zoom_calls_uploader", "up_leads_pncs", "up_initial", 
                "up_discovery", "up_ncl"
            ]
            for key in file_uploader_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("Master reset completed - all data cleared from all sheets (headers preserved)")
            return True
        except Exception as e:
            st.error(f"Master reset failed: {str(e)}")
            return False
    
    def assign_batch_to_orphaned_records(self, sheet_name: str, batch_id: str, data_manager) -> bool:
        """Assign batch ID to records that don't have one"""
        try:
            current_data = data_manager.read_worksheet_by_name(sheet_name)
            if current_data is None or current_data.empty:
                st.warning(f"No data found in {sheet_name}")
                return True
            
            # Check if __batch_id column exists
            if "__batch_id" not in current_data.columns:
                current_data["__batch_id"] = ""
            
            # Find records without batch ID (handle both string and datetime formats)
            batch_col = current_data["__batch_id"]
            batch_col_str = batch_col.astype(str)
            orphaned_mask = (batch_col.isna() | (batch_col_str == "") | 
                            (batch_col_str == "NaT") | (batch_col_str.str.contains("0:00:00")))
            orphaned_count = orphaned_mask.sum()
            
            if orphaned_count == 0:
                st.info(f"No orphaned records found in {sheet_name}")
                return True
            
            # Assign batch ID to orphaned records
            current_data.loc[orphaned_mask, "__batch_id"] = batch_id
            
            # Write back the updated data
            data_manager.write_worksheet_by_name(sheet_name, current_data)
            
            st.success(f"Assigned batch ID '{batch_id}' to {orphaned_count} orphaned records in {sheet_name}")
            return True
        except Exception as e:
            st.error(f"Failed to assign batch to orphaned records in {sheet_name}: {str(e)}")
            return False
    
    def render_batch_management_ui(self):
        """Render the batch management UI"""
        st.markdown("### 📦 Batch Management")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Generate New Batch ID", use_container_width=True):
                st.session_state["current_batch_id"] = self.generate_batch_id()
                st.success(f"New batch ID: {st.session_state['current_batch_id']}")
        
        with col2:
            if st.button("🔄 Allow Re-upload", use_container_width=True):
                st.session_state.get("hashes_calls", set()).clear()
                st.session_state.get("hashes_conv", set()).clear()
                st.success("Re-upload enabled - you can now upload the same files")
        
        with col3:
            if st.button("🔄 Sync All Sheets", use_container_width=True):
                # This would need data_manager passed in
                st.success("Sync functionality would be implemented here")
        
        # Display current batch ID
        st.info(f"**Current Batch ID:** {st.session_state['current_batch_id']}")
        st.divider()
