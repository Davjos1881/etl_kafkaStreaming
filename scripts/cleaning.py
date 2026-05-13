import pandas as pd
import numpy as np

RENAME_MAP = {
    2015: {
        'Country':                       'country',
        'Region':                        'region',
        'Happiness Rank':                'rank',
        'Happiness Score':               'score',
        'Economy (GDP per Capita)':      'gdp',
        'Family':                        'family',
        'Health (Life Expectancy)':      'health',
        'Freedom':                       'freedom',
        'Trust (Government Corruption)': 'trust',
        'Generosity':                    'generosity',
    },
    2016: {
        'Country':                       'country',
        'Region':                        'region',
        'Happiness Rank':                'rank',
        'Happiness Score':               'score',
        'Economy (GDP per Capita)':      'gdp',
        'Family':                        'family',
        'Health (Life Expectancy)':      'health',
        'Freedom':                       'freedom',
        'Trust (Government Corruption)': 'trust',
        'Generosity':                    'generosity',
    },
    2017: {
        'Country':                       'country',
        'Happiness.Rank':                'rank',
        'Happiness.Score':               'score',
        'Economy..GDP.per.Capita.':      'gdp',
        'Family':                        'family',
        'Health..Life.Expectancy.':      'health',
        'Freedom':                       'freedom',
        'Trust..Government.Corruption.': 'trust',
        'Generosity':                    'generosity',
    },
    2018: {
        'Country or region':             'country',
        'Overall rank':                  'rank',
        'Score':                         'score',
        'GDP per capita':                'gdp',
        'Social support':                'family',
        'Healthy life expectancy':       'health',
        'Freedom to make life choices':  'freedom',
        'Perceptions of corruption':     'trust',
        'Generosity':                    'generosity',
    },
    2019: {
        'Country or region':             'country',
        'Overall rank':                  'rank',
        'Score':                         'score',
        'GDP per capita':                'gdp',
        'Social support':                'family',
        'Healthy life expectancy':       'health',
        'Freedom to make life choices':  'freedom',
        'Perceptions of corruption':     'trust',
        'Generosity':                    'generosity',
    },
}

FINAL_COLS = ['year', 'country', 'region', 'rank', 'score',
              'gdp', 'family', 'health', 'freedom', 'generosity', 'trust']

COUNTRY_ALIASES = {
    'Hong Kong S.A.R., China':  'Hong Kong',
    'Taiwan Province of China': 'Taiwan',
    'North Macedonia':          'Macedonia',
    'Northern Cyprus':          'North Cyprus',
    'Trinidad and Tobago':      'Trinidad & Tobago',
    'Somaliland region':        'Somaliland Region',
}

REGION_FALLBACK = {
    'Belize':                   'Latin America and Caribbean',
    'Somalia':                  'Sub-Saharan Africa',
    'Namibia':                  'Sub-Saharan Africa',
    'South Sudan':              'Sub-Saharan Africa',
    'Gambia':                   'Sub-Saharan Africa',
    'Oman':                     'Middle East and Northern Africa',
    'Sudan':                    'Sub-Saharan Africa',
    'Djibouti':                 'Sub-Saharan Africa',
    'Central African Republic': 'Sub-Saharan Africa',
    'Comoros':                  'Sub-Saharan Africa',
    'Lesotho':                  'Sub-Saharan Africa',
    'Mozambique':               'Sub-Saharan Africa',
    'Laos':                     'Southeastern Asia',
    'Puerto Rico':              'Latin America and Caribbean',
    'Suriname':                 'Latin America and Caribbean',
    'Swaziland':                'Sub-Saharan Africa',
}


def load_raw_data(raw_dir):
    dfs = {}
    for year in [2015, 2016, 2017, 2018, 2019]:
        path = raw_dir / f'{year}.csv'
        dfs[year] = pd.read_csv(path)
    return dfs


def rename_and_select(dfs):
    cleaned = {}
    for year, df in dfs.items():
        df = df.rename(columns=RENAME_MAP[year])
        df['year'] = year
        if 'region' not in df.columns:
            df['region'] = np.nan
        df = df[[c for c in FINAL_COLS if c in df.columns]]
        cleaned[year] = df
    return cleaned


def unify_country_names(dfs):
    for year in dfs:
        dfs[year]['country'] = (
            dfs[year]['country']
            .replace(COUNTRY_ALIASES)
            .str.strip()
        )
    return dfs


def fill_regions(dfs):
    region_map = dfs[2015].set_index('country')['region'].to_dict()
    for year in [2017, 2018, 2019]:
        dfs[year]['region'] = dfs[year]['country'].map(region_map)
        dfs[year]['region'] = dfs[year]['region'].fillna(
            dfs[year]['country'].map(REGION_FALLBACK)
        )
    return dfs


def impute_nulls(dfs):
    trust_mean = dfs[2018]['trust'].mean()
    dfs[2018]['trust'] = dfs[2018]['trust'].fillna(round(trust_mean, 4))
    return dfs


def concatenate(dfs):
    df = pd.concat(dfs.values(), ignore_index=True)
    df['year']    = df['year'].astype(int)
    df['rank']    = df['rank'].astype(int)
    df['country'] = df['country'].astype(str)
    df['region']  = df['region'].where(df['region'].notna(), other=np.nan)
    return df


def validate(df):
    assert df.isnull().sum().sum() == 0,   "Hay nulos en el dataset unificado"
    assert df.duplicated().sum() == 0,     "Hay duplicados en el dataset unificado"
    assert set(df['year'].unique()) == {2015, 2016, 2017, 2018, 2019}, "Faltan años"
    assert all(c in df.columns for c in FINAL_COLS), "Faltan columnas canónicas"