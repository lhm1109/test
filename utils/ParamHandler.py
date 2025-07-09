import streamlit as st
import os

# Get environment variables with fallback to query params
def get_config():
    return {
        "mapi_key": st.query_params.get("mapiKey", "") or os.getenv("MAPI_KEY"),
        "redirect_to": st.query_params.get("redirectTo", "") or os.getenv("REDIRECT_TO")
    }

class ParamHandler:
    params = st.query_params
    config = get_config()
    mapi_key = config["mapi_key"]
    base_url = config['redirect_to']