# modules/batch_manager.py
# Batch management module for handling data batches and metadata

import streamlit as st
import pandas as pd
import time
import random
from datetime import date, datetime
from typing import Optional, Dict, List

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
    
    def get_available_batches(self, data_manager) -> Dict[str, Dict[str, int]]:
        """Get all available batches across all sheets with record counts"""
        batches = {}
        
        for sheet_name in ["CALLS", "LEADS", "INIT", "DISC", "NCL"]:
            try:
                df = data_manager.read_worksheet_by_name(sheet_name)
                if df is not None and not df.empty and "__batch_id" in df.columns:
                    # Count records per batch
                    batch_counts = df["__batch_id"].value_counts().to_dict()
                    
                    for batch_id, count in batch_counts.items():
                        if batch_id and str(batch_id).strip() and str(batch_id) != "nan":
                            if batch_id not in batches:
                                batches[batch_id] = {}
                            batches[batch_id][sheet_name] = count
            except Exception as e:
                st.warning(f"Error reading {sheet_name}: {str(e)}")
        
        return batches
    
    def delete_batch(self, batch_id: str, data_manager) -> Dict[str, int]:
        """Delete all records with the specified batch ID from all sheets"""
        deleted_counts = {}
        
        for sheet_name in ["CALLS", "LEADS", "INIT", "DISC", "NCL"]:
            try:
                df = data_manager.read_worksheet_by_name(sheet_name)
                if df is not None and not df.empty and "__batch_id" in df.columns:
                    before_count = len(df)
                    
                    # Filter out records with the specified batch ID
                    df_filtered = df[df["__batch_id"] != batch_id].copy()
                    after_count = len(df_filtered)
                    deleted_count = before_count - after_count
                    
                    if deleted_count > 0:
                        # Write back the filtered data
                        success = data_manager.write_worksheet_by_name(sheet_name, df_filtered)
                        if success:
                            deleted_counts[sheet_name] = deleted_count
                        else:
                            st.error(f"Failed to write filtered data to {sheet_name}")
                    else:
                        deleted_counts[sheet_name] = 0
                else:
                    deleted_counts[sheet_name] = 0
            except Exception as e:
                st.error(f"Error deleting batch from {sheet_name}: {str(e)}")
                deleted_counts[sheet_name] = 0
        
        return deleted_counts
    
    def get_batch_summary(self, batch_id: str, data_manager) -> Dict[str, Dict]:
        """Get detailed summary of a specific batch across all sheets"""
        summary = {}
        
        for sheet_name in ["CALLS", "LEADS", "INIT", "DISC", "NCL"]:
            try:
                df = data_manager.read_worksheet_by_name(sheet_name)
                if df is not None and not df.empty and "__batch_id" in df.columns:
                    batch_data = df[df["__batch_id"] == batch_id]
                    if not batch_data.empty:
                        summary[sheet_name] = {
                            "count": len(batch_data),
                            "upload_date": batch_data["__upload_date"].iloc[0] if "__upload_date" in batch_data.columns else "Unknown",
                            "date_range": f"{batch_data['__batch_start'].iloc[0]} to {batch_data['__batch_end'].iloc[0]}" if "__batch_start" in batch_data.columns and "__batch_end" in batch_data.columns else "Unknown"
                        }
            except Exception as e:
                st.warning(f"Error getting summary for {sheet_name}: {str(e)}")
        
        return summary
    
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
    
    def render_batch_management_ui(self, data_manager):
        """Render the batch management UI with deletion functionality"""
        st.markdown("### 📦 Batch Management")
        
        # Basic batch operations
        col1, col2, col3, col4 = st.columns(4)
        
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
        
        with col4:
            if st.button("🗑️ Wipe All Data", use_container_width=True, type="secondary"):
                # Show confirmation
                st.warning("⚠️ Are you sure you want to wipe ALL data from ALL sheets? This action cannot be undone.")
                
                col_confirm1, col_confirm2 = st.columns(2)
                with col_confirm1:
                    if st.button("✅ Yes, Wipe All Data", type="primary"):
                        success = self.master_reset(data_manager)
                        if success:
                            st.success("✅ All data has been wiped from all sheets. Headers preserved.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to wipe data")
                
                with col_confirm2:
                    if st.button("❌ Cancel"):
                        st.rerun()
        
        # Display current batch ID
        st.info(f"**Current Batch ID:** {st.session_state['current_batch_id']}")
        
        # Batch deletion section
        st.markdown("#### 🗑️ Batch Deletion")
        
        # Get available batches
        batches = self.get_available_batches(data_manager)
        
        if batches:
            # Create a summary of batches
            batch_summary = []
            for batch_id, sheet_counts in batches.items():
                total_records = sum(sheet_counts.values())
                batch_summary.append({
                    "batch_id": batch_id,
                    "total_records": total_records,
                    "sheets": ", ".join([f"{sheet}({count})" for sheet, count in sheet_counts.items()])
                })
            
            # Sort by batch ID (newest first)
            batch_summary.sort(key=lambda x: x["batch_id"], reverse=True)
            
            # Display batch summary
            st.write("**Available Batches:**")
            for batch in batch_summary:
                st.write(f"• **{batch['batch_id']}**: {batch['total_records']} total records across {batch['sheets']}")
            
            # Batch deletion interface
            st.divider()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                batch_options = [""] + [batch["batch_id"] for batch in batch_summary]
                selected_batch = st.selectbox(
                    "Select batch to delete",
                    options=batch_options,
                    key="batch_delete_select",
                    help="Select a batch to permanently delete all its records from all sheets"
                )
            
            with col2:
                if st.button(
                    "🗑️ Delete Selected Batch",
                    disabled=not selected_batch,
                    use_container_width=True,
                    type="secondary"
                ):
                    if selected_batch:
                        # Show confirmation
                        st.warning(f"⚠️ Are you sure you want to delete batch '{selected_batch}'? This action cannot be undone.")
                        
                        col_confirm1, col_confirm2 = st.columns(2)
                        with col_confirm1:
                            if st.button("✅ Yes, Delete Batch", type="primary"):
                                # Get batch summary before deletion
                                batch_summary_before = self.get_batch_summary(selected_batch, data_manager)
                                
                                # Delete the batch
                                deleted_counts = self.delete_batch(selected_batch, data_manager)
                                
                                # Show results
                                total_deleted = sum(deleted_counts.values())
                                if total_deleted > 0:
                                    st.success(f"✅ Successfully deleted batch '{selected_batch}': {total_deleted} records removed")
                                    
                                    # Show detailed breakdown
                                    st.write("**Deletion Summary:**")
                                    for sheet_name, count in deleted_counts.items():
                                        if count > 0:
                                            st.write(f"• {sheet_name}: {count} records deleted")
                                else:
                                    st.info(f"No records found for batch '{selected_batch}'")
                                
                                # Refresh the page to update the batch list
                                st.rerun()
                        
                        with col_confirm2:
                            if st.button("❌ Cancel"):
                                st.rerun()
        else:
            st.info("No batches found. Upload some data to see available batches.")
        
        st.divider()
