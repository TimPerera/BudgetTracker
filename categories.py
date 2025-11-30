# from main import session, cfg
from utils import update_cfg, logger

def update_categories(category, keyword, session, cfg):
    
    if not keyword:
        cfg['categories'][category] = []
    else:
        categories = cfg['categories']
        
        kw = keyword.strip().lower()
        if not kw in categories.get(category,list()):
            logger.debug(f'Updating category {category}:{keyword}')
            categories[category].append(kw)
    session.categories = cfg['categories']
    update_cfg(cfg)

def mixed_categories(desc, cfg):
    cfg.get

def categorize_transactions(df, cfg):
    
    for idx, row in df.iterrows():
        desc = row['Description'].lower().strip()

        if 'doordash' in desc:
            match = None
            for _, map in cfg['categories']['Mixed'].items():
                for key, values in map.items():    
                    if any([val in desc for val in values]):
                        match = key
                # logger.debug(f'key:{key}, value:{values}, match:{match}')
            logger.debug(f'{desc}.{match}. {key}')
            df.at[idx, 'Category'] = key if not match else match
            continue
        for category, keywords in cfg.get('categories', dict()).items():
            kws = [keyword.lower().strip() for keyword in keywords if isinstance(keyword, str)]
            if any([kw in desc for kw in kws]):
                df.at[idx, 'Category'] = category
    return df
