from utils import logger
import streamlit as st
import plotly.express as px
import pandas as pd

FONT_SIZE=13

def render_dash_tab(cfg, session):
    income_col, expense_col, savings_col, net_col, num_transactions_col = st.columns(5)
    df = session.data
    exclusions = ['Internal Transfer','Investment']
    df_filtered = df[~(df['Category'].isin(exclusions))].reset_index()
    metrics = load_metrics(df)
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

    pie_container, bar_container, line_container = st.columns(3)
    with pie_container:
        # Load intereactive pie chart
        render_piechart(df_filtered)

    with bar_container:
        render_barchart(df_filtered)
    # Load Line Chart
    # # Income vs Expenses
    # line_container, _ = st.columns(2)
    with line_container:
        render_linechart(df_filtered)
    st.markdown('#')
    st.dataframe(df)

def render_barchart(df):

    dfg = df.groupby('Category')['Transaction Amount'].sum().reset_index(name='Total Amount').sort_values(by='Total Amount', ascending=False)
    dfg['Total Amount'] = dfg['Total Amount'].abs()
    dfg['Label'] = dfg['Total Amount'].apply(lambda x: f'${x:,.2f}')
    fig = px.bar(dfg, y='Category',x='Total Amount')
    fig.update_traces(text=dfg['Label'], textposition='outside', textfont=dict(size=FONT_SIZE))
    st.plotly_chart(fig)

def render_linechart(df):
    df['Type'] = df['Transaction Amount'].apply(lambda x: 'Expense' if x<0 else 'Income') 
    dfg = df.groupby(['Date Posted','Type'])['Transaction Amount'].sum().reset_index(name='Amount')
    dfg['Amount'] = dfg['Amount'].abs()
    dfg.sort_values('Date Posted', inplace=True)

    # with pd.ExcelWriter('reporter.xlsx') as writer:
    #     dfg.to_excel(writer, sheet_name='grouped')
    #     df.to_excel(writer, sheet_name='raw')
    fig = px.line(dfg, x='Date Posted', y='Amount', color='Type', color_discrete_sequence=['#FF0000', '#00FF00'],symbol='Type')
    st.plotly_chart(fig)


def load_metrics(df):
    # Check how this will be impacted by credit vs debit
    metrics = dict()
    if df.empty: 
        logger.error('No data.')
        return metrics
    if 'categories' not in st.session_state.keys():
        logger.warning('Categories are not defined. Limited analytics available.')
    income   = df[(df['Transaction Amount']>0)]['Transaction Amount'].sum()
    expense  = df[(df['Transaction Amount']<0)]['Transaction Amount'].abs().sum()
    saving   = abs(df[df['Category']=='Investment']['Transaction Amount']).sum()
    net      = income - expense
    count    = len(df)

    metrics = {
        'income':   income, 
        'expense':  expense,
        'saving':   saving, 
        'net':      net, 
        'count':    count
    }
    
    return metrics

def render_piechart(df, cutoff=0.8):
    dft = abs(df.groupby('Category')['Transaction Amount'].agg('sum')).reset_index(name='Total')
    cdft = dft.copy()
    cdft.sort_values(by='Total',ascending=False, inplace=True)
    total= 0
    gt = dft['Total'].sum()# grand total
    for idx, row in cdft.iterrows():
        lt = row['Total']
        pct = lt/gt
        if total < cutoff:
            total += pct
        else:
            cdft.at[idx, 'Category'] = 'Other'

    pie_df = cdft.groupby('Category')['Total'].agg('sum').reset_index(name='Total')
    fig = px.pie(pie_df, names=pie_df['Category'], values=pie_df['Total'])
    fig.update_traces(
        textposition = 'outside',
        textinfo='label+percent',
        textfont=dict(size=FONT_SIZE)
    )
    fig.update_layout(showlegend=False)
    return st.plotly_chart(fig, key='pie')