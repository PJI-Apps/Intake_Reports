# modules/utils.py
# Utilities module for common helper functions

import re
import hashlib
import datetime as dt
from datetime import date, timedelta
from calendar import monthrange
from typing import List, Dict, Tuple, Optional
import pandas as pd

def clean_datestr(x):
    """Clean date string by removing timezone and formatting"""
    if pd.isna(x):
        return x
    s = str(x).strip()
    s = re.sub(r"\s+at\s+", " ", s, flags=re.I)
    s = re.sub(r"\s+(ET|EDT|EST|CT|CDT|CST|MT|MDT|MST|PT|PDT)\b", "", s)
    return s

def file_md5(uploaded_file) -> str:
    """Generate MD5 hash of uploaded file"""
    pos = uploaded_file.tell()
    uploaded_file.seek(0)
    data = uploaded_file.read()
    uploaded_file.seek(pos if pos is not None else 0)
    return hashlib.md5(data).hexdigest()

def month_key_from_range(start: dt.date, end: dt.date) -> str:
    """Generate month key from date range"""
    return f"{start.year}-{start.month:02d}"

def validate_single_month_range(start: dt.date, end: dt.date) -> Tuple[bool, str]:
    """Validate that date range is within a single month"""
    if start > end:
        return False, "Start date must be on or before End date."
    if (start.year, start.month) != (end.year, end.month):
        return False, "Please select a range within a single calendar month."
    return True, ""

def month_bounds(year: int, month: int) -> Tuple[date, date]:
    """Get start and end dates for a month"""
    last_day = monthrange(year, month)[1]
    start = date(year, month, 1)
    end = date(year, month, last_day)
    return start, end

def clamp_to_today(end_date: date) -> date:
    """Clamp end date to today if it's in the future"""
    today = date.today()
    return min(end_date, today)

def custom_weeks_for_month(year: int, month: int) -> List[Dict]:
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

def mask_by_range_dates(df: pd.DataFrame, date_col: str, start: date, end: date) -> pd.Series:
    """Create mask for dates within range"""
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

def find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Find a column by name (case-insensitive)"""
    if df is None or df.empty:
        return None
    cols = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        k = cand.lower().strip()
        if k in cols:
            return cols[k]
    return None

def read_any_file(upload):
    """Read any uploaded file (CSV, Excel)"""
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

def format_hms(seconds: pd.Series) -> pd.Series:
    """Format seconds as HH:MM:SS"""
    return seconds.round().astype(int).map(lambda s: str(dt.timedelta(seconds=s)))

def calculate_percentage(numer, denom) -> float:
    """Calculate percentage with safe division"""
    return 0 if (denom is None or denom == 0) else round((numer/denom)*100)

def html_escape(s: str) -> str:
    """Escape HTML characters"""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def normalize_string(s: str) -> str:
    """Normalize string for comparison"""
    s = s.strip().lower()
    s = re.sub(r"[\s_]+", " ", s)
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return s

def is_blank(series: pd.Series) -> pd.Series:
    """Check if series values are blank"""
    blank_tokens = {"", "nan", "none", "na", "null"}
    if not isinstance(series, pd.Series):
        return pd.Series([True])
    s = series.astype(str)
    return s.isna() | s.str.strip().eq("") | s.str.strip().str.lower().isin(blank_tokens)

def clean_datetime_text(x: str) -> str:
    """Clean datetime text for parsing"""
    if x is None:
        return ""
    
    s = str(x).replace("\xa0", " ").strip()  # NBSP → space
    s = s.replace("–", "-").replace(",", " ")
    s = re.sub(r"\s+at\s+", " ", s, flags=re.I)  # " at "
    s = re.sub(r"\s+(ET|EDT|EST|CT|CDT|CST|MT|MDT|MST|PT|PDT)\b", "", s, flags=re.I)  # drop trailing timezone tag
    s = re.sub(r"(\d)(am|pm)\b", r"\1 \2", s, flags=re.I)  # "12:45pm"→"12:45 pm"
    s = re.sub(r"\s+", " ", s).strip()
    return s

def to_timestamp(series: pd.Series) -> pd.Series:
    """Convert series to timestamp with robust parsing"""
    if not isinstance(series, pd.Series) or series.empty:
        return pd.to_datetime(pd.Series([], dtype=object))
    
    cleaned = series.astype(str).map(clean_datetime_text)
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

def between_inclusive(series: pd.Series, sd: date, ed: date) -> pd.Series:
    """Check if dates are between start and end dates (inclusive)"""
    ts = to_timestamp(series)
    return (ts.dt.date >= sd) & (ts.dt.date <= ed)
