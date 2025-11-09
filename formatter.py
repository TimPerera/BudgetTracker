import pandas as pd
import openpyxl


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

if __name__=='__main__':
    cleaned_data = main()
    cleaned_data.to_excel('output.xlsx')