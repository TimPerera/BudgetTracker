# from main import session, cfg
from utils import update_cfg

def update_categories(category, keyword, session, cfg):
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
    session.categories = cfg['categories']
    update_cfg(cfg)

def categorize_transactions(df, session):
    for category, keywords in session.categories.items():
        kws = [keyword.lower().strip() for keyword in keywords]
        for idx, row in df.iterrows():
            desc = row['Description'].lower().strip()
            
            if any([kw in desc for kw in kws]):
                if idx == 3:
                    print(desc, kws)
                df.at[idx, 'Category'] = category
    return df
