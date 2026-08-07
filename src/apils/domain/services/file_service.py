import io
import pandas as pd
from typing import BinaryIO
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype, is_string_dtype

from apils.domain.entities.file_metadata import FileMetadata, ColumnMetadata
from apils.core.exceptions import FileProcessingDomainError

class FileService:
    def process_file(self, file_stream: BinaryIO, filename: str) -> FileMetadata:
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(file_stream)
            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file_stream)
            else:
                raise FileProcessingDomainError("Unsupported file format. Please upload CSV or Excel.")
            
            columns = []
            
            for col in df.columns:
                if df[col].dtype == 'object' or is_string_dtype(df[col]):
                    # Intentar convertir a fecha
                    converted = pd.to_datetime(df[col], errors='coerce')
                    if converted.notna().sum() == df[col].notna().sum() and not df[col].dropna().empty:
                        df[col] = converted

                is_num = is_numeric_dtype(df[col])
                is_date = is_datetime64_any_dtype(df[col])
                is_text = is_string_dtype(df[col]) or df[col].dtype == 'object'
                
                # Drop NAs for calculating min/max/unique
                clean_col = df[col].dropna()
                
                col_meta = ColumnMetadata(
                    name=str(col),
                    dtype=str(df[col].dtype),
                    is_text=is_text,
                    is_numeric=is_num,
                    is_date=is_date
                )
                
                if not clean_col.empty:
                    if is_text:
                        # Limit unique values so we don't blow up the response for mostly-unique text columns
                        unique_vals = clean_col.unique().tolist()
                        col_meta.unique_values = unique_vals if len(unique_vals) <= 100 else unique_vals[:100]
                    
                    if is_num or is_date:
                        # Need to convert numpy types to standard python types for JSON serialization
                        col_meta.min_value = clean_col.min().item() if hasattr(clean_col.min(), 'item') else clean_col.min()
                        col_meta.max_value = clean_col.max().item() if hasattr(clean_col.max(), 'item') else clean_col.max()
                        
                        # Handle timestamp serialization issue
                        if is_date:
                            col_meta.min_value = col_meta.min_value.isoformat() if hasattr(col_meta.min_value, 'isoformat') else str(col_meta.min_value)
                            col_meta.max_value = col_meta.max_value.isoformat() if hasattr(col_meta.max_value, 'isoformat') else str(col_meta.max_value)
                
                columns.append(col_meta)
                
            return FileMetadata(
                filename=filename,
                total_rows=len(df),
                columns=columns
            )
        except FileProcessingDomainError:
            raise
        except Exception as e:
            raise FileProcessingDomainError(f"Error processing file: {str(e)}")

