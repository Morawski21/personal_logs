import os
import datetime as dt
import pandas as pd
from datetime import datetime
import streamlit as st

import src.config as config

def set_custom_page_config(title: str):
    st.set_page_config(
        page_title=title,
        layout="wide",
        page_icon="assets/icon.png"
    )