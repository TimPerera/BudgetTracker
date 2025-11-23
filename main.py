import streamlit as st

from utils import load_saved_data
from tabs.data_tab import render_data_tab, load_data, load_metrics
from tabs.settings_tab import render_settings_tab

cfg = load_saved_data()
session = st.session_state

if 'categories' not in st.session_state:
    st.session_state.categories = cfg.get('categories', 'Unknown')

def app(file_paths=None):
    st.set_page_config(layout='wide')
    st.title('Budget Tracker')
    session.data = load_data(file_paths, cfg, session)
    dash_tab, data_tab, settings_tab = st.tabs(['Dashboard','Data','Settings'])
        
    with data_tab:
        render_data_tab(session.data, cfg, session)
        
    with settings_tab:
        render_settings_tab(cfg, session)

    with dash_tab:
        income_col, expense_col, savings_col, net_col, num_transactions_col = st.columns(5)
        metrics = load_metrics(session.data)
        with income_col:
            income = metrics.get('income','N/A')
            st.metric('Total Income', f'${income:,.2f}')
        with expense_col:
            expense = metrics.get('expense','N/A')
            st.metric('Total Expenses', f'${expense:,.2f}')
        with savings_col:
            saving = metrics.get('saving','N/A')
            st.metric('Total Savings',f'${saving:,.2f}')
        with net_col:
            net = metrics.get('net','N/A')
            st.metric('Net Income', f'${net:,.2f}')       
        with num_transactions_col:
            count = metrics.get('count','N/A')
            st.metric('Total Transactions', f'{count:,}')

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

    