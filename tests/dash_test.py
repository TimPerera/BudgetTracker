import streamlit as st
from utils import load_saved_data
from tabs.data_tab import load_data
import matplotlib.pyplot as plt

cfg = load_saved_data()

def test_pie(file_paths):
    data = load_data(file_paths, cfg)
    df_total = abs(data.groupby('Category')['Transaction Amount'].agg('sum')).reset_index(name='Total')

    fig, ax = plt.subplots()
    ax.pie(df_total['Total'], labels=df_total['Category'],autopct='%1.1f%%', pctdistance=0.85, labeldistance=1.2)
    center_circle = plt.Circle((0,0),0.7, fc='white')
    fig.gca().add_artist(center_circle)
    ax.axis('equal')
    fig.savefig('pie_chart.png')
    

if __name__=='__main__':
    files = [
             'input/2866.csv', 
             'input/5060.csv',
             'input/6781.csv',
             'input/8558.csv',
             'input/9544.csv'
            ]
    
    cleaned_data = test_pie(files)