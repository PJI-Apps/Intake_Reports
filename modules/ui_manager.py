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
                    st.info("Wipe functionality would be implemented here")
    
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
                             replace_leads, replace_init, replace_disc, replace_ncl)
    
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
                         replace_leads, replace_init, replace_disc, replace_ncl):
        """Process all file uploads"""
        # Import and use the upload processor
        from .upload_processor import UploadProcessor
        
        upload_processor = UploadProcessor(data_manager, batch_manager)
        upload_processor.process_all_uploads(
            calls_uploader, up_leads, up_init, up_disc, up_ncl,
            calls_period_key, upload_start, upload_end, force_replace_calls,
            replace_leads, replace_init, replace_disc, replace_ncl
        )
    
    def render_calls_report(self, data_manager):
        """Render the calls report section"""
        st.markdown("---")
        st.header("📞 Zoom Call Reports")
        
        with st.expander("📞 Calls Report", expanded=False):
            st.subheader("Filters — Calls")
        
        # Get available months
        all_months = self._get_available_months(data_manager.df_calls)
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
        
        cat_choices = ["All"] + (sorted(data_manager.df_calls["Category"].unique().tolist()) 
                                if not data_manager.df_calls.empty else [])
        sel_cat = c3.selectbox("Category", cat_choices, index=0)
        base = data_manager.df_calls if sel_cat == "All" else data_manager.df_calls[data_manager.df_calls["Category"] == sel_cat]
        name_choices = ["All"] + (sorted(base["Name"].unique().tolist()) if not base.empty else [])
        sel_name = c4.selectbox("Name", name_choices, index=0)
        
        # Filter data
        filtered_calls = self._filter_calls_data(data_manager.df_calls, sel_year, sel_month_name, sel_cat, sel_name)
        
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
        # This would call the visualization manager
        st.info("Calls visualizations would be rendered here")
    
    def _get_available_months(self, df_calls: pd.DataFrame) -> list:
        """Get available months from calls data"""
        if isinstance(df_calls, pd.DataFrame) and not df_calls.empty and "Month-Year" in df_calls.columns:
            return sorted(set(df_calls["Month-Year"].dropna().astype(str)))
        return []
    
    def _filter_calls_data(self, df_calls: pd.DataFrame, sel_year: str, sel_month_name: str, 
                          sel_cat: str, sel_name: str) -> pd.DataFrame:
        """Filter calls data based on selected criteria"""
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
        
        return filtered_calls.loc[mask_calls_extra].copy()
    
    def render_conversion_report(self, data_manager):
        """Render the conversion report section"""
        st.markdown("---")
        st.header("📊 Firm Conversion Report")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today().replace(day=1),
                key="conv_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=date.today(),
                key="conv_end_date"
            )
        
        if start_date > end_date:
            st.error("Start date must be on or before end date.")
            return
        
        st.caption(f"Showing Conversion metrics for **{start_date.strftime('%-d %b %Y')} → {end_date.strftime('%-d %b %Y')}**")
        
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # Calculate conversion metrics
        conversion_data = self._calculate_conversion_metrics(data_manager, start_date, end_date)
        
        if not conversion_data:
            st.info("No conversion data available for the selected period.")
            return
        
        # Display conversion funnel
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Leads", conversion_data['leads'])
        
        with col2:
            st.metric("Consultations", conversion_data['consultations'])
        
        with col3:
            st.metric("Discovery Meetings", conversion_data['discovery_meetings'])
        
        with col4:
            st.metric("Retained", conversion_data['retained'])
        
        # Conversion rate
        st.metric("Overall Conversion Rate", f"{conversion_data['conversion_rate']}%")
        
        # Show detailed breakdown
        with st.expander("📊 Detailed Conversion Breakdown", expanded=False):
            self._render_conversion_funnel(conversion_data)
    
    def render_practice_area_report(self, data_manager):
        """Render the practice area report section"""
        st.header("📊 Practice Area")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today().replace(day=1),
                key="practice_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=date.today(),
                key="practice_end_date"
            )
        
        if start_date > end_date:
            st.error("Start date must be on or before end date.")
            return
        
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # Get practice area metrics
        practice_data = self._get_practice_area_metrics_for_report(data_manager, start_date, end_date)
        
        if not practice_data:
            st.info("No practice area data available for the selected period.")
            return
        
        # Display practice area metrics
        st.subheader("Practice Area Performance")
        
        # Create a DataFrame for display
        practice_df = pd.DataFrame(practice_data)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Cases", practice_df['Cases'].sum())
        
        with col2:
            avg_conversion = practice_df['Conversion Rate'].mean()
            st.metric("Average Conversion Rate", f"{avg_conversion:.1f}%")
        
        with col3:
            best_practice = practice_df.loc[practice_df['Conversion Rate'].idxmax(), 'Practice Area']
            st.metric("Best Performing Area", best_practice)
        
        # Display practice area table
        st.dataframe(practice_df, use_container_width=True)
        
        # Show practice area comparison chart
        with st.expander("📊 Practice Area Comparison", expanded=False):
            self._render_practice_area_comparison(practice_data)
    
    def render_intake_report(self, data_manager):
        """Render the intake report section"""
        st.header("📊 Conversion Report: Intake")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today().replace(day=1),
                key="intake_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=date.today(),
                key="intake_end_date"
            )
        
        if start_date > end_date:
            st.error("Start date must be on or before end date.")
            return
        
        # Load data if not already loaded
        if not hasattr(data_manager, 'df_leads') or data_manager.df_leads.empty:
            data_manager.load_all_data()
        
        # Get intake specialist metrics
        intake_data = self._get_intake_specialist_metrics_for_report(data_manager, start_date, end_date)
        
        if not intake_data:
            st.info("No intake specialist data available for the selected period.")
            return
        
        # Display intake specialist metrics
        st.subheader("Intake Specialist Performance")
        
        # Create a DataFrame for display
        intake_df = pd.DataFrame(intake_data)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Cases", intake_df['Cases'].sum())
        
        with col2:
            avg_conversion = intake_df['Conversion Rate'].mean()
            st.metric("Average Conversion Rate", f"{avg_conversion:.1f}%")
        
        with col3:
            best_specialist = intake_df.loc[intake_df['Conversion Rate'].idxmax(), 'Intake Specialist']
            st.metric("Best Performing Specialist", best_specialist)
        
        # Display intake specialist table
        st.dataframe(intake_df, use_container_width=True)
        
        # Show intake specialist comparison chart
        with st.expander("📊 Intake Specialist Comparison", expanded=False):
            self._render_intake_specialist_performance(intake_data)
    
    def render_visualizations(self, data_manager, viz_manager):
        """Render the visualizations section"""
        st.markdown("---")
        st.header("📊 Conversion Trend Visualizations")
        
        # This would contain the visualization logic
        st.info("Visualization functionality would be implemented here")
    
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
