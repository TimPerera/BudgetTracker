import streamlit as st
from utils import load_saved_data
from tabs.data_tab import load_data
import plotly.express as px

cfg = load_saved_data()

def test_pie(file_paths):
    data = load_data(file_paths, cfg)
    dft = abs(data.groupby('Category')['Transaction Amount'].agg('sum')).reset_index(name='Total')
    cdft = dft.copy() # consolidated df
    total= 0
    for idx, row in dft.iterrows():
        lt = row['Total']
        cat = row['Category']
        if total < 70:
            total += lt
        else:
            cdft.at[idx, 'Category'] = 'Other'
    pie_df = cdft.groupby('Category')['Total'].agg('sum').reset_index(name='Total')

    fig = px.pie(pie_df, names=pie_df['Category'], values=pie_df['Total'])
    st.plotly_chart(fig)
                

if __name__=='__main__':
    files = [
             'input/2866.csv', 
             'input/5060.csv',
             'input/6781.csv',
             'input/8558.csv',
             'input/9544.csv'
            ]
    
    cleaned_data = test_pie(files)