import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_float_dtype, is_object_dtype
import re

import streamlit as st

from categories import categorize_transactions, update_categories
from utils import logger

def render_data_tab(data, cfg, session):
    
    categories = session.categories
    # Load Data
    session.data = data.copy()
    # Load Filters
    modify = st.checkbox(label='Add Filters')
    modify_container = st.container()
    if modify:
        with modify_container:
            session.data = render_modify_container(data, session)
    # Display Data
    editable_df = st.data_editor(
                            session.data, 
                            column_config={
                                'Category': st.column_config.SelectboxColumn(
                                    'Category',
                                    help='Categorize a Transaction Type. Add more categories under settings', 
                                    options=categories, 
                                    default='Unknown'
                                    ), 
                                'Date Posted':st.column_config.DateColumn('Date Posted', format='YYYY-MM-DD')
                                })
    data_btn = st.button('Apply Changes')
    if data_btn: # User has chosen to apply changes in categories.
        mask = st.session_state.data['Category'] != editable_df['Category']
        for idx, row in editable_df[mask].iterrows():
            category, keyword = row['Category'], row['Description']
            if pd.isna(category):
                continue
            st.session_state.data.at[idx, 'Category'] = category
            update_categories(category, keyword, session, cfg)
            categorize_transactions(editable_df, session)
        st.rerun()
    return data

def load_data(file_paths, cfg, session):  
    def clean_desc(desc):
        desc = desc.strip()
        if '[IN]' in desc:
            return 'Interest Charge'
        if len(desc)==4:
            return desc
        else:
            return desc[4:]  
    accounts = cfg.get('accounts')
    df_list = list()
    for fpath in file_paths:
        raw_df = pd.read_csv(fpath,skiprows=6, names=['Bank Card','Transaction Type','Date Posted', 'Transaction Amount','Description'])
        if not raw_df.empty:
            ac_num_name_pat = r'.*/(\d{4})\.csv'
            match = re.search(ac_num_name_pat, fpath)
            ac_name = int(match.group(1))
            raw_df['Account Name'] = accounts.get(ac_name, 'No Name')
            raw_df['Description'] = raw_df['Description'].apply(clean_desc)
            raw_df['Category'] = None
            df_list.append(raw_df)  

    # Remove bad rows
    raw_df = pd.concat(df_list)
    raw_df = raw_df[~(raw_df['Bank Card']=='First Bank Card')]
    raw_df.drop(labels='Bank Card',axis=1, inplace=True)
    raw_df['Date Posted'] = pd.to_datetime(raw_df['Date Posted'],format='%Y%m%d')
    raw_df['Transaction Amount'] = raw_df['Transaction Amount'].astype(float)
    raw_df.reset_index(inplace=True, drop=True)
    # raw_df['Transaction Type Code'] = raw_df['Description'].apply(lambda x: x[1:3])
    
    return categorize_transactions(raw_df, session)


def render_modify_container(df, session):  
    filtered_df = pd.DataFrame()
    # Find out what user wants to filter:
    filt_cols = st.multiselect(label='Select Filters', options=df.columns, key='main_filter')
    
    col1_2, col2_2 = st.columns(2)
    for col in filt_cols:
        # print(df[col].dtype)
        if is_datetime64_any_dtype(df[col]):
            col1, col2, _, _= st.columns(4) # My workaround to deal with very large widgets    
            with col1:
                start_dt = st.date_input(label='Select Start Date',
                            min_value=df['Date Posted'].min(), 
                            max_value=df['Date Posted'].max(), 
                            value=df['Date Posted'].min(), 
                            key='start_date_filter')
            with col2:
                end_dt = st.date_input(label='Select End Date',
                                    min_value=start_dt,
                                    max_value=df['Date Posted'].max(),
                                    value=df['Date Posted'].max(), 
                                    key='end_date_filter')
            filtered_df = df[df['Date Posted'].dt.date.between(start_dt, end_dt)]

        elif is_float_dtype(df[col]):
            col1, col2, _, _= st.columns(4) # My workaround to deal with very large widgets
            with col1:
                slider_min, slider_max = st.slider(label=f'Select {col} range.',min_value=df[col].min(), max_value=df[col].max(), value=[df[col].min(), df[col].max()], format='$%0.2f', key='amount_filter')
            filtered_df = df[df[col].between(slider_min, slider_max)]

        elif is_object_dtype(df[col]):
            col1, col2, _, _= st.columns(4) # My workaround to deal with very large widgets
            with col1:
                exclude = st.checkbox('Exclude', key=f'exclude_opt-{col}')
                if col=='Description':
                    desc = st.text_input(label='Enter Description filter.', key='desc_filt')
                    if exclude:
                        filtered_df = df[~(df[col].str.contains(desc, regex=True, case=False, na=False))]
                    else:
                        filtered_df = df[df[col].str.contains(desc,regex=True, case=False, na=False)]
                else:
                    choices = st.multiselect(f'Select {col} Options', options=df[col].unique(), key=f'object_filt-{col}')
                    if choices:
                        if exclude:
                            filtered_df = df[~(df[col].isin(choices))]
                        else:
                            filtered_df = df[df[col].isin(choices)]             
    return filtered_df if not filtered_df.empty else df

def load_metrics(df):
    # Check how this will be impacted by credit vs debit
    metrics = dict()
    if df.empty: 
        logger.error('No data.')
        return metrics
    if 'categories' not in st.session_state.keys():
        logger.warning('Categories are not defined. Limited analytics available.')
    # Exclude Internal Transfers, Investment
    exclusions = ['Internal Transfer','Investment']

    income  = df[~(df['Category'].isin(exclusions)) & (df['Transaction Amount']>0)]['Transaction Amount'].sum()
    expense  = df[~(df['Category'].isin(exclusions)) & (df['Transaction Amount']<0)]['Transaction Amount'].sum()
    saving   = abs(df[df['Category']=='Investment']['Transaction Amount']).sum()
    net      = income + expense
    count    = len(df)

    metrics = {
        'income':   income, 
        'expense':  abs(expense),
        'saving':   saving, 
        'net':      net, 
        'count':    count
    }
    
    return metrics

    
