import pandas as pd
import openpyxl
import streamlit as st
import yaml

@st.cache_data
def clean(file_paths, cfg):
    # print(file_paths)
    accounts = cfg.get('accounts')
    df_list = list()
    for fpath in file_paths:
        raw_df = pd.read_csv(fpath,skiprows=6, names=['Bank Card','Transaction Type','Date Posted', 'Transaction Amount','Description'])

        if not raw_df.empty:
            file_name = fpath[:-4] if isinstance(fpath, str) else fpath.name[:-4]
            raw_df['Account Name'] = accounts.get(file_name, file_name) 
            df_list.append(raw_df)
    # Remove bad rows
    raw_df = pd.concat(df_list)
    raw_df = raw_df[~(raw_df['Bank Card']=='First Bank Card')]
    raw_df.drop(labels='Bank Card',axis=1, inplace=True)
    raw_df['Date Posted'] = pd.to_datetime(raw_df['Date Posted'],format='%Y%m%d').dt.date
    raw_df['Transaction Amount'] = raw_df['Transaction Amount'].astype(float)
    raw_df['Transaction Type Code'] = raw_df['Description'].apply(lambda x: x[1:3])
    # print(raw_df.head())
    return raw_df

@st.cache_data
def load_saved_data():
    with open('configs.yaml','r') as configs:
        cfg = yaml.safe_load(configs)
    return cfg

def update_cfg(cfg):

    with open('configs.yaml','w') as configs:
        yaml.dump(cfg, configs)
    return


def app(files=None):
    st.set_page_config(
        layout='wide'
    )
    st.title('Budget Tracker')
    
    if not files:
        files = st.file_uploader('Upload File Here.', accept_multiple_files=True)

    cfg = load_saved_data()
    accounts = cfg['accounts']
    if files:
        data = clean(files, cfg)
        st.dataframe(data,width='stretch')
        unknown_accounts = [ua for ua in data['Account Name'].unique() 
                                if str(ua) not in accounts.values()] # Only list out accounts that have not been saved in configs.
        ac = pd.DataFrame(
            {
                'Accounts':unknown_accounts, 
                'Name':[cfg.get(account,'') for account in unknown_accounts]
            }
        )
        if not ac.empty:
            edited_ac = st.data_editor(ac)
            for idx, row in edited_ac.iterrows():
                ac = row['Accounts']
                name = row['Name']
                if ac not in cfg.keys():
                    cfg['accounts'][ac] = name
            
            update_cfg(cfg)

if __name__=='__main__':
    files = ['2866.csv', '5060.csv','6781.csv','8558.csv','9544.csv']
    if files:
        cleaned_data = app(files)
    else:
        cleaned_data = app()
    # cleaned_data.to_excel('output.xlsx')
    # cfg = load_saved_data()
    # app()
    # clean(files, cfg)
    # print()

    # print(before)

    