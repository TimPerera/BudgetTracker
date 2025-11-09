
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
