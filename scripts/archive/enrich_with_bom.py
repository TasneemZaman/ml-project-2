"""
Enrich existing dataset with Box Office Mojo data.

Reads `data/raw/imdb_movies_large.csv` and writes `data/raw/imdb_movies_large_with_bom.csv`.
This script is conservative by default (only queries a small subset if run with --limit).
"""
import argparse
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from boxoffice_mojo import get_bom_data
import requests
from tqdm import tqdm


def enrich_dataframe(df: pd.DataFrame, workers: int = 5, limit: int = None) -> pd.DataFrame:
    session = requests.Session()
    rows = []
    items = df.iterrows()
    if limit:
        items = list(df.head(limit).iterrows())
    else:
        items = list(df.iterrows())

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {}
        for idx, row in items:
            title = row.get('movie_title') or row.get('title')
            year = row.get('year') if 'year' in row else None
            futures[ex.submit(get_bom_data, title, year, session)] = idx

        results = {}
        for fut in tqdm(as_completed(futures), total=len(futures)):
            idx = futures[fut]
            try:
                data = fut.result()
            except Exception as e:
                data = {'bom_url': None, 'bom_opening_weekend': None, 'bom_first_week': None, 
                        'bom_domestic_total': None, 'bom_worldwide_total': None, 'bom_international_total': None}
            results[idx] = data

    # attach results
    bom_url = []
    bom_opening = []
    bom_first = []
    bom_domestic = []
    bom_worldwide = []
    bom_international = []
    for idx, row in df.iterrows():
        r = results.get(idx, {})
        bom_url.append(r.get('bom_url'))
        bom_opening.append(r.get('bom_opening_weekend'))
        bom_first.append(r.get('bom_first_week'))
        bom_domestic.append(r.get('bom_domestic_total'))
        bom_worldwide.append(r.get('bom_worldwide_total'))
        bom_international.append(r.get('bom_international_total'))

    df = df.copy()
    df['bom_url'] = bom_url
    df['bom_opening_weekend'] = bom_opening
    df['bom_first_week'] = bom_first
    df['bom_domestic_total'] = bom_domestic
    df['bom_worldwide_total'] = bom_worldwide
    df['bom_international_total'] = bom_international
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='data/raw/imdb_movies_large.csv')
    p.add_argument('--output', default='data/raw/imdb_movies_large_with_bom.csv')
    p.add_argument('--workers', type=int, default=6)
    p.add_argument('--limit', type=int, default=None, help='limit number of movies to process (for testing)')
    args = p.parse_args()

    df = pd.read_csv(args.input)
    print(f'Loaded {len(df)} rows from {args.input}')
    df2 = enrich_dataframe(df, workers=args.workers, limit=args.limit)
    df2.to_csv(args.output, index=False)
    print('Wrote enriched CSV to', args.output)


if __name__ == '__main__':
    main()
