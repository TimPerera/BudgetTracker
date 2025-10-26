import pandas as pd
import openpyxl

def clean():

    raw_df = pd.read_csv('./statement-3.csv',skiprows=6, names=['Bank Card','Transaction Type','Date Posted', 'Transaction Amount','Description'])
    # print(raw_df.head())
    # raw_df.to_excel('./output.xlsx')
    # Remove bad rows
    raw_df = raw_df[~(raw_df['Bank Card']=='First Bank Card')]

    raw_df['Date Posted'] = pd.to_datetime(raw_df['Date Posted'],format='%Y%m%d').dt.date
    raw_df['Transaction Amount'] = raw_df['Transaction Amount'].astype(float)
    raw_df['Transaction Type Code'] = raw_df['Description'].apply(lambda x: x[1:3])
    return raw_df

if __name__=='__main__':
    cleaned_data = main()
    cleaned_data.to_excel('output.xlsx')