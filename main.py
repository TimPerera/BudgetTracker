import pandas as pd
import openpyxl
import streamlit as st
import yaml

def load_saved_data():
    with open('configs.yaml','r') as configs:
        cfg = yaml.safe_load(configs)
    return cfg
cfg = load_saved_data()

if 'categories' not in st.session_state:
    st.session_state.categories = cfg.get('categories', 'Unknown')

def clean_desc(desc):
    desc = desc.strip()
    if '[IN]' in desc:
        return 'Interest Charge'
    if len(desc)==4:
        return desc
    else:
        return desc[4:]

def clean(file_paths):
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
    
    return categorize_transactions(raw_df)

def update_cfg(cfg):
    with open('configs.yaml','w') as configs:
        return yaml.dump(cfg, configs)

def update_categories(category, keyword):
    print(f'Attempting to update categories {category}:{keyword}')
    if not keyword:
        cfg['categories'][category] = []
    else:
        categories = cfg['categories']
        
        kw = keyword.strip().lower()
        if not kw in categories.get(category,list()):
            categories[category].append(kw)
        else:
            print('Something unexpected happened')
    st.session_state.categories = cfg['categories']
    update_cfg(cfg)

def categorize_transactions(df):
    for category, keywords in st.session_state.categories.items():
        kws = [keyword.lower().strip() for keyword in keywords]
        for idx, row in df.iterrows():
            desc = row['Description'].lower().strip()
            
            if any([kw in desc for kw in kws]):
                if idx == 3:
                    print(desc, kws)
                df.at[idx, 'Category'] = category
            # else:
            #     if 'msp/div' in desc:
            #         print(f'Categories {desc}. Keywords found for category are {kws}')
    return df

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

    