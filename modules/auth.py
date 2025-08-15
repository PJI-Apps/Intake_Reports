# modules/auth.py
# Authentication module for PJI Law Reports application

import streamlit as st
import yaml
import streamlit_authenticator as stauth
from typing import Tuple, Optional

def setup_authentication():
    """Setup authentication configuration"""
    try:
        config = yaml.safe_load(st.secrets["auth_config"]["config"])
        authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            config.get("preauthorized", {}).get("emails", []),
        )
        return authenticator
    except Exception as e:
        st.error("Authentication is not configured correctly. Check your **Secrets**.")
        st.exception(e)
        st.stop()

def _login_compat(authenticator_obj):
    """Compatibility function for different versions of streamlit_authenticator"""
    # New API (0.4.x+)
    try:
        res = authenticator_obj.login(
            fields={"Form name": "Login", "Username": "Username", "Password": "Password"},
            location="main",
        )
        if isinstance(res, tuple) and len(res) == 3:
            return res
        if isinstance(res, dict):
            return res.get("name"), res.get("authentication_status"), res.get("username")
        if res is not None:
            return res
    except TypeError:
        pass
    except Exception:
        pass
    
    # Old API (0.3.2)
    try:
        return authenticator_obj.login("Login", "main")
    except TypeError:
        return authenticator_obj.login(form_name="Login", location="main")

def check_auth_status(authenticator) -> Tuple[Optional[str], Optional[bool], Optional[str]]:
    """Check authentication status and handle login/logout"""
    name, auth_status, username = _login_compat(authenticator)

    if auth_status is False:
        st.error("Username/password is incorrect")
        st.stop()
    elif auth_status is None:
        st.warning("Please enter your username and password")
        st.stop()
    else:
        with st.sidebar:
            authenticator.logout("Logout", "sidebar")
            st.caption(f"Signed in as **{name}**")
    
    return name, auth_status, username
