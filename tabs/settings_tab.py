import pandas as pd

import streamlit as st

from categories import update_categories
from utils import update_cfg

def render_settings_tab(cfg, session):
      # Settings Tab to configure data presentation in tab1.
      
    accounts = cfg.get('accounts')
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
            session.categories[new_category] = []
            update_categories(new_category, None, session, cfg)
            st.rerun()
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