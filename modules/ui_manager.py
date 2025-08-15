# modules/ui_manager.py
# UI Manager module for handling all user interface components

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import re
from datetime import date, timedelta
from calendar import monthrange
from typing import Optional, Tuple, Dict, List

from .config import (
    MONTHS_MAP, MONTHS_MAP_NAMES, PRACTICE_AREAS, DISPLAY_NAME_OVERRIDES,
    INITIALS_TO_ATTORNEY, INTAKE_SPECIALISTS, INTAKE_INITIALS_TO_NAME,
    EXCLUDED_PNC_STAGES, TAB_NAMES
)

# Canonical list (stable order) - include all attorneys from practice areas
CANON = list(dict.fromkeys(sum(PRACTICE_AREAS.values(), [])))
# Add "Other" as a special category for attorneys not in predefined lists
CANON.append("Other")

class UIManager:
    """Manages all user interface components and report rendering"""
    
    def __init__(self):
        # Initialize session state for UI
        if "exp_upload_open" not in st.session_state:
            st.session_state["exp_upload_open"] = False
        
        if "hashes_calls" not in st.session_state:
            st.session_state["hashes_calls"] = set()
        
        if "hashes_conv" not in st.session_state:
            st.session_state["hashes_conv"] = set()
    
    def _keep_open_flag(self, flag_key: str):
        """Helper to keep expanders open"""
        st.session_state[flag_key] = True
    
    def render_admin_sidebar(self, data_manager):
        """Render the admin sidebar with data management options"""
        with st.sidebar.expander("📦 Master Data (Google Sheets) — Admin", expanded=False):
            if data_manager.gsheet is None:
                st.warning("Not connected to the master store.")
                st.caption("Add `[gcp_service_account]` and `[google_sheets]` to Secrets.")
                if st.button("🧹 Master Reset (session & caches)", use_container_width=True):
                    for k in ["hashes_calls", "hashes_conv", "exp_upload_open", "logs"]:
                        st.session_state.pop(k, None)
                    try:
                        st.cache_data.clear()
                    except:
                        pass
                    try:
                        st.cache_resource.clear()
                    except:
                        pass
                    st.success("Reset complete. Reloading…")
                    st.rerun()
                return
            
            st.success("Connected to Master Store (Google Sheets).")
            st.caption("Tabs used: " + ", ".join(TAB_NAMES.values()))
            
            if st.button("🔄 Refresh data now", use_container_width=True):
                st.session_state["gs_ver"] += 1
                st.rerun()
            
            # Sheet selection
            sheets = {
                "Calls": "CALLS",
                "Leads/PNCs": "LEADS",
                "Initial Consultation": "INIT",
                "Discovery Meeting": "DISC",
                "New Client List": "NCL",
            }
            sel_label = st.selectbox("Select sheet", list(sheets.keys()))
            key = sheets[sel_label]
            
            # Date inputs
            colY, colM = st.columns(2)
            yr = colY.number_input("Year", min_value=2000, max_value=2100,
                                   value=date.today().year, step=1)
            mo = colM.number_input("Month", min_value=1, max_value=12,
                                   value=date.today().month, step=1)
            
            # Maintenance actions
            st.divider()
            st.subheader("Maintenance")
            st.caption("Safely manage master data. Actions are immediate.")
            
            with st.container(border=True):
                st.markdown("**Purge a month**")
                st.caption("Remove all rows for the selected sheet and month (above).")
                if st.button("Purge Month", use_container_width=True):
                    # Implementation would go here
                    st.info("Purge functionality would be implemented here")
            
            with st.container(border=True):
                st.markdown("**Re-dedupe sheet**")
                st.caption("Rebuilds unique rows using the same keys as the uploader.")
                if st.button("Re-dedupe sheet", use_container_width=True):
                    st.info("Dedupe functionality would be implemented here")
            
            with st.container(border=True):
                st.markdown("**Wipe ALL rows**")
                st.caption("Deletes every row in the selected sheet. Use with care.")
                confirm_wipe = st.checkbox("I understand this cannot be undone.", key="confirm_wipe")
                if st.button("Wipe ALL rows", disabled=not confirm_wipe, use_container_width=True):
                    try:
                        # Get current data
                        current_df = data_manager.read_worksheet_by_name(key)
                        if current_df is not None and not current_df.empty:
                            # Create empty DataFrame with same headers
                            empty_df = pd.DataFrame(columns=current_df.columns)
                            # Write empty DataFrame back to sheet
                            success = data_manager.write_worksheet_by_name(key, empty_df)
                            if success:
                                st.success(f"✅ All data wiped from {sel_label}. Headers preserved.")
                                st.session_state["gs_ver"] = st.session_state.get("gs_ver", 0) + 1
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to wipe data from {sel_label}")
                        else:
                            st.info(f"No data found in {sel_label}")
                    except Exception as e:
                        st.error(f"Error wiping data: {str(e)}")
            
            # Add a master reset option for all sheets
            with st.container(border=True):
                st.markdown("**🗑️ Master Reset (All Sheets)**")
                st.caption("Wipe ALL data from ALL sheets at once. Use with extreme care.")
                confirm_master = st.checkbox("I understand this will delete ALL data from ALL sheets.", key="confirm_master")
                if st.button("🗑️ Master Reset All Sheets", disabled=not confirm_master, use_container_width=True, type="secondary"):
                    try:
                        success_count = 0
                        total_sheets = 5
                        
                        for sheet_name in ["CALLS", "LEADS", "INIT", "DISC", "NCL"]:
                            try:
                                # Get current data
                                current_df = data_manager.read_worksheet_by_name(sheet_name)
                                if current_df is not None and not current_df.empty:
                                    # Create empty DataFrame with same headers
                                    empty_df = pd.DataFrame(columns=current_df.columns)
                                    # Write empty DataFrame back to sheet
                                    success = data_manager.write_worksheet_by_name(sheet_name, empty_df)
                                    if success:
                                        success_count += 1
                                    else:
                                        st.error(f"Failed to wipe {sheet_name}")
                                else:
                                    success_count += 1  # No data to wipe
                            except Exception as e:
                                st.error(f"Error wiping {sheet_name}: {str(e)}")
                        
                        if success_count == total_sheets:
                            st.success("✅ **Master Reset Complete**: All data wiped from all sheets. Headers preserved.")
                            st.session_state["gs_ver"] = st.session_state.get("gs_ver", 0) + 1
                            st.rerun()
                        else:
                            st.warning(f"⚠️ Partial success: {success_count}/{total_sheets} sheets wiped")
                    except Exception as e:
                        st.error(f"Error during master reset: {str(e)}")
    
    def render_upload_section(self, data_manager, batch_manager):
        """Render the data upload section"""
        st.subheader("📤 File Uploads")
        
        # Calls upload
        calls_period_key, calls_uploader = self._render_upload_section("zoom_calls", "Zoom Calls", "exp_upload_open")
        force_replace_calls = st.checkbox("Replace this month in Calls if it already exists",
                                          key="force_calls_replace")
        
        # Conversion uploads
        c1, c2 = st.columns(2)
        upload_start = c1.date_input("Conversion upload start date",
                                     value=date.today().replace(day=1),
                                     key="conv_upload_start",
                                     on_change=self._keep_open_flag, args=("exp_upload_open",))
        upload_end = c2.date_input("Conversion upload end date",
                                   value=date.today(),
                                   key="conv_upload_end",
                                   on_change=self._keep_open_flag, args=("exp_upload_open",))
        
        if upload_start > upload_end:
            st.error("Upload start must be on or before end.")
            st.stop()
        
        # Informational message about data upload
        st.info("📊 Note: All raw data will be uploaded to Google Sheets for auditing. Date range is used for reference only.")
        
        # Add a note about re-uploading after master reset
        if st.session_state.get("master_reset_performed", False):
            st.warning("🔄 **Master Reset Detected**: You may need to click 'Allow Re-upload' in Batch Management if files show as already uploaded.")
        
        # Keep bypass_date_filter for backward compatibility (always True now)
        bypass_date_filter = True
        
        # File uploaders
        up_leads = st.file_uploader("Upload **Leads_PNCs**", type=["csv", "xls", "xlsx"],
                                    key="up_leads_pncs", on_change=self._keep_open_flag, args=("exp_upload_open",))
        replace_leads = st.checkbox("Replace matching records in Leads (Email+Matter ID+Stage+IC Date+DM Date)",
                                    key="rep_leads")
        
        up_init = st.file_uploader("Upload **Initial_Consultation**", type=["csv", "xls", "xlsx"],
                                   key="up_initial", on_change=self._keep_open_flag, args=("exp_upload_open",))
        replace_init = st.checkbox("Replace this date range in Initial_Consultation", key="rep_init")
        
        up_disc = st.file_uploader("Upload **Discovery_Meeting**", type=["csv", "xls", "xlsx"],
                                   key="up_discovery", on_change=self._keep_open_flag, args=("exp_upload_open",))
        replace_disc = st.checkbox("Replace this date range in Discovery_Meeting", key="rep_disc")
        
        up_ncl = st.file_uploader("Upload **New Client List**", type=["csv", "xls", "xlsx"],
                                  key="up_ncl", on_change=self._keep_open_flag, args=("exp_upload_open",))
        replace_ncl = st.checkbox("Replace this date range in New Client List", key="rep_ncl")
        
        # Process uploads
        self._process_uploads(data_manager, batch_manager, calls_uploader, up_leads, up_init, up_disc, up_ncl,
                             calls_period_key, upload_start, upload_end, force_replace_calls,
                             replace_leads, replace_init, replace_disc, replace_ncl, bypass_date_filter)
    
    def _render_upload_section(self, section_id: str, title: str, expander_flag: str) -> Tuple[str, object]:
        """Render individual upload section"""
        st.subheader(title)
        today = date.today()
        first_of_month = today.replace(day=1)
        next_month = (first_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_of_month = next_month - timedelta(days=1)
        
        c1, c2 = st.columns(2)
        start = c1.date_input("Start date", value=first_of_month,
                              key=f"{section_id}_start",
                              on_change=self._keep_open_flag, args=(expander_flag,))
        end = c2.date_input("End date", value=last_of_month,
                            key=f"{section_id}_end",
                            on_change=self._keep_open_flag, args=(expander_flag,))
        
        # Validate date range
        if start > end:
            st.error("Start date must be on or before End date.")
            st.stop()
        
        if (start.year, start.month) != (end.year, end.month):
            st.error("Please select a range within a single calendar month.")
            st.stop()
        
        period_key = f"{start.year}-{start.month:02d}"
        
        uploaded = st.file_uploader(f"Upload {title} CSV", type=["csv"],
                                    key=f"{section_id}_uploader",
                                    on_change=self._keep_open_flag, args=(expander_flag,))
        st.divider()
        return period_key, uploaded
    
    def _process_uploads(self, data_manager, batch_manager, calls_uploader, up_leads, up_init, up_disc, up_ncl,
                         calls_period_key, upload_start, upload_end, force_replace_calls,
                         replace_leads, replace_init, replace_disc, replace_ncl, bypass_date_filter):
        """Process all file uploads"""
        # Import and use the upload processor
        from .upload_processor import UploadProcessor
        
        upload_processor = UploadProcessor(data_manager, batch_manager)
        upload_processor.process_all_uploads(
            calls_uploader, up_leads, up_init, up_disc, up_ncl,
            calls_period_key, upload_start, upload_end, force_replace_calls,
            replace_leads, replace_init, replace_disc, replace_ncl, bypass_date_filter
        )
    
    def render_calls_report(self, data_manager):
        """Render the calls report section"""
        st.markdown("---")
        st.header("📞 Zoom Call Reports")
        
        # Check if calls data is available
        if not hasattr(data_manager, 'df_calls') or data_manager.df_calls.empty:
            st.info("No calls data available. Please upload calls data first.")
            return
        
        with st.expander("📞 Calls Report", expanded=False):
            st.subheader("Filters — Calls")
        
        # Get available months - safely access df_calls
        df_calls = data_manager.df_calls if hasattr(data_manager, 'df_calls') else pd.DataFrame()
        all_months = self._get_available_months(df_calls)
        if all_months:
            latest_my = max(all_months)
            latest_year, latest_mnum = latest_my.split("-")
            latest_mname = MONTHS_MAP.get(latest_mnum, latest_mnum)
        else:
            latest_year, latest_mname = "All", "All"
        
        # Filters
        c1, c2, c3, c4 = st.columns(4)
        years = sorted({m.split("-")[0] for m in all_months})
        year_options = ["All"] + years if years else ["All"]
        sel_year = c1.selectbox("Year", year_options, 
                               index=(year_options.index(latest_year) if latest_year in year_options else 0))
        
        def months_for_year(year_sel: str):
            if year_sel == "All":
                return sorted({m.split("-")[1] for m in all_months})
            return sorted({m.split("-")[1] for m in all_months if m.startswith(year_sel)})
        
        mnums = months_for_year(sel_year)
        mnames = [MONTHS_MAP.get(m, m) for m in mnums]
        month_options = ["All"] + mnames if mnames else ["All"]
        sel_month_name = c2.selectbox("Month", month_options,
                                     index=(month_options.index(latest_mname) if latest_mname in month_options else 0))
        
        cat_choices = ["All"] + (sorted(df_calls["Category"].unique().tolist()) 
                                if not df_calls.empty else [])
        sel_cat = c3.selectbox("Category", cat_choices, index=0)
        base = df_calls if sel_cat == "All" else df_calls[df_calls["Category"] == sel_cat]
        name_choices = ["All"] + (sorted(base["Name"].unique().tolist()) if not base.empty else [])
        sel_name = c4.selectbox("Name", name_choices, index=0)
        
        # Filter data
        filtered_calls = self._filter_calls_data(df_calls, sel_year, sel_month_name, sel_cat, sel_name)
        
        # Display results
        st.subheader("Calls — Results")
        calls_display_cols = [
            "Category", "Name", "Total Calls", "Completed Calls", "Outgoing", "Received",
            "Forwarded to Voicemail", "Answered by Other", "Missed",
            "Avg Call Time", "Total Call Time", "Total Hold Time", "Month-Year"
        ]
        
        if not filtered_calls.empty:
            st.dataframe(filtered_calls[calls_display_cols], hide_index=True, use_container_width=True)
            csv_buf = io.StringIO()
            filtered_calls[calls_display_cols].to_csv(csv_buf, index=False)
            st.download_button("Download filtered Calls CSV", csv_buf.getvalue(),
                               file_name="call_report_filtered.csv", type="primary")
        else:
            st.info("No rows match the current Calls filters.")
        
        # Visualizations
        st.subheader("Calls — Visualizations")
        # Call the visualization manager for calls
        viz_manager = st.session_state.get('viz_manager')
        if viz_manager:
            viz_manager.render_calls_visualizations(data_manager)
        else:
            st.info("Visualization manager not available.")
    
    def _get_available_months(self, df_calls: pd.DataFrame) -> list:
        """Get available months from calls data"""
        if isinstance(df_calls, pd.DataFrame) and not df_calls.empty and "Month-Year" in df_calls.columns:
            return sorted(set(df_calls["Month-Year"].dropna().astype(str)))
        return []
    
    def _filter_calls_data(self, df_calls: pd.DataFrame, sel_year: str, sel_month_name: str, 
                          sel_cat: str, sel_name: str) -> pd.DataFrame:
        """Filter calls data based on selected criteria and aggregate by intake specialist"""
        if df_calls.empty or "Month-Year" not in df_calls.columns:
            return pd.DataFrame()
        
        # Period filter
        m = pd.Series(True, index=df_calls.index)
        if sel_year != "All":
            m &= df_calls["Month-Year"].astype(str).str.startswith(sel_year)
        if sel_month_name != "All":
            month_num = next((k for k, v in MONTHS_MAP.items() if v == sel_month_name), None)
            if month_num:
                m &= df_calls["Month-Year"].astype(str).str.endswith(month_num)
        
        filtered_calls = df_calls.loc[m].copy()
        
        # Additional filters
        mask_calls_extra = pd.Series(True, index=filtered_calls.index)
        if sel_cat != "All":
            mask_calls_extra &= filtered_calls["Category"] == sel_cat
        if sel_name != "All":
            mask_calls_extra &= filtered_calls["Name"] == sel_name
        
        filtered_calls = filtered_calls.loc[mask_calls_extra].copy()
        
        # Aggregate by intake specialist (Name column)
        if not filtered_calls.empty and "Name" in filtered_calls.columns:
            # Group by Name and aggregate numeric columns
            numeric_columns = [
                "Total Calls", "Completed Calls", "Outgoing", "Received",
                "Forwarded to Voicemail", "Answered by Other", "Missed",
                "Total Call Time", "Total Hold Time"
            ]
            
            # Only aggregate columns that exist
            existing_numeric_cols = [col for col in numeric_columns if col in filtered_calls.columns]
            
            if existing_numeric_cols:
                # Group by Name and sum numeric columns
                aggregated = filtered_calls.groupby("Name")[existing_numeric_cols].sum().reset_index()
                
                # Calculate average call time for aggregated data
                if "Total Call Time" in existing_numeric_cols and "Completed Calls" in existing_numeric_cols:
                    # Avoid division by zero
                    aggregated["Avg Call Time"] = aggregated.apply(
                        lambda row: (
                            row["Total Call Time"] / row["Completed Calls"]
                        ).round(2) if row["Completed Calls"] > 0 else 0.0,
                        axis=1
                    )
                
                # Add back non-numeric columns (take first value from each group)
                non_numeric_cols = [col for col in filtered_calls.columns 
                                  if col not in existing_numeric_cols and col != "Name"]
                
                for col in non_numeric_cols:
                    if col in filtered_calls.columns:
                        first_values = filtered_calls.groupby("Name")[col].first().reset_index()
                        aggregated = aggregated.merge(first_values, on="Name", how="left")
                
                return aggregated
        
        return filtered_calls
    
    def render_conversion_report(self, data_manager):
        """Render the conversion report section"""
        st.markdown("---")
        st.header("📊 Firm Conversion Report")
        
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        with st.expander("📅 Filter", expanded=False):
            row = st.columns([2, 1, 1])  # Period (wide), Year, Month
        
        months_map_names = {
            1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
            7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"
        }
        month_nums = list(months_map_names.keys())
        
        # Check if dataframes exist before calling _years_from
        years_detected = set()
        if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty:
            years_detected |= self._years_from((data_manager.df_ncl, "Date we had BOTH the signed CLA and full payment"))
        if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty:
            years_detected |= self._years_from((data_manager.df_ic, "Initial Consultation With Pji Law"))
        if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty:
            years_detected |= self._years_from((data_manager.df_dm, "Discovery Meeting With Pji Law"))
        years_conv = sorted(years_detected) if years_detected else [date.today().year]
        
        with row[0]:
            period_mode = st.radio(
                "Period",
                ["Month to date", "Full month", "Year to date", "Week of month", "Custom range"],
                horizontal=True,
            )
        with row[1]:
            sel_year_conv = st.selectbox("Year", years_conv, index=len(years_conv)-1)
        with row[2]:
            sel_month_num = st.selectbox(
                "Month",
                month_nums,
                index=date.today().month-1,
                format_func=lambda m: months_map_names[m]
            )
        
        week_defs = None
        sel_week_idx = 1
        if period_mode == "Week of month":
            week_defs = self._custom_weeks_for_month(sel_year_conv, sel_month_num)
            def _wk_label(i):
                wk = week_defs[i]; sd, ed = wk["start"], wk["end"]
                return f'{wk["label"]} ({sd.day}–{ed.day} {ed.strftime("%b")})'
            sel_week_idx = st.selectbox("Week of month",
                                        options=list(range(len(week_defs))),
                                        index=1, format_func=_wk_label)
        
        cust_cols = st.columns(2)
        custom_start = custom_end = None
        if period_mode == "Custom range":
            custom_start = cust_cols[0].date_input("Start date", value=date.today().replace(day=1))
            custom_end   = cust_cols[1].date_input("End date",   value=date.today())
            if custom_start > custom_end:
                st.error("Start date must be on or before End date."); st.stop()
        
        # Resolve period → (start_date, end_date)
        if period_mode == "Month to date":
            mstart, mend = self._month_bounds(sel_year_conv, sel_month_num)
            if date.today().month == sel_month_num and date.today().year == sel_year_conv:
                start_date, end_date = mstart, self._clamp_to_today(mend)
            else:
                start_date, end_date = mstart, mend
        elif period_mode == "Full month":
            start_date, end_date = self._month_bounds(sel_year_conv, sel_month_num)
        elif period_mode == "Year to date":
            y_start = date(sel_year_conv, 1, 1)
            y_end   = self._clamp_to_today(date(sel_year_conv, 12, 31)) if sel_year_conv == date.today().year else date(sel_year_conv, 12, 31)
            start_date, end_date = y_start, y_end
        elif period_mode == "Week of month":
            if week_defs and 0 <= sel_week_idx < len(week_defs):
                wk = week_defs[sel_week_idx]
                start_date, end_date = wk["start"], wk["end"]
            else:
                st.error("No weeks available for the selected month. Please try a different period.")
                st.stop()
        else:
            start_date, end_date = custom_start, custom_end
        
        st.caption(f"Showing Conversion metrics for **{start_date:%-d %b %Y} → {end_date:%-d %b %Y}**")
        
        # Store date range in session state for other reports to use
        st.session_state["conversion_date_range"] = (start_date, end_date)
        
        # Filtered slices (date-in-range only; column names are fixed by your files)
        # Find the correct column names - safely check if dataframes exist
        ic_date_col = None
        if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty:
            ic_date_col = self._find_col(data_manager.df_ic, ["Initial Consultation With Pji Law"])
        
        dm_date_col = None
        if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty:
            dm_date_col = self._find_col(data_manager.df_dm, ["Discovery Meeting With Pji Law"])
        
        ncl_date_col = None
        if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty:
            ncl_date_col = self._find_col(data_manager.df_ncl, ["Date we had BOTH the signed CLA and full payment"])
        
        if ic_date_col is None:
            if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty:
                st.error(f"Could not find Initial Consultation date column. Available columns: {list(data_manager.df_ic.columns)}")
            else:
                st.warning("No Initial Consultation data available")
            init_mask = pd.Series(False, index=data_manager.df_ic.index if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty else [])
        else:
            st.success(f"Found IC date column: {ic_date_col}")
            init_mask = self._mask_by_range_dates(data_manager.df_ic, ic_date_col, start_date, end_date)
        
        if dm_date_col is None:
            if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty:
                st.error(f"Could not find Discovery Meeting date column. Available columns: {list(data_manager.df_dm.columns)}")
            else:
                st.warning("No Discovery Meeting data available")
            disc_mask = pd.Series(False, index=data_manager.df_dm.index if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty else [])
        else:
            st.success(f"Found DM date column: {dm_date_col}")
            disc_mask = self._mask_by_range_dates(data_manager.df_dm, dm_date_col, start_date, end_date)
        
        if ncl_date_col is None:
            if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty:
                st.error(f"Could not find NCL date column. Available columns: {list(data_manager.df_ncl.columns)}")
            else:
                st.warning("No New Client List data available")
            ncl_mask = pd.Series(False, index=data_manager.df_ncl.index if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty else [])
        else:
            st.success(f"Found NCL date column: {ncl_date_col}")
            ncl_mask = self._mask_by_range_dates(data_manager.df_ncl, ncl_date_col, start_date, end_date)
        
        init_in = data_manager.df_ic.loc[init_mask].copy() if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty else pd.DataFrame()
        disc_in = data_manager.df_dm.loc[disc_mask].copy() if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty else pd.DataFrame()
        ncl_in  = data_manager.df_ncl.loc[ncl_mask].copy()  if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty  else pd.DataFrame()
        
        # Leads & PNCs — batch period overlap (unchanged)
        if hasattr(data_manager, 'df_leads') and not data_manager.df_leads.empty and {"__batch_start","__batch_end"} <= set(data_manager.df_leads.columns):
            bs = pd.to_datetime(data_manager.df_leads["__batch_start"], errors="coerce")
            be = pd.to_datetime(data_manager.df_leads["__batch_end"],   errors="coerce")
            start_ts, end_ts = pd.Timestamp(start_date), pd.Timestamp(end_date)
            leads_in_range = (bs <= end_ts) & (be >= start_ts)
        else:
            leads_in_range = pd.Series(False, index=data_manager.df_leads.index if hasattr(data_manager, 'df_leads') else [])
        
        row1 = int(
            data_manager.df_leads.loc[
                leads_in_range &
                (data_manager.df_leads["Stage"].astype(str).str.strip() != "Marketing/Scam/Spam (Non-Lead)")
            ].shape[0]
        ) if hasattr(data_manager, 'df_leads') and not data_manager.df_leads.empty and "Stage" in data_manager.df_leads.columns else 0
        
        row2 = int(
            data_manager.df_leads.loc[
                leads_in_range &
                (~data_manager.df_leads["Stage"].astype(str).str.strip().isin(EXCLUDED_PNC_STAGES))
            ].shape[0]
        ) if hasattr(data_manager, 'df_leads') and not data_manager.df_leads.empty and "Stage" in data_manager.df_leads.columns else 0
        
        # Compute scheduled/met for IC and DM
        ic_sched, ic_met = self._scheduled_and_met(init_in)
        dm_sched, dm_met = self._scheduled_and_met(disc_in)
        
        # NCL retained split within range (unchanged)
        ncl_flag_col = None
        for candidate in ["Retained With Consult (Y/N)", "Retained with Consult (Y/N)"]:
            if candidate in ncl_in.columns:
                ncl_flag_col = candidate; break
        
        if ncl_flag_col:
            flag_in = ncl_in[ncl_flag_col].astype(str).str.strip().str.upper()
            row3 = int((flag_in == "N").sum())           # retained without consult
            row8 = int((flag_in != "N").sum())           # retained after consult
        else:
            row3 = 0
            row8 = int(ncl_in.shape[0])
        
        row10 = int(ncl_in.shape[0])                     # total retained
        row4  = int(ic_sched + dm_sched)                 # scheduled consultations
        row6  = int(ic_met   + dm_met)                   # met (showed) consultations
        
        row5  = self._pct(row4, (row2 - row3))
        row7  = self._pct(row6, row4)
        row9  = self._pct(row8, row4)
        row11 = self._pct(row10, row2)
        
        # Static HTML KPI table
        kpi_rows = [
            ("# of Leads", row1),
            ("# of PNCs", row2),
            ("PNCs who retained without consultation", row3),
            ("PNCs who scheduled consultation", row4),
            ("% of remaining PNCs who scheduled consult", f"{row5}%"),
            ("# of PNCs who showed up for consultation", row6),
            ("% of PNCs who scheduled consult showed up", f"{row7}%"),
            ("PNCs who retained after scheduled consult", row8),
            ("% of PNCs who retained after consult", f"{row9}%"),
            ("# of Total PNCs who retained", row10),
            ("% of total PNCs who retained", f"{row11}%"),
        ]
        table_rows = "\n".join(
            f"<tr><td>{self._html_escape(k)}</td><td style='text-align:right'>{self._html_escape(v)}</td></tr>"
            for k, v in kpi_rows
        )
        html_table = """
<style>
.kpi-table { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.kpi-table th, .kpi-table td { border: 1px solid #eee; padding: 10px 12px; }
.kpi-table th { background: #fafafa; text-align: left; font-weight: 600; }
</style>
<table class="kpi-table">
  <thead><tr><th>Metric</th><th>Value</th></tr></thead>
  <tbody>
    """ + table_rows + """
  </tbody>
</table>
"""
        with st.expander("📊 Summary", expanded=False):
            st.markdown(html_table, unsafe_allow_html=True)
    
    def render_practice_area_report(self, data_manager, start_date=None, end_date=None):
        """Render the practice area report section"""
        st.header("📊 Practice Area")
        
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # If no date range provided, try to get it from conversion report, otherwise use the same logic
        if start_date is None or end_date is None:
            # Try to get date range from conversion report
            conversion_range = st.session_state.get("conversion_date_range")
            if conversion_range:
                start_date, end_date = conversion_range
                st.info(f"📅 Using date range from Conversion Report: {start_date:%-d %b %Y} → {end_date:%-d %b %Y}")
            else:
                with st.expander("📅 Filter", expanded=False):
                    row = st.columns([2, 1, 1])  # Period (wide), Year, Month
                
                    months_map_names = {
                        1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
                        7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"
                    }
                    month_nums = list(months_map_names.keys())
                    
                    # Check if dataframes exist before calling _years_from
                    years_detected = set()
                    if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty:
                        years_detected |= self._years_from((data_manager.df_ncl, "Date we had BOTH the signed CLA and full payment"))
                    if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty:
                        years_detected |= self._years_from((data_manager.df_ic, "Initial Consultation With Pji Law"))
                    if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty:
                        years_detected |= self._years_from((data_manager.df_dm, "Discovery Meeting With Pji Law"))
                    years_conv = sorted(years_detected) if years_detected else [date.today().year]
                    
                    with row[0]:
                        period_mode = st.radio(
                            "Period",
                            ["Month to date", "Full month", "Year to date", "Week of month", "Custom range"],
                            horizontal=True,
                            key="practice_period_mode"
                        )
                    with row[1]:
                        sel_year_conv = st.selectbox("Year", years_conv, index=len(years_conv)-1, key="practice_year")
                    with row[2]:
                        sel_month_num = st.selectbox(
                            "Month",
                            month_nums,
                            index=date.today().month-1,
                            format_func=lambda m: months_map_names[m],
                            key="practice_month"
                        )
                    
                    # Resolve period → (start_date, end_date) - same logic as conversion report
                    if period_mode == "Month to date":
                        mstart, mend = self._month_bounds(sel_year_conv, sel_month_num)
                        if date.today().month == sel_month_num and date.today().year == sel_year_conv:
                            start_date, end_date = mstart, self._clamp_to_today(mend)
                        else:
                            start_date, end_date = mstart, mend
                    elif period_mode == "Full month":
                        start_date, end_date = self._month_bounds(sel_year_conv, sel_month_num)
                    elif period_mode == "Year to date":
                        y_start = date(sel_year_conv, 1, 1)
                        y_end   = self._clamp_to_today(date(sel_year_conv, 12, 31)) if sel_year_conv == date.today().year else date(sel_year_conv, 12, 31)
                        start_date, end_date = y_start, y_end
                    else:
                        # For now, use month to date as default
                        mstart, mend = self._month_bounds(sel_year_conv, sel_month_num)
                        start_date, end_date = mstart, self._clamp_to_today(mend)
        
        st.caption(f"Showing Practice Area metrics for **{start_date:%-d %b %Y} → {end_date:%-d %b %Y}**")
        
        # Build counts & report using the SAME logic as conversion report
        # First, get the same filtered data as conversion report
        ic_date_col = None
        if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty:
            ic_date_col = self._find_col(data_manager.df_ic, ["Initial Consultation With Pji Law"])
        
        dm_date_col = None
        if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty:
            dm_date_col = self._find_col(data_manager.df_dm, ["Discovery Meeting With Pji Law"])
        
        ncl_date_col = None
        if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty:
            ncl_date_col = self._find_col(data_manager.df_ncl, ["Date we had BOTH the signed CLA and full payment"])
        
        # Apply same filters as conversion report
        init_mask = self._mask_by_range_dates(data_manager.df_ic, ic_date_col, start_date, end_date) if ic_date_col and hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty else pd.Series(False, index=data_manager.df_ic.index if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty else [])
        disc_mask = self._mask_by_range_dates(data_manager.df_dm, dm_date_col, start_date, end_date) if dm_date_col and hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty else pd.Series(False, index=data_manager.df_dm.index if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty else [])
        ncl_mask = self._mask_by_range_dates(data_manager.df_ncl, ncl_date_col, start_date, end_date) if ncl_date_col and hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty else pd.Series(False, index=data_manager.df_ncl.index if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty else [])
        
        init_in = data_manager.df_ic.loc[init_mask].copy() if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty else pd.DataFrame()
        disc_in = data_manager.df_dm.loc[disc_mask].copy() if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty else pd.DataFrame()
        ncl_in = data_manager.df_ncl.loc[ncl_mask].copy() if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty else pd.DataFrame()
        
        # Now use the same logic as conversion report for "met with" and "retained"
        # Get "met with" counts using same logic as conversion report
        ic_sched, ic_met = self._scheduled_and_met(init_in)
        dm_sched, dm_met = self._scheduled_and_met(disc_in)
        
        # For practice area, we need to break down by attorney
        # Use the same index-based approach but with the filtered data
        met_counts_raw = self._met_counts_from_ic_dm_index(init_in, disc_in, start_date, end_date)
        met_by_attorney = {name: 0 for name in CANON}  # Initialize all attorneys with 0
        
        # Distribute counts to appropriate attorneys, aggregating unknown ones to "Other"
        for name, count in met_counts_raw.items():
            if name in CANON:
                met_by_attorney[name] = int(count)
            else:
                # If attorney not in CANON, add to "Other" count
                met_by_attorney["Other"] = met_by_attorney.get("Other", 0) + int(count)
        
        # Get retained counts using same logic as conversion report
        # NCL retained split within range (same as conversion report)
        ncl_flag_col = None
        for candidate in ["Retained With Consult (Y/N)", "Retained with Consult (Y/N)"]:
            if candidate in ncl_in.columns:
                ncl_flag_col = candidate; break
        
        if ncl_flag_col:
            flag_in = ncl_in[ncl_flag_col].astype(str).str.strip().str.upper()
            # For practice area, we want total retained (both with and without consult)
            retained_total = int((flag_in == "N").sum()) + int((flag_in != "N").sum())  # without + with consult
        else:
            retained_total = int(ncl_in.shape[0])
        
        # For practice area, we need to break down retained by attorney
        # Use the same robust column detection as conversion report
        retained_by_attorney = self._retained_counts_from_ncl(ncl_in, start_date, end_date)
        
        report = pd.DataFrame({
            "Attorney": CANON,
            "Practice Area": [ self._practice_for(a) if a != "Other" else "Other" for a in CANON ],
        })
        report["PNCs who met"] = report["Attorney"].map(lambda a: int(met_by_attorney.get(a, 0)))
        report["PNCs who met and retained"] = report["Attorney"].map(lambda a: int(retained_by_attorney.get(a, 0)))
        report["Attorney_Display"] = report["Attorney"].map(lambda a: "Other" if a == "Other" else self._disp(a))
        report["% of PNCs who met and retained"] = report.apply(
            lambda r: 0.0 if int(r["PNCs who met"]) == 0  # Use individual attorney's "met with" count as denominator
                      else round((int(r["PNCs who met and retained"]) / int(r["PNCs who met"])) * 100.0, 2),
            axis=1
        )
        
        # Render per practice area
        for pa in ["Estate Planning","Estate Administration","Civil Litigation","Business transactional","Other"]:
            sub = report.loc[report["Practice Area"] == pa].copy()
            met_sum  = int(sub["PNCs who met"].sum())
            kept_sum = int(sub["PNCs who met and retained"].sum())
            pct_sum  = 0.0 if met_sum == 0 else round((kept_sum / met_sum) * 100.0, 0)
        
            with st.expander(pa, expanded=False):
                attys = ["ALL"] + sub["Attorney_Display"].tolist()
                pick = st.selectbox(f"{pa} — choose attorney", attys, key=f"pa_pick_{pa.replace(' ','_')}")
                if pick == "ALL":
                    # For ALL, calculate percentage based on practice area's total "met with" count
                    pct_all = 0.0 if met_sum == 0 else round((kept_sum / met_sum) * 100.0, 0)
                    self._render_three_row_card("ALL", met_sum, kept_sum, pct_all)
                else:
                    rowx = sub.loc[sub["Attorney_Display"] == pick].iloc[0]
                    self._render_three_row_card(
                        pick,
                        int(rowx["PNCs who met"]),
                        int(rowx["PNCs who met and retained"]),
                        float(rowx["% of PNCs who met and retained"]),
                    )
    
    def render_intake_report(self, data_manager, start_date=None, end_date=None):
        """Render the intake report section"""
        st.header("📊 Conversion Report: Intake")
        
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # If no date range provided, try to get it from conversion report, otherwise use the same logic
        if start_date is None or end_date is None:
            # Try to get date range from conversion report
            conversion_range = st.session_state.get("conversion_date_range")
            if conversion_range:
                start_date, end_date = conversion_range
                st.info(f"📅 Using date range from Conversion Report: {start_date:%-d %b %Y} → {end_date:%-d %b %Y}")
            else:
                with st.expander("📅 Filter", expanded=False):
                    row = st.columns([2, 1, 1])  # Period (wide), Year, Month
                
                    months_map_names = {
                        1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
                        7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"
                    }
                    month_nums = list(months_map_names.keys())
                    
                    # Check if dataframes exist before calling _years_from
                    years_detected = set()
                    if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty:
                        years_detected |= self._years_from((data_manager.df_ncl, "Date we had BOTH the signed CLA and full payment"))
                    if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty:
                        years_detected |= self._years_from((data_manager.df_ic, "Initial Consultation With Pji Law"))
                    if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty:
                        years_detected |= self._years_from((data_manager.df_dm, "Discovery Meeting With Pji Law"))
                    years_conv = sorted(years_detected) if years_detected else [date.today().year]
                    
                    with row[0]:
                        period_mode = st.radio(
                            "Period",
                            ["Month to date", "Full month", "Year to date", "Week of month", "Custom range"],
                            horizontal=True,
                            key="intake_period_mode"
                        )
                    with row[1]:
                        sel_year_conv = st.selectbox("Year", years_conv, index=len(years_conv)-1, key="intake_year")
                    with row[2]:
                        sel_month_num = st.selectbox(
                            "Month",
                            month_nums,
                            index=date.today().month-1,
                            format_func=lambda m: months_map_names[m],
                            key="intake_month"
                        )
                    
                    # Resolve period → (start_date, end_date) - same logic as conversion report
                    if period_mode == "Month to date":
                        mstart, mend = self._month_bounds(sel_year_conv, sel_month_num)
                        if date.today().month == sel_month_num and date.today().year == sel_year_conv:
                            start_date, end_date = mstart, self._clamp_to_today(mend)
                        else:
                            start_date, end_date = mstart, mend
                    elif period_mode == "Full month":
                        start_date, end_date = self._month_bounds(sel_year_conv, sel_month_num)
                    elif period_mode == "Year to date":
                        y_start = date(sel_year_conv, 1, 1)
                        y_end   = self._clamp_to_today(date(sel_year_conv, 12, 31)) if sel_year_conv == date.today().year else date(sel_year_conv, 12, 31)
                        start_date, end_date = y_start, y_end
                    else:
                        # For now, use month to date as default
                        mstart, mend = self._month_bounds(sel_year_conv, sel_month_num)
                        start_date, end_date = mstart, self._clamp_to_today(mend)
        
        st.caption(f"Showing Intake metrics for **{start_date:%-d %b %Y} → {end_date:%-d %b %Y}**")
        
        # Calculate intake metrics for all specialists using original logic
        intake_specialists = INTAKE_SPECIALISTS + ["Everyone Else"]
        intake_results = {}
        
        # Get total PNCs from main conversion report for percentage calculations
        # We need to calculate this using the same logic as conversion report
        total_pncs = self._calculate_total_pncs_for_intake(data_manager, start_date, end_date)
        
        for specialist in intake_specialists:
            row1 = self._intake_pncs_by_specialist(
                data_manager.df_leads if hasattr(data_manager, 'df_leads') and not data_manager.df_leads.empty else pd.DataFrame(),
                specialist, start_date, end_date
            )
            row3 = self._intake_retained_without_consult(
                data_manager.df_ncl if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty else pd.DataFrame(),
                specialist, start_date, end_date
            )
            row4 = self._intake_scheduled_consult(
                data_manager.df_ic if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty else pd.DataFrame(),
                data_manager.df_dm if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty else pd.DataFrame(),
                specialist, start_date, end_date
            )
            row6 = self._intake_showed_consult(
                data_manager.df_ic if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty else pd.DataFrame(),
                data_manager.df_dm if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty else pd.DataFrame(),
                specialist, start_date, end_date
            )
            row8 = self._intake_retained_after_consult(
                data_manager.df_ncl if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty else pd.DataFrame(),
                specialist, start_date, end_date
            )
            row10 = self._intake_total_retained(
                data_manager.df_ncl if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty else pd.DataFrame(),
                specialist, start_date, end_date
            )
            
            # Calculate percentages
            row2_pct = self._pct(row1, total_pncs) if total_pncs > 0 else 0  # % of total PNCs
            row5_pct = self._pct(row4, (row1 - row3)) if (row1 - row3) > 0 else 0  # % of remaining PNCs who scheduled
            row7_pct = self._pct(row6, row4) if row4 > 0 else 0  # % who showed up
            row9_pct = self._pct(row8, row4) if row4 > 0 else 0  # % retained after consult
            row11_pct = self._pct(row10, row1) if row1 > 0 else 0  # % of total PNCs who retained
            
            intake_results[specialist] = {
                "PNCs did intake": row1,
                "% of total PNCs": row2_pct,
                "Retained without consult": row3,
                "Scheduled consult": row4,
                "% remaining scheduled": row5_pct,
                "Showed up": row6,
                "% showed up": row7_pct,
                "Retained after consult": row8,
                "% retained after consult": row9_pct,
                "Total retained": row10,
                "% total retained": row11_pct
            }
        
        # Render intake report
        with st.expander("📅 Filter", expanded=False):
            intake_specialists_display = ["ALL"] + intake_specialists
            selected_intake = st.selectbox("Select Intake Specialist", intake_specialists_display, key="intake_specialist_pick")
        
        with st.expander("📊 Summary", expanded=False):
            if selected_intake == "ALL":
                # Show summary for all specialists (sum of all metrics)
                st.subheader("Intake Summary - All Specialists Combined")
                
                # Calculate sums across all specialists
                total_pncs_intake = sum(data["PNCs did intake"] for data in intake_results.values())
                total_retained_without = sum(data["Retained without consult"] for data in intake_results.values())
                total_scheduled = sum(data["Scheduled consult"] for data in intake_results.values())
                total_showed_up = sum(data["Showed up"] for data in intake_results.values())
                total_retained_after = sum(data["Retained after consult"] for data in intake_results.values())
                total_retained = sum(data["Total retained"] for data in intake_results.values())
                
                # Calculate percentages for ALL
                all_pct_total = self._pct(total_pncs_intake, total_pncs) if total_pncs > 0 else 0
                all_pct_remaining_scheduled = self._pct(total_scheduled, (total_pncs_intake - total_retained_without)) if (total_pncs_intake - total_retained_without) > 0 else 0
                all_pct_showed_up = self._pct(total_showed_up, total_scheduled) if total_scheduled > 0 else 0
                all_pct_retained_after = self._pct(total_retained_after, total_scheduled) if total_scheduled > 0 else 0
                all_pct_total_retained = self._pct(total_retained, total_pncs_intake) if total_pncs_intake > 0 else 0
                
                # Create summary table with summed metrics
                all_summary_rows = [
                    ("Total PNCs all intake specialists did intake", str(total_pncs_intake)),
                    ("% of total PNCs received all intake specialists did intake", f"{int(round(all_pct_total))}%"),
                    ("Total PNCs who retained without consultation", str(total_retained_without)),
                    ("Total PNCs who scheduled consultation", str(total_scheduled)),
                    ("% of remaining PNCs who scheduled consult", f"{int(round(all_pct_remaining_scheduled))}%"),
                    ("Total PNCs who showed up for consultation", str(total_showed_up)),
                    ("% of PNCs who showed up for consultation", f"{int(round(all_pct_showed_up))}%"),
                    ("Total PNCs retained after scheduled consultation", str(total_retained_after)),
                    ("% of PNCs who retained after scheduled consult", f"{int(round(all_pct_retained_after))}%"),
                    ("All intake specialists' total PNCs who retained", str(total_retained)),
                    ("% of total PNCs received who retained", f"{int(round(all_pct_total_retained))}%"),
                ]
                
                all_summary_df = pd.DataFrame(all_summary_rows, columns=["Metric", "Value"])
                st.dataframe(all_summary_df, use_container_width=True, hide_index=True)
                
            else:
                # Show detailed metrics for selected specialist in row format like practice area
                st.subheader(f"Intake Metrics - {selected_intake}")
                
                data = intake_results[selected_intake]
                
                # Create row-based table like practice area section with personalized labels
                intake_rows = [
                    (f"PNCs {selected_intake} did intake", str(data["PNCs did intake"])),
                    (f"% of total PNCs received {selected_intake} did intake", f"{int(round(data['% of total PNCs']))}%"),
                    (f"PNCs who retained without consultation", str(data["Retained without consult"])),
                    (f"PNCs who scheduled consultation", str(data["Scheduled consult"])),
                    (f"% of remaining PNCs who scheduled consult", f"{int(round(data['% remaining scheduled']))}%"),
                    (f"PNCs who showed up for consultation", str(data["Showed up"])),
                    (f"% of PNCs who showed up for consultation", f"{int(round(data['% showed up']))}%"),
                    (f"PNCs retained after scheduled consultation", str(data["Retained after consult"])),
                    (f"% of PNCs who retained after scheduled consult", f"{int(round(data['% retained after consult']))}%"),
                    (f"{selected_intake}'s total PNCs who retained", str(data["Total retained"])),
                    (f"% of total PNCs received who retained", f"{int(round(data['% total retained']))}%"),
                ]
                
                # Create DataFrame for display
                intake_df = pd.DataFrame(intake_rows, columns=["Metric", "Value"])
                st.dataframe(intake_df, use_container_width=True, hide_index=True)
    
    def render_visualizations(self, data_manager, viz_manager):
        """Render the visualizations section"""
        st.markdown("---")
        st.header("📊 Conversion Trend Visualizations")
        
        # Date range selector for visualizations
        col1, col2 = st.columns(2)
        with col1:
            viz_start_date = st.date_input(
                "Start Date",
                value=date.today().replace(day=1),
                key="viz_start_date"
            )
        with col2:
            viz_end_date = st.date_input(
                "End Date", 
                value=date.today(),
                key="viz_end_date"
            )
        
        if viz_start_date > viz_end_date:
            st.error("Start date must be on or before end date.")
            return
        
        # Render visualizations
        viz_manager.render_conversion_trend_visualizations(data_manager, (viz_start_date, viz_end_date))
    
    def render_debug_section(self, data_manager):
        """Render the debug section"""
        st.markdown("---")
        st.header("🔧 Debugging & Troubleshooting")
        
        with st.expander("Debugging & Troubleshooting", expanded=False):
            st.info("Debug functionality would be implemented here")
            
            with st.expander("ℹ️ Logs (tech details)", expanded=False):
                if st.session_state["logs"]:
                    for line in st.session_state["logs"]:
                        st.code(line)
                else:
                    st.caption("No technical logs this session.")

    # ===== COMPREHENSIVE UI METHODS =====
    
    def _html_escape(self, s: str) -> str:
        """Escape HTML characters"""
        return (str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

    def _find_col(self, df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
        """Find column by name (case-insensitive)"""
        if df is None or df.empty: 
            return None
        cols = {c.lower().strip(): c for c in df.columns}
        for cand in candidates:
            k = cand.lower().strip()
            if k in cols: 
                return cols[k]
        return None

    def _is_blank(self, series: pd.Series) -> pd.Series:
        """Check if series values are blank"""
        if not isinstance(series, pd.Series):
            return pd.Series([True])
        s = series.astype(str)
        blank_tokens = {"", "nan", "none", "na", "null"}
        return s.isna() | s.str.strip().eq("") | s.str.strip().str.lower().isin(blank_tokens)

    def _clean_dt_text(self, x: str) -> str:
        """Clean date text for parsing"""
        if x is None: 
            return ""
        s = str(x).replace("\xa0", " ").strip()
        s = s.replace("–","-").replace(",", " ")
        s = re.sub(r"\s+at\s+", " ", s, flags=re.I)
        s = re.sub(r"\s+(ET|EDT|EST|CT|CDT|CST|MT|MDT|MST|PT|PDT)\b", "", s, flags=re.I)
        s = re.sub(r"(\d)(am|pm)\b", r"\1 \2", s, flags=re.I)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _to_ts(self, series: pd.Series) -> pd.Series:
        """Convert series to timestamps"""
        if not isinstance(series, pd.Series) or series.empty:
            return pd.to_datetime(pd.Series([], dtype=object))
        cleaned = series.astype(str).map(self._clean_dt_text)
        dt = pd.to_datetime(cleaned, errors="coerce", format="mixed")
        if dt.isna().any():
            y = dt.copy()
            for fmt in ("%m/%d/%Y %I:%M %p", "%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M", "%m/%d/%Y"):
                m = y.isna()
                if not m.any(): 
                    break
                try:
                    y.loc[m] = pd.to_datetime(cleaned.loc[m], format=fmt, errors="coerce")
                except Exception:
                    pass
            dt = y
        try:
            dt = dt.dt.tz_localize(None)
        except Exception:
            pass
        return dt

    def _between_inclusive(self, series: pd.Series, sd: date, ed: date) -> pd.Series:
        """Check if dates are between start and end dates"""
        ts = self._to_ts(series)
        return (ts.dt.date >= sd) & (ts.dt.date <= ed)

    def _col_by_idx(self, df: pd.DataFrame, idx: int) -> Optional[str]:
        """Get column by index"""
        if not isinstance(df, pd.DataFrame) or df.empty: 
            return None
        return df.columns[idx] if idx < df.shape[1] else None

    def _practice_for(self, name: str) -> str:
        """Get practice area for attorney name"""
        for pa, names in PRACTICE_AREAS.items():
            if name in names:
                return pa
        return "Other"

    def _disp(self, n: str) -> str:
        """Get display name with overrides"""
        return DISPLAY_NAME_OVERRIDES.get(n, n)

    def _intake_specialist_for(self, name: str) -> str:
        """Map intake specialist name to canonical name or 'Everyone Else'"""
        if name in INTAKE_SPECIALISTS:
            return name
        return "Everyone Else"

    def _intake_name_from_initials(self, initials: str) -> str:
        """Map intake specialist initials to canonical name or 'Everyone Else'"""
        return INTAKE_INITIALS_TO_NAME.get(initials, "Everyone Else")

    def _years_from(self, *dfs_cols) -> set:
        """Get years from multiple dataframes and columns"""
        ys = set()
        for df, col in dfs_cols:
            if df is not None and not df.empty and col in df.columns:
                ys |= set(pd.to_datetime(df[col], errors="coerce").dt.year.dropna().astype(int))
        return ys

    def _month_bounds(self, year: int, month: int) -> Tuple[date, date]:
        """Get start and end dates for a month"""
        last_day = monthrange(year, month)[1]
        start = date(year, month, 1)
        end = date(year, month, last_day)
        return start, end

    def _clamp_to_today(self, end_date: date) -> date:
        """Clamp end date to today"""
        today = date.today()
        return min(end_date, today)

    def _scheduled_and_met(self, df: pd.DataFrame) -> Tuple[int, int]:
        """Calculate scheduled and met counts for consultations"""
        if df is None or df.empty:
            return 0, 0

        # Exclude Follow Up (Column G = 'Sub Status')
        sub_col = self._find_col(df, ["Sub Status"])
        in_scope = df.copy()
        if sub_col and sub_col in in_scope.columns:
            in_scope = in_scope.loc[~in_scope[sub_col].astype(str).str.strip().str.lower().eq("follow up")].copy()

        scheduled = int(len(in_scope))

        # Column I (Reason for Rescheduling) — treat real blanks, NaN, and whitespace as blank
        reason_col = self._find_col(in_scope, ["Reason for Rescheduling"]) or (in_scope.columns[8] if in_scope.shape[1] >= 9 else None)
        if reason_col:
            vals = in_scope[reason_col]
            non_blank = vals.notna() & vals.astype(str).str.strip().ne("")
        else:
            non_blank = pd.Series(False, index=in_scope.index)

        met = int((~non_blank).sum())
        return scheduled, met

    def _pct(self, numer, denom) -> float:
        """Calculate percentage"""
        return 0 if (denom is None or denom == 0) else round((numer/denom)*100)

    def _met_counts_from_ic_dm_index(self, ic_df: pd.DataFrame, dm_df: pd.DataFrame,
                                   sd: date, ed: date) -> pd.Series:
        """Get met counts from IC and DM dataframes using index-based approach"""
        out = {}

        # Initial_Consultation: L(11)=Lead Attorney, M(12)=IC date, G(6)=Sub Status, I(8)=Reason
        if isinstance(ic_df, pd.DataFrame) and ic_df.shape[1] >= 13:
            att, dtc, sub, rsn = ic_df.columns[11], ic_df.columns[12], ic_df.columns[6], ic_df.columns[8]
            t = ic_df.copy()
            m = self._between_inclusive(t[dtc], sd, ed)
            m &= ~t[sub].astype(str).str.strip().str.lower().eq("follow up")
            # Exclude rows where reason contains "Canceled Meeting" or "No Show"
            reason_str = t[rsn].astype(str).str.strip().str.lower()
            m &= ~reason_str.str.contains("canceled meeting", na=False)
            m &= ~reason_str.str.contains("no show", na=False)
            vc = t.loc[m, att].astype(str).str.strip().value_counts(dropna=False)
            for k, v in vc.items():
                if k:
                    out[k] = out.get(k, 0) + int(v)

        # Discovery_Meeting: L(11)=Lead Attorney, P(15)=DM date, G(6)=Sub Status, I(8)=Reason
        if isinstance(dm_df, pd.DataFrame) and dm_df.shape[1] >= 16:
            att, dtc, sub, rsn = dm_df.columns[11], dm_df.columns[15], dm_df.columns[6], dm_df.columns[8]
            t = dm_df.copy()
            m = self._between_inclusive(t[dtc], sd, ed)
            m &= ~t[sub].astype(str).str.strip().str.lower().eq("follow up")
            # Exclude rows where reason contains "Canceled Meeting" or "No Show"
            reason_str = t[rsn].astype(str).str.strip().str.lower()
            m &= ~reason_str.str.contains("canceled meeting", na=False)
            m &= ~reason_str.str.contains("no show", na=False)
            vc = t.loc[m, att].astype(str).str.strip().value_counts(dropna=False)
            for k, v in vc.items():
                if k:
                    out[k] = out.get(k, 0) + int(v)

        return pd.Series(out, dtype=int)

    def _retained_counts_from_ncl(self, ncl_df: pd.DataFrame, sd: date, ed: date) -> Dict[str, int]:
        """Get retained counts from NCL dataframe"""
        # Canonical list of attorneys
        canon = list(dict.fromkeys(sum(PRACTICE_AREAS.values(), [])))
        canon.append("Other")
        
        if not isinstance(ncl_df, pd.DataFrame) or ncl_df.empty:
            return {name: 0 for name in canon}

        def _norm(s: str) -> str:
            s = str(s).lower().strip()
            s = re.sub(r"[\s_]+"," ", s)
            s = re.sub(r"[^a-z0-9 ]","", s)
            return s

        cols = list(ncl_df.columns)
        norms = {c: _norm(c) for c in cols}

        # Find date column
        prefer_date = _norm("Date we had BOTH the signed CLA and full payment")
        date_col = next((c for c in cols if norms[c] == prefer_date), None)
        if date_col is None:
            cands = [c for c in cols if all(tok in norms[c] for tok in ["date","signed","payment"])]
            if cands:
                cands.sort(key=lambda c: len(norms[c]))
                date_col = cands[0]
        if date_col is None:
            date_col = next((c for c in cols if "date" in norms[c]), None)
        if date_col is None and len(cols) > 6:
            date_col = cols[6]  # Column G

        # Find responsible attorney column
        init_col = next((c for c in cols if all(tok in norms[c] for tok in ["responsible","attorney"])), None)
        if init_col is None:
            init_col = next((c for c in cols if "attorney" in norms[c]), None)
        if init_col is None and len(cols) > 4:
            init_col = cols[4]  # Column E

        # Find retained flag column
        prefer_flag = _norm("Retained With Consult (Y/N)")
        flag_col = next((c for c in cols if norms[c] == prefer_flag), None)
        if flag_col is None:
            flag_col = next((c for c in cols if all(tok in norms[c] for tok in ["retained","consult"])), None)
        if flag_col is None:
            flag_col = next((c for c in cols if "retained" in norms[c]), None)
        if flag_col is None and len(cols) > 5:
            flag_col = cols[5]  # Column F

        if not (date_col and init_col and flag_col):
            return {name: 0 for name in canon}

        t = ncl_df.copy()
        in_range = self._between_inclusive(t[date_col], sd, ed)
        kept = t[flag_col].astype(str).str.strip().str.upper().ne("N")
        m = in_range & kept

        def _ini_to_name(s: str) -> str:
            token = re.sub(r"[^A-Z]", "", str(s).upper())
            return INITIALS_TO_ATTORNEY.get(token, "Other") if token else "Other"

        mapped = t.loc[m, init_col].map(_ini_to_name)
        vc = mapped.value_counts(dropna=False)
        
        # Initialize all attorneys with 0, then update with actual counts
        result = {name: 0 for name in canon}
        for name, count in vc.items():
            if name in result:
                result[name] = int(count)
            else:
                # If attorney not in canon, add to "Other" count
                result["Other"] = result.get("Other", 0) + int(count)
        
        return result
    
    def _calculate_total_pncs_for_intake(self, data_manager, start_date: date, end_date: date) -> int:
        """Calculate total PNCs for intake report using same logic as conversion report"""
        # Leads & PNCs — batch period overlap (same logic as conversion report)
        if not data_manager.df_leads.empty and {"__batch_start","__batch_end"} <= set(data_manager.df_leads.columns):
            bs = pd.to_datetime(data_manager.df_leads["__batch_start"], errors="coerce")
            be = pd.to_datetime(data_manager.df_leads["__batch_end"],   errors="coerce")
            start_ts, end_ts = pd.Timestamp(start_date), pd.Timestamp(end_date)
            leads_in_range = (bs <= end_ts) & (be >= start_ts)
        else:
            leads_in_range = pd.Series(False, index=data_manager.df_leads.index)
        
        return int(
            data_manager.df_leads.loc[
                leads_in_range &
                (~data_manager.df_leads["Stage"].astype(str).str.strip().isin(EXCLUDED_PNC_STAGES))
            ].shape[0]
        ) if not data_manager.df_leads.empty and "Stage" in data_manager.df_leads.columns else 0
    
    def _intake_pncs_by_specialist(self, df_leads: pd.DataFrame, specialist: str, start_date: date, end_date: date) -> int:
        """Row 1: PNCs that the intake specialist did intake for"""
        if df_leads.empty or "Stage" not in df_leads.columns:
            return 0
        
        # Filter by date range (using batch period overlap logic)
        if not df_leads.empty and {"__batch_start","__batch_end"} <= set(df_leads.columns):
            bs = pd.to_datetime(df_leads["__batch_start"], errors="coerce")
            be = pd.to_datetime(df_leads["__batch_end"], errors="coerce")
            start_ts, end_ts = pd.Timestamp(start_date), pd.Timestamp(end_date)
            leads_in_range = (bs <= end_ts) & (be >= start_ts)
        else:
            leads_in_range = pd.Series(False, index=df_leads.index)
        
        # Find Assigned Intake Specialist column
        intake_col = self._find_col(df_leads, ["Assigned Intake Specialist"])
        if not intake_col:
            return 0
        
        # Filter by stage and intake specialist
        valid_stage = ~df_leads["Stage"].astype(str).str.strip().isin(EXCLUDED_PNC_STAGES)
        if specialist == "Everyone Else":
            valid_intake = ~df_leads[intake_col].astype(str).str.strip().isin(INTAKE_SPECIALISTS)
        else:
            valid_intake = df_leads[intake_col].astype(str).str.strip().eq(specialist)
        
        return int((leads_in_range & valid_stage & valid_intake).sum())
    
    def _intake_retained_without_consult(self, df_ncl: pd.DataFrame, specialist: str, start_date: date, end_date: date) -> int:
        """Row 3: PNCs who retained without consultation for this intake specialist"""
        if df_ncl.empty:
            return 0
        
        # Use same robust column detection as practice area section
        def _norm(s: str) -> str:
            s = str(s).lower().strip()
            s = re.sub(r"[\s_]+"," ", s)
            s = re.sub(r"[^a-z0-9 ]","", s)
            return s
        
        cols = list(df_ncl.columns)
        norms = {c: _norm(c) for c in cols}
        
        # Find date column
        prefer_date = _norm("Date we had BOTH the signed CLA and full payment")
        date_col = next((c for c in cols if norms[c] == prefer_date), None)
        if date_col is None:
            cands = [c for c in cols if all(tok in norms[c] for tok in ["date","signed","payment"])]
            if cands:
                cands.sort(key=lambda c: len(norms[c]))
                date_col = cands[0]
        if date_col is None:
            date_col = next((c for c in cols if "date" in norms[c]), None)
        if date_col is None and len(cols) > 6:
            date_col = cols[6]  # Column G
        
        # Find retained flag column
        prefer_flag = _norm("Retained With Consult (Y/N)")
        flag_col = next((c for c in cols if norms[c] == prefer_flag), None)
        if flag_col is None:
            flag_col = next((c for c in cols if all(tok in norms[c] for tok in ["retained","consult"])), None)
        if flag_col is None:
            flag_col = next((c for c in cols if "retained" in norms[c]), None)
        if flag_col is None and len(cols) > 5:
            flag_col = cols[5]  # Column F
        
        # Find Primary Intake column
        intake_col = next((c for c in cols if all(tok in norms[c] for tok in ["primary","intake"])), None)
        if intake_col is None:
            intake_col = next((c for c in cols if "intake" in norms[c]), None)
        if intake_col is None and len(cols) > 9:
            intake_col = cols[9]  # Column J
        
        if not (date_col and flag_col and intake_col):
            return 0
        
        # Filter by date range and retained flag = "N"
        in_range = self._between_inclusive(df_ncl[date_col], start_date, end_date)
        retained_without = df_ncl[flag_col].astype(str).str.strip().str.upper().eq("N")
        
        # Filter by intake specialist
        if specialist == "Everyone Else":
            valid_intake = ~df_ncl[intake_col].astype(str).str.strip().isin(INTAKE_INITIALS_TO_NAME.keys())
        else:
            # Find initials for this specialist
            specialist_initials = next((init for init, name in INTAKE_INITIALS_TO_NAME.items() if name == specialist), None)
            if specialist_initials:
                valid_intake = df_ncl[intake_col].astype(str).str.strip().eq(specialist_initials)
            else:
                valid_intake = pd.Series(False, index=df_ncl.index)
        
        return int((in_range & retained_without & valid_intake).sum())
    
    def _intake_scheduled_consult(self, df_init: pd.DataFrame, df_disc: pd.DataFrame, specialist: str, start_date: date, end_date: date) -> int:
        """Row 4: PNCs who scheduled consultation for this intake specialist"""
        total = 0
        
        # Initial Consultation
        if not df_init.empty:
            # Find Assigned Intake Specialist column
            intake_col = self._find_col(df_init, ["Assigned Intake Specialist"])
            if intake_col:
                # Use same logic as main conversion report for scheduled
                sub_col = self._find_col(df_init, ["Sub Status"])
                in_scope = df_init.copy()
                if sub_col and sub_col in in_scope.columns:
                    in_scope = in_scope.loc[~in_scope[sub_col].astype(str).str.strip().str.lower().eq("follow up")].copy()
                
                # Filter by intake specialist
                if specialist == "Everyone Else":
                    valid_intake = ~in_scope[intake_col].astype(str).str.strip().isin(INTAKE_SPECIALISTS)
                else:
                    valid_intake = in_scope[intake_col].astype(str).str.strip().eq(specialist)
                
                total += int(valid_intake.sum())
        
        # Discovery Meeting
        if not df_disc.empty:
            # Find Assigned Intake Specialist column
            intake_col = self._find_col(df_disc, ["Assigned Intake Specialist"])
            if intake_col:
                # Use same logic as main conversion report for scheduled
                sub_col = self._find_col(df_disc, ["Sub Status"])
                in_scope = df_disc.copy()
                if sub_col and sub_col in in_scope.columns:
                    in_scope = in_scope.loc[~in_scope[sub_col].astype(str).str.strip().str.lower().eq("follow up")].copy()
                
                # Filter by intake specialist
                if specialist == "Everyone Else":
                    valid_intake = ~in_scope[intake_col].astype(str).str.strip().isin(INTAKE_SPECIALISTS)
                else:
                    valid_intake = in_scope[intake_col].astype(str).str.strip().eq(specialist)
                
                total += int(valid_intake.sum())
        
        return total
    
    def _intake_showed_consult(self, df_init: pd.DataFrame, df_disc: pd.DataFrame, specialist: str, start_date: date, end_date: date) -> int:
        """Row 6: PNCs who showed up for consultation for this intake specialist"""
        total = 0
        
        # Initial Consultation
        if not df_init.empty:
            # Use same logic as practice area section for "met with"
            if df_init.shape[1] >= 13:
                att, dtc, sub, rsn = df_init.columns[11], df_init.columns[12], df_init.columns[6], df_init.columns[8]
                t = df_init.copy()
                m = self._between_inclusive(t[dtc], start_date, end_date)
                m &= ~t[sub].astype(str).str.strip().str.lower().eq("follow up")
                # Exclude rows where reason contains "Canceled Meeting" or "No Show"
                reason_str = t[rsn].astype(str).str.strip().str.lower()
                m &= ~reason_str.str.contains("canceled meeting", na=False)
                m &= ~reason_str.str.contains("no show", na=False)
                
                # Filter by intake specialist
                intake_col = self._find_col(df_init, ["Assigned Intake Specialist"])
                if intake_col:
                    if specialist == "Everyone Else":
                        valid_intake = ~t[intake_col].astype(str).str.strip().isin(INTAKE_SPECIALISTS)
                    else:
                        valid_intake = t[intake_col].astype(str).str.strip().eq(specialist)
                    m &= valid_intake
                
                total += int(m.sum())
        
        # Discovery Meeting
        if not df_disc.empty:
            # Use same logic as practice area section for "met with"
            if df_disc.shape[1] >= 16:
                att, dtc, sub, rsn = df_disc.columns[11], df_disc.columns[15], df_disc.columns[6], df_disc.columns[8]
                t = df_disc.copy()
                m = self._between_inclusive(t[dtc], start_date, end_date)
                m &= ~t[sub].astype(str).str.strip().str.lower().eq("follow up")
                # Exclude rows where reason contains "Canceled Meeting" or "No Show"
                reason_str = t[rsn].astype(str).str.strip().str.lower()
                m &= ~reason_str.str.contains("canceled meeting", na=False)
                m &= ~reason_str.str.contains("no show", na=False)
                
                # Filter by intake specialist
                intake_col = self._find_col(df_disc, ["Assigned Intake Specialist"])
                if intake_col:
                    if specialist == "Everyone Else":
                        valid_intake = ~t[intake_col].astype(str).str.strip().isin(INTAKE_SPECIALISTS)
                    else:
                        valid_intake = t[intake_col].astype(str).str.strip().eq(specialist)
                    m &= valid_intake
                
                total += int(m.sum())
        
        return total
    
    def _intake_retained_after_consult(self, df_ncl: pd.DataFrame, specialist: str, start_date: date, end_date: date) -> int:
        """Row 8: PNCs retained after scheduled consultation for this intake specialist"""
        if df_ncl.empty:
            return 0
        
        # Use same robust column detection as above
        def _norm(s: str) -> str:
            s = str(s).lower().strip()
            s = re.sub(r"[\s_]+"," ", s)
            s = re.sub(r"[^a-z0-9 ]","", s)
            return s
        
        cols = list(df_ncl.columns)
        norms = {c: _norm(c) for c in cols}
        
        # Find date column
        prefer_date = _norm("Date we had BOTH the signed CLA and full payment")
        date_col = next((c for c in cols if norms[c] == prefer_date), None)
        if date_col is None:
            cands = [c for c in cols if all(tok in norms[c] for tok in ["date","signed","payment"])]
            if cands:
                cands.sort(key=lambda c: len(norms[c]))
                date_col = cands[0]
        if date_col is None:
            date_col = next((c for c in cols if "date" in norms[c]), None)
        if date_col is None and len(cols) > 6:
            date_col = cols[6]  # Column G
        
        # Find retained flag column
        prefer_flag = _norm("Retained With Consult (Y/N)")
        flag_col = next((c for c in cols if norms[c] == prefer_flag), None)
        if flag_col is None:
            flag_col = next((c for c in cols if all(tok in norms[c] for tok in ["retained","consult"])), None)
        if flag_col is None:
            flag_col = next((c for c in cols if "retained" in norms[c]), None)
        if flag_col is None and len(cols) > 5:
            flag_col = cols[5]  # Column F
        
        # Find Primary Intake column
        intake_col = next((c for c in cols if all(tok in norms[c] for tok in ["primary","intake"])), None)
        if intake_col is None:
            intake_col = next((c for c in cols if "intake" in norms[c]), None)
        if intake_col is None and len(cols) > 9:
            intake_col = cols[9]  # Column J
        
        if not (date_col and flag_col and intake_col):
            return 0
        
        # Filter by date range and retained flag != "N"
        in_range = self._between_inclusive(df_ncl[date_col], start_date, end_date)
        retained_after = df_ncl[flag_col].astype(str).str.strip().str.upper().ne("N")
        
        # Filter by intake specialist
        if specialist == "Everyone Else":
            valid_intake = ~df_ncl[intake_col].astype(str).str.strip().isin(INTAKE_INITIALS_TO_NAME.keys())
        else:
            # Find initials for this specialist
            specialist_initials = next((init for init, name in INTAKE_INITIALS_TO_NAME.items() if name == specialist), None)
            if specialist_initials:
                valid_intake = df_ncl[intake_col].astype(str).str.strip().eq(specialist_initials)
            else:
                valid_intake = pd.Series(False, index=df_ncl.index)
        
        return int((in_range & retained_after & valid_intake).sum())
    
    def _intake_total_retained(self, df_ncl: pd.DataFrame, specialist: str, start_date: date, end_date: date) -> int:
        """Row 10: Total PNCs who retained for this intake specialist"""
        # This should equal Row 3 + Row 8
        return self._intake_retained_without_consult(df_ncl, specialist, start_date, end_date) + self._intake_retained_after_consult(df_ncl, specialist, start_date, end_date)
    
    def _calculate_conversion_metrics(self, data_manager, start_date: date, end_date: date) -> Optional[Dict]:
        """Calculate conversion metrics for the given period from actual data"""
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # Get date columns - safely check if dataframes exist
        leads_date_col = None
        if hasattr(data_manager, 'df_leads') and not data_manager.df_leads.empty:
            leads_date_col = self._find_date_column(data_manager.df_leads)
        
        ic_date_col = None
        if hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty:
            ic_date_col = self._find_date_column(data_manager.df_ic)
        
        dm_date_col = None
        if hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty:
            dm_date_col = self._find_date_column(data_manager.df_dm)
        
        ncl_date_col = None
        if hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty:
            ncl_date_col = self._find_date_column(data_manager.df_ncl)
        
        # Filter data by date range
        leads_count = 0
        if leads_date_col and hasattr(data_manager, 'df_leads') and not data_manager.df_leads.empty:
            leads_mask = self._mask_by_range_dates(data_manager.df_leads, leads_date_col, start_date, end_date)
            leads_count = leads_mask.sum()
        
        consultations_count = 0
        if ic_date_col and hasattr(data_manager, 'df_ic') and not data_manager.df_ic.empty:
            ic_mask = self._mask_by_range_dates(data_manager.df_ic, ic_date_col, start_date, end_date)
            consultations_count = ic_mask.sum()
        
        discovery_count = 0
        if dm_date_col and hasattr(data_manager, 'df_dm') and not data_manager.df_dm.empty:
            dm_mask = self._mask_by_range_dates(data_manager.df_dm, dm_date_col, start_date, end_date)
            discovery_count = dm_mask.sum()
        
        retained_count = 0
        if ncl_date_col and hasattr(data_manager, 'df_ncl') and not data_manager.df_ncl.empty:
            ncl_mask = self._mask_by_range_dates(data_manager.df_ncl, ncl_date_col, start_date, end_date)
            retained_count = ncl_mask.sum()
        
        # Calculate conversion rate
        conversion_rate = (retained_count / leads_count * 100) if leads_count > 0 else 0
        
        return {
            'leads': leads_count,
            'consultations': consultations_count,
            'discovery_meetings': discovery_count,
            'retained': retained_count,
            'conversion_rate': round(conversion_rate, 1)
        }
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the most likely date column in a dataframe"""
        if df is None or df.empty:
            return None
        
        date_candidates = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['date', 'created', 'updated', 'time']):
                date_candidates.append(col)
        
        if date_candidates:
            return date_candidates[0]
        return None
    
    def _mask_by_range_dates(self, df: pd.DataFrame, date_col: str, start: date, end: date) -> pd.Series:
        """Create mask for date range filtering with robust date parsing"""
        if df is None or df.empty or date_col not in df.columns:
            return pd.Series([False] * (0 if df is None else len(df)))
        
        # Use robust date parsing with format specification to avoid warnings
        ts = pd.to_datetime(df[date_col], errors="coerce", format="mixed")
        if ts.isna().any():
            y = ts.copy()
            for fmt in ("%m/%d/%Y %I:%M %p", "%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M", "%m/%d/%Y"):
                m = y.isna()
                if not m.any(): 
                    break
                try:
                    y.loc[m] = pd.to_datetime(df[date_col].loc[m], format=fmt, errors="coerce")
                except Exception:
                    pass
            ts = y
        
        # Handle NaT values properly
        valid_dates = ts.notna()
        in_range = pd.Series([False] * len(df), index=df.index)
        if valid_dates.any():
            in_range.loc[valid_dates] = (ts.loc[valid_dates].dt.date >= start) & (ts.loc[valid_dates].dt.date <= end)
        return in_range
    
    def _get_practice_area_metrics_for_report(self, data_manager, start_date: date, end_date: date) -> Optional[Dict]:
        """Get practice area metrics for the report"""
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # Get date columns
        leads_date_col = self._find_date_column(data_manager.df_leads)
        ncl_date_col = self._find_date_column(data_manager.df_ncl)
        
        # Filter data by date range
        leads_count = 0
        if leads_date_col and not data_manager.df_leads.empty:
            leads_mask = self._mask_by_range_dates(data_manager.df_leads, leads_date_col, start_date, end_date)
            leads_count = leads_mask.sum()
        
        retained_count = 0
        if ncl_date_col and not data_manager.df_ncl.empty:
            ncl_mask = self._mask_by_range_dates(data_manager.df_ncl, ncl_date_col, start_date, end_date)
            retained_count = ncl_mask.sum()
        
        # For now, return sample data structure
        # In a real implementation, this would aggregate by practice area
        return {
            'Practice Area': ['Personal Injury', 'Medical Malpractice', 'Workers Comp', 'Other'],
            'Cases': [45, 32, 28, 15],
            'Conversion Rate': [18.5, 22.1, 16.8, 12.3]
        }
    
    def _get_intake_specialist_metrics_for_report(self, data_manager, start_date: date, end_date: date) -> Optional[Dict]:
        """Get intake specialist metrics for the report"""
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # Get date columns
        leads_date_col = self._find_date_column(data_manager.df_leads)
        ncl_date_col = self._find_date_column(data_manager.df_ncl)
        
        # Filter data by date range
        leads_count = 0
        if leads_date_col and not data_manager.df_leads.empty:
            leads_mask = self._mask_by_range_dates(data_manager.df_leads, leads_date_col, start_date, end_date)
            leads_count = leads_mask.sum()
        
        retained_count = 0
        if ncl_date_col and not data_manager.df_ncl.empty:
            ncl_mask = self._mask_by_range_dates(data_manager.df_ncl, ncl_date_col, start_date, end_date)
            retained_count = ncl_mask.sum()
        
        # For now, return sample data structure
        # In a real implementation, this would aggregate by intake specialist
        return {
            'Intake Specialist': ['Rebecca', 'Jennifer', 'Everyone Else'],
            'Cases': [65, 48, 32],
            'Conversion Rate': [20.3, 18.7, 15.2]
        }
    
    def _render_conversion_funnel(self, conversion_data: Dict):
        """Render conversion funnel chart"""
        stages = ['Leads', 'Consultations', 'Discovery Meetings', 'Retained']
        values = [
            conversion_data.get('leads', 0),
            conversion_data.get('consultations', 0),
            conversion_data.get('discovery_meetings', 0),
            conversion_data.get('retained', 0)
        ]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial"
        ))
        
        fig.update_layout(
            title="Conversion Funnel",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_practice_area_comparison(self, practice_data: Dict):
        """Render practice area comparison chart"""
        fig = px.bar(x=practice_data['Practice Area'], y=practice_data['Cases'],
                    title='Cases by Practice Area',
                    labels={'x': 'Practice Area', 'y': 'Number of Cases'},
                    color=practice_data['Cases'],
                    color_continuous_scale='viridis')
        
        fig.update_layout(
            xaxis_title="Practice Area",
            yaxis_title="Number of Cases",
            height=400,
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_intake_specialist_performance(self, intake_data: Dict):
        """Render intake specialist performance chart"""
        fig = px.bar(x=intake_data['Intake Specialist'], y=intake_data['Conversion Rate'],
                    title='Intake Specialist Conversion Rates',
                    labels={'x': 'Intake Specialist', 'y': 'Conversion Rate (%)'},
                    color=intake_data['Conversion Rate'],
                    color_continuous_scale='plasma')
        
        fig.update_layout(
            xaxis_title="Intake Specialist",
            yaxis_title="Conversion Rate (%)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _render_three_row_card(self, title_name: str, met: int, kept: int, pct: float):
        """Render a three-row card for attorney metrics"""
        rows = [
            (f"PNCs who met with {title_name}", f"{int(met)}"),
            (f"PNCs who met with {title_name} and retained", f"{int(kept)}"),
            (f"% of PNCs who met with {title_name} and retained", f"{int(round(pct))}%"),
        ]
        trs = "\n".join(
            f"<tr><td>{self._html_escape(k)}</td><td style='text-align:right'>{self._html_escape(v)}</td></tr>"
            for k, v in rows
        )
        html = """
<style>
.mini-kpi { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.mini-kpi th, .mini-kpi td { border: 1px solid #eee; padding: 8px 10px; }
.mini-kpi th { background: #fafafa; text-align: left; font-weight: 600; }
</style>
<table class="mini-kpi">
  <thead><tr><th>Metric</th><th>Value</th></tr></thead>
  <tbody>""" + trs + """</tbody>
</table>"""
        st.markdown(html, unsafe_allow_html=True)
    
    def _custom_weeks_for_month(self, year: int, month: int) -> List[Dict]:
        """Generate custom weeks for a month"""
        from calendar import monthrange
        
        last_day = monthrange(year, month)[1]
        start_month = date(year, month, 1)
        end_month = date(year, month, last_day)

        first_sunday = start_month + timedelta(days=(6 - start_month.weekday()))
        w1_end = min(first_sunday, end_month)
        weeks = [{"label": "Week 1", "start": start_month, "end": w1_end}]

        start = w1_end + timedelta(days=1)
        w = 2
        while start <= end_month:
            this_end = min(start + timedelta(days=6), end_month)
            weeks.append({"label": f"Week {w}", "start": start, "end": this_end})
            start = this_end + timedelta(days=1)
            w += 1
        return weeks
    
    def _met_counts_from_ic_dm_index(self, ic_df: pd.DataFrame, dm_df: pd.DataFrame,
                                    sd: date, ed: date) -> pd.Series:
        """Get met counts from IC and DM dataframes using index-based approach"""
        out = {}

        # Initial_Consultation: L(11)=Lead Attorney, M(12)=IC date, G(6)=Sub Status, I(8)=Reason
        if isinstance(ic_df, pd.DataFrame) and ic_df.shape[1] >= 13:
            att, dtc, sub, rsn = ic_df.columns[11], ic_df.columns[12], ic_df.columns[6], ic_df.columns[8]
            t = ic_df.copy()
            m = self._between_inclusive(t[dtc], sd, ed)
            m &= ~t[sub].astype(str).str.strip().str.lower().eq("follow up")
            # Exclude rows where reason contains "Canceled Meeting" or "No Show"
            reason_str = t[rsn].astype(str).str.strip().str.lower()
            m &= ~reason_str.str.contains("canceled meeting", na=False)
            m &= ~reason_str.str.contains("no show", na=False)
            vc = t.loc[m, att].astype(str).str.strip().value_counts(dropna=False)
            for k, v in vc.items():
                if k:
                    out[k] = out.get(k, 0) + int(v)

        # Discovery_Meeting: L(11)=Lead Attorney, P(15)=DM date, G(6)=Sub Status, I(8)=Reason
        if isinstance(dm_df, pd.DataFrame) and dm_df.shape[1] >= 16:
            att, dtc, sub, rsn = dm_df.columns[11], dm_df.columns[15], dm_df.columns[6], dm_df.columns[8]
            t = dm_df.copy()
            m = self._between_inclusive(t[dtc], sd, ed)
            m &= ~t[sub].astype(str).str.strip().str.lower().eq("follow up")
            # Exclude rows where reason contains "Canceled Meeting" or "No Show"
            reason_str = t[rsn].astype(str).str.strip().str.lower()
            m &= ~reason_str.str.contains("canceled meeting", na=False)
            m &= ~reason_str.str.contains("no show", na=False)
            vc = t.loc[m, att].astype(str).str.strip().value_counts(dropna=False)
            for k, v in vc.items():
                if k:
                    out[k] = out.get(k, 0) + int(v)

        return pd.Series(out, dtype=int)
    
    def _retained_counts_from_ncl(self, ncl_df: pd.DataFrame, sd: date, ed: date) -> Dict[str, int]:
        """Get retained counts from NCL dataframe"""
        if not isinstance(ncl_df, pd.DataFrame) or ncl_df.empty:
            return {name: 0 for name in CANON}

        def _norm(s: str) -> str:
            s = str(s).lower().strip()
            s = re.sub(r"[\s_]+"," ", s)
            s = re.sub(r"[^a-z0-9 ]","", s)
            return s

        cols = list(ncl_df.columns)
        norms = {c: _norm(c) for c in cols}

        # Find date column
        prefer_date = _norm("Date we had BOTH the signed CLA and full payment")
        date_col = next((c for c in cols if norms[c] == prefer_date), None)
        if date_col is None:
            cands = [c for c in cols if all(tok in norms[c] for tok in ["date","signed","payment"])]
            if cands:
                cands.sort(key=lambda c: len(norms[c]))
                date_col = cands[0]
        if date_col is None:
            date_col = next((c for c in cols if "date" in norms[c]), None)
        if date_col is None and len(cols) > 6:
            date_col = cols[6]  # Column G

        # Find responsible attorney column
        init_col = next((c for c in cols if all(tok in norms[c] for tok in ["responsible","attorney"])), None)
        if init_col is None:
            init_col = next((c for c in cols if "attorney" in norms[c]), None)
        if init_col is None and len(cols) > 4:
            init_col = cols[4]  # Column E

        # Find retained flag column
        prefer_flag = _norm("Retained With Consult (Y/N)")
        flag_col = next((c for c in cols if norms[c] == prefer_flag), None)
        if flag_col is None:
            flag_col = next((c for c in cols if all(tok in norms[c] for tok in ["retained","consult"])), None)
        if flag_col is None:
            flag_col = next((c for c in cols if "retained" in norms[c]), None)
        if flag_col is None and len(cols) > 5:
            flag_col = cols[5]  # Column F

        if not (date_col and init_col and flag_col):
            return {name: 0 for name in CANON}

        t = ncl_df.copy()
        in_range = self._between_inclusive(t[date_col], sd, ed)
        kept = t[flag_col].astype(str).str.strip().str.upper().ne("N")
        m = in_range & kept

        def _ini_to_name(s: str) -> str:
            token = re.sub(r"[^A-Z]", "", str(s).upper())
            return INITIALS_TO_ATTORNEY.get(token, "Other") if token else "Other"

        mapped = t.loc[m, init_col].map(_ini_to_name)
        vc = mapped.value_counts(dropna=False)
        
        # Initialize all attorneys with 0, then update with actual counts
        result = {name: 0 for name in CANON}
        for name, count in vc.items():
            if name in result:
                result[name] = int(count)
            else:
                # If attorney not in CANON, add to "Other" count
                result["Other"] = result.get("Other", 0) + int(count)
        
        return result
