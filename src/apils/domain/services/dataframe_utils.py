import pandas as pd
from pandas.api.types import is_string_dtype

def infer_and_convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Infers the correct types for dataframe columns, converting strings to dates
    or numeric values (handling currency/percentage symbols) where appropriate.
    Returns the modified dataframe.
    """
    for col in df.columns:
        if df[col].dtype == 'object' or is_string_dtype(df[col]):
            clean_col = df[col].dropna()
            if clean_col.empty:
                continue

            # 1. Try to convert to datetime
            converted_date = pd.to_datetime(df[col], errors='coerce')
            if converted_date.notna().sum() == clean_col.count():
                df[col] = converted_date
                continue
                
            # 2. Try to convert to numeric (handling currency and percentages)
            # Remove everything except digits, minus sign, and decimal point
            cleaned_series = df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
            # Replace empty strings with NaN so to_numeric handles them as missing.
            cleaned_series = cleaned_series.replace('', pd.NA)
            
            converted_num = pd.to_numeric(cleaned_series, errors='coerce')
            
            # If the number of successful numeric conversions matches the number of non-null original values
            if converted_num.notna().sum() == clean_col.count():
                 df[col] = converted_num
                 continue

    return df
