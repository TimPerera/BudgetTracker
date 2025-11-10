import pandas as pd

import streamlit as st

from categories import categorize_transactions, update_categories

def render_data_tab(file_paths, cfg, session):

    # Load Data
    data = load_data(file_paths, cfg, session)
    categories = session.categories
    session.orig_data = data.copy()
    editable_df = st.data_editor(
                            data, 
                            column_config={
                                'Category': st.column_config.SelectboxColumn(
                                    'Category',
                                    help='Categorize a Transaction Type. Add more categories under settings', 
                                    options=categories, 
                                    default='Unknown'
                                    )
                                })
    data_btn = st.button('Apply Changes')
    if data_btn: # User has chosen to apply changes in categories.
        mask = st.session_state.orig_data['Category'] != editable_df['Category']
        for idx, row in editable_df[mask].iterrows():
            category, keyword = row['Category'], row['Description']
            if pd.isna(category):
                continue
            st.session_state.orig_data.at[idx, 'Category'] = category
            update_categories(category, keyword, session, cfg)
            categorize_transactions(editable_df, session)
        st.rerun()

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
            file_name = fpath[:-4] if isinstance(fpath, str) else fpath.name[:-4]
            raw_df['Account Name'] = accounts.get(file_name, file_name)
            raw_df['Description'] = raw_df['Description'].apply(clean_desc)
            raw_df['Category'] = None
            df_list.append(raw_df)
    # Remove bad rows
    raw_df = pd.concat(df_list)
    raw_df = raw_df[~(raw_df['Bank Card']=='First Bank Card')]
    raw_df.drop(labels='Bank Card',axis=1, inplace=True)
    raw_df['Date Posted'] = pd.to_datetime(raw_df['Date Posted'],format='%Y%m%d').dt.date
    raw_df['Transaction Amount'] = raw_df['Transaction Amount'].astype(float)
    raw_df.reset_index(inplace=True)
    # raw_df['Transaction Type Code'] = raw_df['Description'].apply(lambda x: x[1:3])
    
    return categorize_transactions(raw_df, session)



    
