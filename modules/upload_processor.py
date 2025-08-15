# modules/upload_processor.py
# Upload processing module for handling file uploads and data processing

import streamlit as st
import pandas as pd
import io
import re
import hashlib
from datetime import date, datetime, timedelta
from calendar import monthrange
from typing import Optional, Tuple, Dict, List, Any

from .config import (
    REQUIRED_COLUMNS_CALLS, ALLOWED_CALLS, CATEGORY_CALLS, RENAME_NAME_CALLS,
    TAB_NAMES, TAB_FALLBACKS
)

class UploadProcessor:
    """Handles file upload processing and data validation"""
    
    def __init__(self, data_manager, batch_manager):
        self.data_manager = data_manager
        self.batch_manager = batch_manager
    
    def process_all_uploads(self, calls_uploader, up_leads, up_init, up_disc, up_ncl,
                           calls_period_key, upload_start, upload_end, force_replace_calls,
                           replace_leads, replace_init, replace_disc, replace_ncl):
        """Process all file uploads with batch management"""
        
        if not any([calls_uploader, up_leads, up_init, up_disc, up_ncl]):
            return
        
        # Get current batch ID
        batch_id = st.session_state.get("current_batch_id", "unknown_batch")
        upload_date = date.today()
        
        success_count = 0
        total_count = 0
        
        # Process Calls upload
        if calls_uploader:
            total_count += 1
            if self._process_calls_upload(calls_uploader, calls_period_key, batch_id, 
                                        upload_date, force_replace_calls):
                success_count += 1
        
        # Process conversion uploads
        if any([up_leads, up_init, up_disc, up_ncl]):
            total_count += 1
            if self._process_conversion_uploads(up_leads, up_init, up_disc, up_ncl,
                                              upload_start, upload_end, batch_id,
                                              upload_date, replace_leads, replace_init,
                                              replace_disc, replace_ncl):
                success_count += 1
        
        # Show results
        if success_count > 0:
            st.success(f"✅ Successfully processed {success_count}/{total_count} uploads")
            st.info(f"Batch ID: {batch_id}")
            
            # Refresh data
            self.data_manager.load_all_data()
            st.rerun()
        else:
            st.error("❌ No uploads were processed successfully")
    
    def _process_calls_upload(self, calls_uploader, period_key: str, batch_id: str,
                             upload_date: date, force_replace: bool) -> bool:
        """Process calls CSV upload"""
        try:
            # Check if file already uploaded
            file_hash = self.data_manager.file_md5(calls_uploader)
            if file_hash in st.session_state.get("hashes_calls", set()) and not force_replace:
                st.warning("This calls file has already been uploaded. Check 'Replace' to upload again.")
                return False
            
            # Read and process the file
            raw_df = self.data_manager._read_any(calls_uploader)
            if raw_df is None or raw_df.empty:
                st.error("Failed to read calls file")
                return False
            
            # Process the data
            processed_df = self.data_manager.process_calls_csv(raw_df, period_key)
            
            # Add batch metadata
            processed_df = self.batch_manager.add_batch_metadata(
                processed_df, batch_id, upload_date, 
                date.today().replace(day=1), 
                (date.today().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            )
            
            # Get existing data
            existing_df = self.data_manager.read_worksheet_by_name("CALLS")
            
            # Handle replacement logic
            if force_replace and not existing_df.empty:
                # Remove existing data for this period
                existing_df = existing_df[existing_df["Month-Year"] != period_key]
                st.info(f"Replacing existing data for {period_key}")
            
            # Combine data
            if existing_df.empty:
                final_df = processed_df
            else:
                final_df = pd.concat([existing_df, processed_df], ignore_index=True)
            
            # Write to Google Sheets
            success = self.data_manager.write_worksheet_by_name("CALLS", final_df)
            
            if success:
                st.session_state.get("hashes_calls", set()).add(file_hash)
                st.success(f"✅ Calls data uploaded successfully ({len(processed_df)} records)")
                return True
            else:
                st.error("Failed to write calls data to Google Sheets")
                return False
                
        except Exception as e:
            st.error(f"Error processing calls upload: {str(e)}")
            return False
    
    def _process_conversion_uploads(self, up_leads, up_init, up_disc, up_ncl,
                                  upload_start: date, upload_end: date, batch_id: str,
                                  upload_date: date, replace_leads: bool, replace_init: bool,
                                  replace_disc: bool, replace_ncl: bool) -> bool:
        """Process conversion data uploads"""
        
        success_count = 0
        total_count = 0
        
        # Process Leads/PNCs
        if up_leads:
            total_count += 1
            if self._process_leads_upload(up_leads, upload_start, upload_end, batch_id,
                                        upload_date, replace_leads):
                success_count += 1
        
        # Process Initial Consultation
        if up_init:
            total_count += 1
            if self._process_init_upload(up_init, upload_start, upload_end, batch_id,
                                       upload_date, replace_init):
                success_count += 1
        
        # Process Discovery Meeting
        if up_disc:
            total_count += 1
            if self._process_disc_upload(up_disc, upload_start, upload_end, batch_id,
                                       upload_date, replace_disc):
                success_count += 1
        
        # Process New Client List
        if up_ncl:
            total_count += 1
            if self._process_ncl_upload(up_ncl, upload_start, upload_end, batch_id,
                                      upload_date, replace_ncl):
                success_count += 1
        
        return success_count > 0
    
    def _process_leads_upload(self, up_leads, upload_start: date, upload_end: date,
                             batch_id: str, upload_date: date, replace: bool) -> bool:
        """Process Leads/PNCs upload"""
        try:
            # Check if file already uploaded
            file_hash = self.data_manager.file_md5(up_leads)
            if file_hash in st.session_state.get("hashes_conv", set()) and not replace:
                st.warning("This leads file has already been uploaded. Check 'Replace' to upload again.")
                return False
            
            # Read the file
            raw_df = self.data_manager._read_any(up_leads)
            if raw_df is None or raw_df.empty:
                st.error("Failed to read leads file")
                return False
            
            # Filter by date range
            filtered_df = self._filter_by_date_range(raw_df, upload_start, upload_end)
            
            # Add batch metadata
            processed_df = self.batch_manager.add_batch_metadata(
                filtered_df, batch_id, upload_date, upload_start, upload_end
            )
            
            # Get existing data
            existing_df = self.data_manager.read_worksheet_by_name("LEADS")
            
            # Handle replacement logic
            if replace and not existing_df.empty:
                # Remove matching records (Email + Matter ID + Stage + IC Date + DM Date)
                existing_df = self._remove_matching_leads(existing_df, processed_df)
                st.info("Replacing matching records in Leads")
            
            # Combine data
            if existing_df.empty:
                final_df = processed_df
            else:
                final_df = pd.concat([existing_df, processed_df], ignore_index=True)
            
            # Write to Google Sheets
            success = self.data_manager.write_worksheet_by_name("LEADS", final_df)
            
            if success:
                st.session_state.get("hashes_conv", set()).add(file_hash)
                st.success(f"✅ Leads data uploaded successfully ({len(processed_df)} records)")
                return True
            else:
                st.error("Failed to write leads data to Google Sheets")
                return False
                
        except Exception as e:
            st.error(f"Error processing leads upload: {str(e)}")
            return False
    
    def _process_init_upload(self, up_init, upload_start: date, upload_end: date,
                            batch_id: str, upload_date: date, replace: bool) -> bool:
        """Process Initial Consultation upload"""
        try:
            # Check if file already uploaded
            file_hash = self.data_manager.file_md5(up_init)
            if file_hash in st.session_state.get("hashes_conv", set()) and not replace:
                st.warning("This initial consultation file has already been uploaded. Check 'Replace' to upload again.")
                return False
            
            # Read the file
            raw_df = self.data_manager._read_any(up_init)
            if raw_df is None or raw_df.empty:
                st.error("Failed to read initial consultation file")
                return False
            
            # Filter by date range
            filtered_df = self._filter_by_date_range(raw_df, upload_start, upload_end)
            
            # Add batch metadata
            processed_df = self.batch_manager.add_batch_metadata(
                filtered_df, batch_id, upload_date, upload_start, upload_end
            )
            
            # Get existing data
            existing_df = self.data_manager.read_worksheet_by_name("INIT")
            
            # Handle replacement logic
            if replace and not existing_df.empty:
                # Remove data for this date range
                existing_df = self._remove_by_date_range(existing_df, upload_start, upload_end)
                st.info("Replacing data for this date range in Initial Consultation")
            
            # Combine data
            if existing_df.empty:
                final_df = processed_df
            else:
                final_df = pd.concat([existing_df, processed_df], ignore_index=True)
            
            # Write to Google Sheets
            success = self.data_manager.write_worksheet_by_name("INIT", final_df)
            
            if success:
                st.session_state.get("hashes_conv", set()).add(file_hash)
                st.success(f"✅ Initial consultation data uploaded successfully ({len(processed_df)} records)")
                return True
            else:
                st.error("Failed to write initial consultation data to Google Sheets")
                return False
                
        except Exception as e:
            st.error(f"Error processing initial consultation upload: {str(e)}")
            return False
    
    def _process_disc_upload(self, up_disc, upload_start: date, upload_end: date,
                            batch_id: str, upload_date: date, replace: bool) -> bool:
        """Process Discovery Meeting upload"""
        try:
            # Check if file already uploaded
            file_hash = self.data_manager.file_md5(up_disc)
            if file_hash in st.session_state.get("hashes_conv", set()) and not replace:
                st.warning("This discovery meeting file has already been uploaded. Check 'Replace' to upload again.")
                return False
            
            # Read the file
            raw_df = self.data_manager._read_any(up_disc)
            if raw_df is None or raw_df.empty:
                st.error("Failed to read discovery meeting file")
                return False
            
            # Filter by date range
            filtered_df = self._filter_by_date_range(raw_df, upload_start, upload_end)
            
            # Add batch metadata
            processed_df = self.batch_manager.add_batch_metadata(
                filtered_df, batch_id, upload_date, upload_start, upload_end
            )
            
            # Get existing data
            existing_df = self.data_manager.read_worksheet_by_name("DISC")
            
            # Handle replacement logic
            if replace and not existing_df.empty:
                # Remove data for this date range
                existing_df = self._remove_by_date_range(existing_df, upload_start, upload_end)
                st.info("Replacing data for this date range in Discovery Meeting")
            
            # Combine data
            if existing_df.empty:
                final_df = processed_df
            else:
                final_df = pd.concat([existing_df, processed_df], ignore_index=True)
            
            # Write to Google Sheets
            success = self.data_manager.write_worksheet_by_name("DISC", final_df)
            
            if success:
                st.session_state.get("hashes_conv", set()).add(file_hash)
                st.success(f"✅ Discovery meeting data uploaded successfully ({len(processed_df)} records)")
                return True
            else:
                st.error("Failed to write discovery meeting data to Google Sheets")
                return False
                
        except Exception as e:
            st.error(f"Error processing discovery meeting upload: {str(e)}")
            return False
    
    def _process_ncl_upload(self, up_ncl, upload_start: date, upload_end: date,
                           batch_id: str, upload_date: date, replace: bool) -> bool:
        """Process New Client List upload"""
        try:
            # Check if file already uploaded
            file_hash = self.data_manager.file_md5(up_ncl)
            if file_hash in st.session_state.get("hashes_conv", set()) and not replace:
                st.warning("This new client list file has already been uploaded. Check 'Replace' to upload again.")
                return False
            
            # Read the file
            raw_df = self.data_manager._read_any(up_ncl)
            if raw_df is None or raw_df.empty:
                st.error("Failed to read new client list file")
                return False
            
            # Filter by date range
            filtered_df = self._filter_by_date_range(raw_df, upload_start, upload_end)
            
            # Add batch metadata
            processed_df = self.batch_manager.add_batch_metadata(
                filtered_df, batch_id, upload_date, upload_start, upload_end
            )
            
            # Get existing data
            existing_df = self.data_manager.read_worksheet_by_name("NCL")
            
            # Handle replacement logic
            if replace and not existing_df.empty:
                # Remove data for this date range
                existing_df = self._remove_by_date_range(existing_df, upload_start, upload_end)
                st.info("Replacing data for this date range in New Client List")
            
            # Combine data
            if existing_df.empty:
                final_df = processed_df
            else:
                final_df = pd.concat([existing_df, processed_df], ignore_index=True)
            
            # Write to Google Sheets
            success = self.data_manager.write_worksheet_by_name("NCL", final_df)
            
            if success:
                st.session_state.get("hashes_conv", set()).add(file_hash)
                st.success(f"✅ New client list data uploaded successfully ({len(processed_df)} records)")
                return True
            else:
                st.error("Failed to write new client list data to Google Sheets")
                return False
                
        except Exception as e:
            st.error(f"Error processing new client list upload: {str(e)}")
            return False
    
    def _filter_by_date_range(self, df: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
        """Filter dataframe by date range using any date column"""
        if df.empty:
            return df
        
        # Find date columns
        date_columns = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['date', 'with pji law']):
                date_columns.append(col)
        
        if not date_columns:
            # If no date columns found, return all data
            return df
        
        # Try to filter by any date column
        for date_col in date_columns:
            try:
                # Convert to datetime
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                # Filter by date range
                mask = (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
                filtered_df = df[mask].copy()
                
                if not filtered_df.empty:
                    return filtered_df
            except Exception:
                continue
        
        # If no filtering worked, return original data
        return df
    
    def _remove_by_date_range(self, df: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
        """Remove records within a date range"""
        if df.empty:
            return df
        
        # Find date columns
        date_columns = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['date', 'with pji law']):
                date_columns.append(col)
        
        if not date_columns:
            return df
        
        # Try to remove by any date column
        for date_col in date_columns:
            try:
                # Convert to datetime
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                # Create mask to keep records outside the date range
                mask = ~((df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date))
                filtered_df = df[mask].copy()
                
                return filtered_df
            except Exception:
                continue
        
        return df
    
    def _remove_matching_leads(self, existing_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        """Remove matching leads records based on Email + Matter ID + Stage + IC Date + DM Date"""
        if existing_df.empty or new_df.empty:
            return existing_df
        
        # Find key columns
        email_col = self._find_column(existing_df, ['email', 'e-mail'])
        matter_col = self._find_column(existing_df, ['matter id', 'matterid', 'matter'])
        stage_col = self._find_column(existing_df, ['stage', 'status'])
        ic_date_col = self._find_column(existing_df, ['initial consultation', 'ic date'])
        dm_date_col = self._find_column(existing_df, ['discovery meeting', 'dm date'])
        
        if not all([email_col, matter_col, stage_col]):
            return existing_df
        
        # Create composite key for matching
        existing_df['_composite_key'] = (
            existing_df[email_col].astype(str) + '|' +
            existing_df[matter_col].astype(str) + '|' +
            existing_df[stage_col].astype(str)
        )
        
        new_df['_composite_key'] = (
            new_df[email_col].astype(str) + '|' +
            new_df[matter_col].astype(str) + '|' +
            new_df[stage_col].astype(str)
        )
        
        # Remove matching records
        matching_keys = set(new_df['_composite_key'].dropna())
        existing_df = existing_df[~existing_df['_composite_key'].isin(matching_keys)]
        
        # Clean up
        existing_df = existing_df.drop('_composite_key', axis=1)
        
        return existing_df
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column by possible names (case-insensitive)"""
        if df.empty:
            return None
        
        df_columns_lower = {col.lower(): col for col in df.columns}
        
        for name in possible_names:
            if name.lower() in df_columns_lower:
                return df_columns_lower[name.lower()]
        
        return None
