# modules/data_manager.py
# Data management module for Google Sheets operations and data processing

import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials
import gspread_dataframe as gd
import time
import re
import hashlib
import datetime as dt
from typing import Optional, Dict, Any, List, Tuple
from datetime import date, datetime, timedelta
from calendar import monthrange

from .config import TAB_NAMES, TAB_FALLBACKS, REQUIRED_COLUMNS_CALLS, ALLOWED_CALLS, CATEGORY_CALLS, RENAME_NAME_CALLS

class DataManager:
    """Manages data operations including Google Sheets connectivity and data processing"""
    
    def __init__(self):
        # Initialize session state first
        if "logs" not in st.session_state:
            st.session_state["logs"] = []
            
        if "gs_ver" not in st.session_state:
            st.session_state["gs_ver"] = 0
        
        self.gc = None
        self.gsheet = None
        self._initialize_google_sheets()
    
    def log(self, msg: str):
        """Add message to logs"""
        st.session_state["logs"].append(msg)
    
    def _initialize_google_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Get service account credentials
            sa = st.secrets.get("gcp_service_account", None)
            if not sa:
                self.log("Google Cloud service account not configured")
                return
                
            if "client_email" not in sa:
                raise ValueError("Service account object missing 'client_email'")
            
            # Get spreadsheet ID
            gs_config = st.secrets.get("google_sheets", None)
            if not gs_config or "spreadsheet_id" not in gs_config:
                self.log("Google Sheets spreadsheet ID not configured")
                return
                
            spreadsheet_id = gs_config["spreadsheet_id"]
                
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_info(sa, scopes=scopes)
            self.gc = gspread.authorize(creds)
            self.gsheet = self.gc.open_by_key(spreadsheet_id)
            self.log("Google Sheets connection established")
            
        except Exception as e:
            self.log(f"Failed to initialize Google Sheets: {e}")
    
    @st.cache_resource(show_spinner=False)
    def _get_gsheet_client_cached(self):
        """Cached Google Sheets client"""
        return self.gc, self.gsheet
    
    def _get_worksheet(self, title: str):
        """Get or create worksheet with fallback support"""
        if self.gsheet is None:
            return None

        # 1) Fast path: try fetching a few times (transient errors happen)
        for delay in (0.0, 0.6, 1.2):
            try:
                if delay:
                    time.sleep(delay)
                return self.gsheet.worksheet(title)
            except Exception:
                continue

        # 2) Fallback titles (legacy tab names)
        for fb in TAB_FALLBACKS.get(title, []):
            try:
                return self.gsheet.worksheet(fb)
            except Exception:
                continue

        # 3) Create only if truly absent
        try:
            self.gsheet.add_worksheet(title=title, rows=2000, cols=40)
            return self.gsheet.worksheet(title)
        except Exception:
            try:
                return self.gsheet.worksheet(title)
            except Exception:
                pass

        return None
    
    @st.cache_data(ttl=300, show_spinner=False)
    def _read_worksheet_cached(self, sheet_url: str, tab_title: str, ver: int) -> pd.DataFrame:
        """Cached worksheet reading"""
        try:
            ws = self._get_worksheet(tab_title)
            if ws is None:
                return pd.DataFrame()
            
            last_exc = None
            for delay in (0.0, 1.0, 2.0):
                try:
                    if delay: 
                        time.sleep(delay)
                    df = gd.get_as_dataframe(ws, evaluate_formulas=True, dtype=str)
                    last_exc = None
                    break
                except Exception as e:
                    last_exc = e
            
            if last_exc is not None:
                self.log(f"Read failed for '{tab_title}': {last_exc}")
                return pd.DataFrame()
            
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            
            # Convert date columns
            for c in df.columns:
                cl = c.lower()
                if ("date" in cl or "with pji law" in cl) and not cl.startswith("__batch"):
                    df[c] = pd.to_datetime(df[c], errors="coerce", format="mixed")
            
            return df.dropna(how="all").fillna("")
            
        except Exception as e:
            self.log(f"Failed to read worksheet {tab_title}: {e}")
            return pd.DataFrame()
    
    def read_worksheet_by_name(self, logical_key: str) -> pd.DataFrame:
        """Read worksheet by logical name"""
        if self.gsheet is None:
            return pd.DataFrame()
            
        ws = self._get_worksheet(TAB_NAMES[logical_key])
        if ws is None:
            return pd.DataFrame()
            
        try:
            sheet_url = st.secrets["master_store"]["sheet_url"]
            return self._read_worksheet_cached(sheet_url, ws.title, st.session_state["gs_ver"])
        except Exception as e:
            self.log(f"Read failed for '{ws.title}': {e}")
            return pd.DataFrame()
    
    def write_worksheet_by_name(self, logical_key: str, df: pd.DataFrame) -> bool:
        """Write DataFrame to worksheet"""
        ws = self._get_worksheet(TAB_NAMES[logical_key])
        if ws is None or df is None:
            return False
            
        try:
            ws.clear()
            gd.set_with_dataframe(ws, df.reset_index(drop=True), include_index=False, include_column_header=True)
            st.session_state["gs_ver"] += 1
            return True
        except Exception as e:
            self.log(f"Write failed for '{TAB_NAMES[logical_key]}': {e}")
            return False
    
    def load_all_data(self):
        """Load all data from Google Sheets"""
        self.df_calls = self.read_worksheet_by_name("CALLS")
        self.df_leads = self.read_worksheet_by_name("LEADS")
        self.df_init = self.read_worksheet_by_name("INIT")
        self.df_disc = self.read_worksheet_by_name("DISC")
        self.df_ncl = self.read_worksheet_by_name("NCL")
        
        # Process calls data if available
        if not self.df_calls.empty:
            self.df_calls["__avg_sec"] = pd.to_timedelta(self.df_calls["Avg Call Time"], errors="coerce").dt.total_seconds().fillna(0.0)
            self.df_calls["__total_sec"] = pd.to_timedelta(self.df_calls["Total Call Time"], errors="coerce").dt.total_seconds().fillna(0.0)
            self.df_calls["__hold_sec"] = pd.to_timedelta(self.df_calls["Total Hold Time"], errors="coerce").dt.total_seconds().fillna(0.0)
    
    def get_available_batches(self, sheet_name: str) -> list:
        """Get list of available batch IDs for a sheet"""
        try:
            current_data = self.read_worksheet_by_name(sheet_name)
            if current_data is None or current_data.empty or "__batch_id" not in current_data.columns:
                return []
            
            return sorted(current_data["__batch_id"].unique().tolist())
        except Exception:
            return []
    
    def remove_batch_from_sheet(self, sheet_name: str, batch_id: str) -> bool:
        """Remove all records with specific batch ID from a sheet"""
        try:
            current_data = self.read_worksheet_by_name(sheet_name)
            if current_data is None or current_data.empty:
                return True
            
            # Remove records with matching batch ID
            filtered_data = current_data[current_data["__batch_id"] != batch_id].copy()
            
            # Write back the filtered data
            success = self.write_worksheet_by_name(sheet_name, filtered_data)
            
            if success:
                removed_count = len(current_data) - len(filtered_data)
                st.success(f"Removed {removed_count} records with batch ID '{batch_id}' from {sheet_name}")
            
            return success
        except Exception as e:
            st.error(f"Failed to remove batch from {sheet_name}: {str(e)}")
            return False
    
    def sync_from_master_sheet(self, sheet_name: str) -> bool:
        """Sync data from master sheet (refresh after manual edits)"""
        try:
            current_data = self.read_worksheet_by_name(sheet_name)
            if current_data is not None and not current_data.empty:
                st.success(f"Successfully synced {len(current_data)} records from {sheet_name}")
                return True
            else:
                st.warning(f"No data found in {sheet_name}")
                return False
        except Exception as e:
            st.error(f"Failed to sync from {sheet_name}: {str(e)}")
            return False

    def _clean_datestr(self, x):
        """Clean date string by removing timezone and formatting"""
        if pd.isna(x):
            return x
        s = str(x).strip()
        s = re.sub(r"\s+at\s+", " ", s, flags=re.I)
        s = re.sub(r"\s+(ET|EDT|EST|CT|CDT|CST|MT|MDT|MST|PT|PDT)\b", "", s)
        return s

    def file_md5(self, uploaded_file) -> str:
        """Generate MD5 hash of uploaded file"""
        pos = uploaded_file.tell()
        uploaded_file.seek(0)
        data = uploaded_file.read()
        uploaded_file.seek(pos if pos is not None else 0)
        return hashlib.md5(data).hexdigest()

    def _fmt_hms(self, seconds: pd.Series) -> pd.Series:
        """Format seconds as HH:MM:SS"""
        return seconds.round().astype(int).map(lambda s: str(dt.timedelta(seconds=s)))

    def month_key_from_range(self, start: dt.date, end: dt.date) -> str:
        """Generate month key from date range"""
        return f"{start.year}-{start.month:02d}"

    def validate_single_month_range(self, start: dt.date, end: dt.date) -> Tuple[bool, str]:
        """Validate that date range is within a single month"""
        if start > end:
            return False, "Start date must be on or before End date."
        if (start.year, start.month) != (end.year, end.month):
            return False, "Please select a range within a single calendar month."
        return True, ""

    def process_calls_csv(self, raw: pd.DataFrame, period_key: str) -> pd.DataFrame:
        """Process calls CSV data with normalization and aggregation"""
        def norm(s: str) -> str:
            s = s.strip().lower()
            s = re.sub(r"[\s_]+"," ",s)
            s = re.sub(r"[^a-z0-9 ]","",s)
            return s
        
        raw.columns = [c.strip() for c in raw.columns]
        col_norm = {c: norm(c) for c in raw.columns}
        
        synonyms = {
            "Name":["name","user name","username","display name"],
            "Total Calls":["total calls","calls total","total number of calls","total call count","total"],
            "Completed Calls":["completed calls","completed","answered calls","handled calls","calls answered"],
            "Outgoing":["outgoing","outgoing calls","outbound","outbound calls"],
            "Received":["received","incoming","incoming calls"],
            "Forwarded to Voicemail":["forwarded to voicemail","to voicemail","voicemail forwarded","voicemail"],
            "Answered by Other":["answered by other","answered by others","answered by other member","answered by other user","answered by other extension"],
            "Missed":["missed","missed calls","abandoned","ring no answer"],
            "Avg Call Time":["avg call time","average call time","avg call duration","average call duration","avg talk time","average talk time"],
            "Total Call Time":["total call time","total call duration","total talk time"],
            "Total Hold Time":["total hold time","hold time total","total on hold"],
        }
        
        rename_map, used = {}, set()
        for canonical, alts in synonyms.items():
            for actual, n in col_norm.items():
                if actual in used: continue
                if n in alts:
                    rename_map[actual] = canonical
                    used.add(actual)
                    break
        
        df = raw.rename(columns=rename_map).copy()

        # Combine split incoming/outgoing if present
        def norm2(s: str) -> str:
            return re.sub(r"[^a-z0-9 ]","",re.sub(r"[\s_]+"," ",s.strip().lower()))
        
        incoming = [c for c in raw.columns if norm2(c) in {"incoming internal","incoming external","incoming"}]
        outgoing = [c for c in raw.columns if norm2(c) in {"outgoing internal","outgoing external","outgoing"}]
        
        if incoming:
            base = pd.to_numeric(df.get("Received", 0), errors="coerce").fillna(0)
            for c in incoming: 
                base += pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)
            df["Received"] = base
        
        if outgoing:
            base = pd.to_numeric(df.get("Outgoing", 0), errors="coerce").fillna(0)
            for c in outgoing: 
                base += pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)
            df["Outgoing"] = base

        missing = [c for c in REQUIRED_COLUMNS_CALLS if c not in df.columns]
        if missing:
            st.error("Calls CSV headers detected: " + ", ".join(list(raw.columns)))
            raise ValueError(f"Calls CSV is missing columns after normalization: {missing}")

        df = df[df["Name"].isin(ALLOWED_CALLS)].copy()
        df["Name"] = df["Name"].replace(RENAME_NAME_CALLS)
        df["Category"] = df["Name"].map(lambda n: CATEGORY_CALLS.get(n, "Other"))

        for c in ["Total Calls","Completed Calls","Outgoing","Received","Forwarded to Voicemail","Answered by Other","Missed"]:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

        df["_avg_sec"]   = pd.to_timedelta(df["Avg Call Time"], errors="coerce").dt.total_seconds().fillna(0.0)
        df["_total_sec"] = pd.to_timedelta(df["Total Call Time"], errors="coerce").dt.total_seconds().fillna(0.0)
        df["_hold_sec"]  = pd.to_timedelta(df["Total Hold Time"], errors="coerce").dt.total_seconds().fillna(0.0)
        df["Month-Year"] = period_key

        grouped = df.groupby(["Month-Year","Category","Name"], as_index=False).agg(
            {"Total Calls":"sum","Completed Calls":"sum","Outgoing":"sum","Received":"sum",
             "Forwarded to Voicemail":"sum","Answered by Other":"sum","Missed":"sum",
             "_total_sec":"sum","_hold_sec":"sum"}
        )
        
        totals = df.groupby(["Month-Year","Category","Name"], as_index=False).agg(
            total_calls_sum=("Total Calls","sum"),
            avg_weighted_sum=("_avg_sec", lambda s: (s * df.loc[s.index,"Total Calls"]).sum()),
        )
        totals["avg_sec_weighted"] = totals.apply(
            lambda r: (r["avg_weighted_sum"]/r["total_calls_sum"]) if r["total_calls_sum"]>0 else 0.0, axis=1)

        out = grouped.merge(
            totals[["Month-Year","Category","Name","avg_sec_weighted"]],
            on=["Month-Year","Category","Name"], how="left"
        )
        out["Avg Call Time"]   = self._fmt_hms(out["avg_sec_weighted"])
        out["Total Call Time"] = self._fmt_hms(out["_total_sec"])
        out["Total Hold Time"] = self._fmt_hms(out["_hold_sec"])

        out["__avg_sec"]   = out["avg_sec_weighted"]
        out["__total_sec"] = out["_total_sec"]
        out["__hold_sec"]  = out["_hold_sec"]

        out = out[["Category","Name","Total Calls","Completed Calls","Outgoing","Received",
                   "Forwarded to Voicemail","Answered by Other","Missed",
                   "Avg Call Time","Total Call Time","Total Hold Time","Month-Year",
                   "__avg_sec","__hold_sec","__total_sec"]].sort_values(["Category","Name"]).reset_index(drop=True)
        return out

    def _read_any(self, upload):
        """Read any supported file format (CSV, Excel)"""
        if upload is None: 
            return None
        
        name = (upload.name or "").lower()
        if name.endswith(".csv"):
            try: 
                df = pd.read_csv(upload)
            except Exception:
                upload.seek(0)
                df = pd.read_csv(upload, engine="python")
            df.columns = [str(c).strip() for c in df.columns]
            return df
        
        try:
            if name.endswith(".xlsx"):
                df = pd.read_excel(upload, engine="openpyxl")
            elif name.endswith(".xls"):
                df = pd.read_excel(upload, engine="xlrd")
            else:
                df = pd.read_excel(upload)
        except Exception:
            upload.seek(0)
            df = pd.read_excel(upload)
        
        df.columns = [str(c).strip() for c in df.columns]
        return df

    def _mask_by_range(self, df: pd.DataFrame, col: str, start_date: date, end_date: date) -> pd.Series:
        """Create mask for date range filtering"""
        s = pd.to_datetime(df[col], errors="coerce")
        return (s.dt.date >= start_date) & (s.dt.date <= end_date) & s.notna()

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

    def _month_bounds(self, year: int, month: int):
        """Get start and end dates for a month"""
        last_day = monthrange(year, month)[1]
        start = date(year, month, 1)
        end   = date(year, month, last_day)
        return start, end

    def _clamp_to_today(self, end_date: date) -> date:
        """Clamp end date to today"""
        today = date.today()
        return min(end_date, today)

    def custom_weeks_for_month(self, year: int, month: int):
        """Generate custom week definitions for a month"""
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
