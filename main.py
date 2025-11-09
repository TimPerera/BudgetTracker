import pandas as pd
import openpyxl
import streamlit as st
import yaml


cfg = load_saved_data()

if 'categories' not in st.session_state:
    st.session_state.categories = cfg.get('categories', 'Unknown')





def app(files=None):
    st.set_page_config(
        layout='wide'
    )
    st.title('Budget Tracker')
    tab1, tab2 = st.tabs(['Data','Settings'])

    with tab1:
        if not files:
            files = st.file_uploader('Upload File Here.', accept_multiple_files=True)

        cfg = load_saved_data()
        accounts = cfg['accounts']
        categories = st.session_state.categories
        if files:
            data = clean(files)
            st.session_state.orig_data = data.copy()
            editable_df = st.data_editor(
                            data, 
                            column_config={
                                'Category': st.column_config.SelectboxColumn(
                                    'Category',
                                    help='Categorize a Transaction Type. Add more categories under settings', 
                                    options=categories, 
                                    default='Unknown'
                                    )
                                }
                            )
            data_btn = st.button('Apply Changes')
            if data_btn: # User has chosen to apply changes in categories.
                mask = st.session_state.orig_data['Category'] != editable_df['Category']
                for idx, row in editable_df[mask].iterrows():
                    category, keyword = row['Category'], row['Description']
                    if pd.isna(category):
                        continue
                    st.session_state.orig_data.at[idx, 'Category'] = category
                    update_categories(category, keyword)
                    categorize_transactions(editable_df)
                st.rerun()
                # st.success('Categorized Transactions')              
            
    with tab2:  # Settings Tab to configure data presentation in tab1.   
        ac = pd.DataFrame(
            {
            'Accounts':accounts.keys(), 
            'Name':[accounts.get(account,None) for account in accounts.keys()]
            }
        )

        new_category = st.text_input('New Category Name')
        add_button = st.button('Add Category')
        if add_button and new_category:
            if new_category not in st.session_state.categories:
                st.session_state.categories[new_category] = []
                update_categories(new_category, None)
                st.rerun()
                st.success(f'Added new Category: {new_category}')
            else:
                st.error('Category already exists.')

        if not ac.empty:
            edited_ac = st.data_editor(ac)
            for _, row in edited_ac.iterrows():
                ac = row['Accounts']
                name = row['Name']
                if ac not in cfg['accounts'].keys():
                    cfg['accounts'][ac] = name
            btn = st.button(
                label='Apply', 
            )
            if btn: 
                update_cfg(cfg)
                st.rerun()

if __name__=='__main__':
    files = [
             '2866.csv', 
             '5060.csv',
             '6781.csv',
             '8558.csv',
             '9544.csv'
            ]
    
    if files:
        cleaned_data = app(files)
    else:
        cleaned_data = app()

    