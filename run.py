import os
import csv
import pandas as pd
import numpy as np

ASSET_ID = 'Asset ID'
CUSTOM_ID = 'Custom ID'
ASSET_LABEL = 'Asset Labels'
ASSET_TITLE = 'Asset Title'
ALLOWED_FILE_EXTS = ['.csv']
ASSETS_HEADERS = [ASSET_ID, CUSTOM_ID, ASSET_LABEL, ASSET_TITLE]

DTYPES = {
    ASSET_ID: np.str,
    CUSTOM_ID: np.str,
    ASSET_LABEL: np.str,
    ASSET_TITLE: np.str
}

# Merges unique values from 2 columns
# - x, y: columns for merging
def merge_values(x, y):
    data = []
    if x != '':
        data.append(x)

    if y != '':
        data.append(y)
    return '|'.join(data)

# Only get non blank value from 2 columns
# - x, y: columns for pulling data
def get_col_value(x, y):
    if x != '':
        return x

    if y != '':
        return y

    return ''

# Load all assets to one DataFrame
# - indir: directory where assets can be found
def load_assets(indir):
    assets = pd.DataFrame()

    for _file in os.listdir(indir):
        _filepath = os.path.join(indir, _file)
        filename, file_extension = os.path.splitext(_filepath)

        if file_extension in ALLOWED_FILE_EXTS:
            print('Pulling assets from {file}...'.format(file=_file))
            df = pd.read_csv(_filepath, dtype=DTYPES).fillna('')

            assets = pd.concat([assets, df])
            del df
            print('Done: Pulling assets from {file}.'.format(file=_file))
        else:
            print('{file} - cannot read file.'.format(file=_file))

    assets = assets.sort_values(by=[ASSET_ID, CUSTOM_ID], na_position='last').fillna('')
    assets = assets.drop_duplicates([ASSET_ID], keep='first')
    
    return assets[ASSETS_HEADERS]

# Augment files using Pandas' Merge Dataframe function
# Only fills in blank columns -- Asset Label & Asset Title
# - source: directory where files for augmenting comes from
# - assets_dir: directory where assets can be found
# - outdir (optional, default: out): directory where output is written

def augment_files(source, assets_dir, outdir='out'):
    assets = load_assets(assets_dir)

    if not os.path.exists(output_directory):
        print('Creating output directory...')
        os.makedirs(output_directory)
        print('Done: Creating output directory.')
        
    for _file in os.listdir(source):
        _filepath = os.path.join(source, _file)
        filename, file_extension = os.path.splitext(_filepath)

        if file_extension in ALLOWED_FILE_EXTS:
            print('Processing {file}...'.format(file=_file))
            df = pd.read_csv(_filepath, dtype=DTYPES).fillna('')

            if not ASSET_LABEL in list(df.columns.values):
                df[ASSET_LABEL] = ''

            if not CUSTOM_ID in list(df.columns.values):
                df[CUSTOM_ID] = ''

            if not ASSET_TITLE in list(df.columns.values):
                df[ASSET_TITLE] = ''
                
            headers = list(df.columns.values)
            
            merged_df = pd.merge(df, assets, on=ASSET_ID, how='left')
            
            merged_df[CUSTOM_ID] = merged_df.apply(
                lambda row: merge_values(row[CUSTOM_ID + '_x'], row[CUSTOM_ID + '_y']), axis=1)
            
            merged_df[ASSET_LABEL] = merged_df.apply(
                lambda row: get_col_value(row[ASSET_LABEL + '_x'], row[ASSET_LABEL + '_y']), axis=1)
            
            merged_df[ASSET_TITLE] = merged_df.apply(
                lambda row: get_col_value(row[ASSET_TITLE + '_x'], row[ASSET_TITLE + '_y']), axis=1)
            
            print('Done: Processing {file}...'.format(file=_file))
            print('Exporting {file}...'.format(file=_file))
            
            merged_df[headers].to_csv(os.path.join(outdir, _file), index=False)
            del merged_df
            
            print('Done: Exporting {file}...'.format(file=_file))
        else:
            print('{file} - cannot augment file.'.format(file=_file))



if __name__ == '__main__':
    assets_directory = os.path.join('sample', 'in', 'assets')
    source_directory = os.path.join('sample', 'in', 'source')
    output_directory = os.path.join('sample', 'out')

    augment_files(source_directory, assets_directory, outdir=output_directory)