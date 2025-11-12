import streamlit as st

from utils import load_saved_data
from tabs.data_tab import render_data_tab
from tabs.settings_tab import render_settings_tab

cfg = load_saved_data()
session = st.session_state

if 'categories' not in st.session_state:
    st.session_state.categories = cfg.get('categories', 'Unknown')

def app(file_paths=None):
    st.set_page_config(layout='wide')
    st.title('Budget Tracker')
    data_tab, settings_tab = st.tabs(['Data','Settings'])

    with data_tab:
        render_data_tab(file_paths, cfg, session)
    with settings_tab:
        render_settings_tab(cfg, session)
    
if __name__=='__main__':
    files = [
             'input/2866.csv', 
             'input/5060.csv',
             'input/6781.csv',
             'input/8558.csv',
             'input/9544.csv'
            ]
    
    if files:
        cleaned_data = app(files)
    else:
        cleaned_data = app()

    