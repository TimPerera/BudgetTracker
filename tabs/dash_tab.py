from utils import logger
import streamlit as st
import plotly.express as px

def render_dash_tab(cfg, session):
    income_col, expense_col, savings_col, net_col, num_transactions_col = st.columns(5)
    df = session.data
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

    # Load intereactive pie chart
    render_piechart(df)

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

def render_piechart(df, cutoff=0.8):
    dft = abs(df.groupby('Category')['Transaction Amount'].agg('sum')).reset_index(name='Total')
    cdft = dft.copy() # consolidated df
    cdft.sort_values(by='Total',ascending=False, inplace=True)
    total= 0
    gt = dft['Total'].sum()# grand total
    for idx, row in cdft.iterrows():
        lt = row['Total']
        pct = lt/gt
        cat = row['Category']
        print(cat, total)
        if total < cutoff:
            total += pct
        else:
            cdft.at[idx, 'Category'] = 'Other'
    pie_df = cdft.groupby('Category')['Total'].agg('sum').reset_index(name='Total')

    fig = px.pie(pie_df, names=pie_df['Category'], values=pie_df['Total'])
    fig.update_traces(
        textposition = 'outside',
        textinfo='label+percent'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)