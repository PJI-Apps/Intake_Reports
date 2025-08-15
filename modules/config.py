# modules/config.py
# Configuration and constants for the PJI Law Reports application

import streamlit as st
from typing import Dict, List

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="PJI Law Reports", 
        page_icon="📈", 
        layout="wide"
    )

# Google Sheets configuration
TAB_NAMES = {
    "CALLS": "Call_Report_Master",
    "LEADS": "Leads_PNCs_Master",
    "INIT":  "Initial_Consultation_Master",
    "DISC":  "Discovery_Meeting_Master",
    "NCL":   "New_Client_List_Master",
}

TAB_FALLBACKS = {
    "CALLS": ["Zoom_Calls"],
    "LEADS": ["Leads_PNCs"],
    "INIT":  ["Initial_Consultation"],
    "DISC":  ["Discovery_Meeting"],
    "NCL":   ["New_Clients", "New Client List"],
}

# Calls processing configuration
REQUIRED_COLUMNS_CALLS: List[str] = [
    "Name", "Total Calls", "Completed Calls", "Outgoing", "Received",
    "Forwarded to Voicemail", "Answered by Other", "Missed",
    "Avg Call Time", "Total Call Time", "Total Hold Time"
]

ALLOWED_CALLS: List[str] = [
    "Anastasia Economopoulos", "Aneesah Shaik", "Azariah", "Chloe", "Donnay", "Earl",
    "Faeryal Sahadeo", "Kaithlyn", "Micayla Sam", "Nathanial Beneke", "Nobuhle",
    "Rialet", "Riekie Van Ellinckhuyzen", "Shaylin Steyn", "Sihle Gadu",
    "Thabang Tshubyane", "Tiffany",
]

CATEGORY_CALLS: Dict[str, str] = {
    "Anastasia Economopoulos": "Intake", "Aneesah Shaik": "Intake", "Azariah": "Intake", 
    "Chloe": "Intake IC", "Donnay": "Receptionist", "Earl": "Intake", 
    "Faeryal Sahadeo": "Intake", "Kaithlyn": "Intake", "Micayla Sam": "Intake", 
    "Nathanial Beneke": "Intake", "Nobuhle": "Intake IC", "Rialet": "Intake",
    "Riekie Van Ellinckhuyzen": "Receptionist", "Maria Van Ellinckhuyzen": "Receptionist",
    "Shaylin Steyn": "Receptionist", "Sihle Gadu": "Intake", 
    "Thabang Tshubyane": "Intake", "Tiffany": "Intake",
}

RENAME_NAME_CALLS = {"Riekie Van Ellinckhuyzen": "Maria Van Ellinckhuyzen"}

# Practice area configuration
PRACTICE_AREAS = {
    "Estate Planning": ["Connor Watkins", "Jennifer Fox", "Rebecca Megel"],
    "Estate Administration": [
        "Adam Hill", "Elias Kerby", "Elizabeth Ross", "Garrett Kizer",
        "Kyle Grabulis", "Sarah Kravetz", "Jamie Kliem", "Carter McClain",
    ],
    "Civil Litigation": [
        "Andrew Suddarth", "William Bang", "Bret Giaimo",
        "Hannah Supernor", "Laura Kouremetis", "Lukios Stefan", "William Gogoel"
    ],
    "Business transactional": ["Kevin Jaros"],
}

OTHER_ATTORNEYS = ["Robert Brown", "Justine Sennott", "Paul Abraham"]

DISPLAY_NAME_OVERRIDES = {
    "Elias Kerby": "Eli Kerby",
    "William Bang": "Billy Bang",
    "William Gogoel": "Will Gogoel",
    "Andrew Suddarth": "Andy Suddarth",
}

# Attorney initials mapping
INITIALS_TO_ATTORNEY = {
    "CW": "Connor Watkins", "JF": "Jennifer Fox", "RM": "Rebecca Megel",
    "AH": "Adam Hill", "EK": "Elias Kerby", "ER": "Elizabeth Ross",
    "GK": "Garrett Kizer", "KG": "Kyle Grabulis", "SK": "Sarah Kravetz",
    "AS": "Andrew Suddarth", "WB": "William Bang", "BG": "Bret Giaimo",
    "HS": "Hannah Supernor", "LK": "Laura Kouremetis", "LS": "Lukios Stefan",
    "WG": "William Gogoel", "KJ": "Kevin Jaros", "JK": "Jamie Kliem", 
    "CM": "Carter McClain", "RB": "Robert Brown", "JS": "Justine Sennott", 
    "PA": "Paul Abraham",
}

# Intake specialists configuration
INTAKE_SPECIALISTS = [
    "Anastasia Economopoulos", "Aneesah Shaik", "Azariah Pillay", "Chloe Lansdell",
    "Earl Michaels", "Faeryal Sahadeo", "Kaithlyn Maharaj", "Micayla Sam",
    "Nathanial Beneke", "Nobuhle Mnikathi", "Rialet van Heerden", "Sihle Gadu",
    "Thabang Tshubyane", "Tiffany Pillay"
]

INTAKE_INITIALS_TO_NAME = {
    "AE": "Anastasia Economopoulos", "AS": "Aneesah Shaik", "AP": "Azariah Pillay",
    "CL": "Chloe Lansdell", "EM": "Earl Michaels", "FS": "Faeryal Sahadeo",
    "KM": "Kaithlyn Maharaj", "MS": "Micayla Sam", "NB": "Nathanial Beneke",
    "NM": "Nobuhle Mnikathi", "RH": "Rialet van Heerden", "SG": "Sihle Gadu",
    "TT": "Thabang Tshubyane", "TP": "Tiffany Pillay"
}

# Excluded PNC stages
EXCLUDED_PNC_STAGES = {
    "Marketing/Scam/Spam (Non-Lead)", "Referred Out", "No Stage", "New Lead",
    "No Follow Up (No Marketing/Communication)", "No Follow Up (Receives Marketing/Communication)",
    "Anastasia E", "Aneesah S.", "Azariah P.", "Earl M.", "Faeryal S.", "Kaithlyn M.",
    "Micayla S.", "Nathanial B.", "Rialet v H.", "Sihle G.", "Thabang T.", "Tiffany P",
    ":Chloe L:", "Nobuhle M."
}

# Month mappings
MONTHS_MAP = {
    "01": "January", "02": "February", "03": "March", "04": "April", 
    "05": "May", "06": "June", "07": "July", "08": "August", 
    "09": "September", "10": "October", "11": "November", "12": "December"
}

MONTHS_MAP_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}
