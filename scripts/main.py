import threading
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
from cleaning import (load_raw_data, rename_and_select, fill_regions,
                      unify_country_names, impute_nulls, concatenate, validate)
from kafka_src.producer import run_producer
from kafka_src.consumer import run_consumer

base_path = Path(r'C:\Users\santa\Desktop\ETL_cositas\workshop_03')

# Rutas
raw_dir       = base_path / 'data' / 'raw'
processed_dir = base_path / 'data' / 'processed'
unified_csv   = processed_dir / 'happiness_unified.csv'
model_path    = base_path / 'models' / 'model.pkl'
scaler_path   = base_path / 'models' / 'scaler.pkl'


def main():

    # ── Clean ────────────────────────────────────────────────────────────────
    dfs = load_raw_data(raw_dir)
    dfs = rename_and_select(dfs)
    dfs = unify_country_names(dfs)
    dfs = fill_regions(dfs)
    dfs = impute_nulls(dfs)
    df_unified = concatenate(dfs)
    validate(df_unified)
    df_unified.to_csv(unified_csv, index=False)

    # ── Streaming ────────────────────────────────────────────────────────────
    producer_thread = threading.Thread(target=run_producer, args=(unified_csv,))
    producer_thread.start()

    run_consumer(model_path, scaler_path)

    producer_thread.join()


if __name__ == '__main__':
    main()