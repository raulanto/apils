import io
import re
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from apils.schemas.report import ReportRequestPayload
from apils.core.exceptions import FileProcessingDomainError

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter, legal, A4, A3, A2, A1, A0
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class ReportService:
    def __init__(self, file_service):
        self.file_service = file_service
        
    def _apply_filters(self, df: pd.DataFrame, filters: List[Any]) -> pd.DataFrame:
        for f in filters:
            col = f.column
            if col not in df.columns:
                continue
            
            if f.type == "text" and f.values:
                df = df[df[col].isin(f.values)]
            elif f.type == "range":
                if f.min is not None:
                    df = df[df[col] >= float(f.min)]
                if f.max is not None:
                    df = df[df[col] <= float(f.max)]
        return df

    def _get_color_for_value(self, val: float, min_val: float, max_val: float, direction: str) -> colors.Color:
        if pd.isna(val):
            return colors.white
            
        if max_val == min_val:
            return colors.white
            
        # Normalize between 0 and 1
        ratio = (val - min_val) / (max_val - min_val)
        
        if direction == "desc":
            ratio = 1 - ratio
            
        if ratio < 0.5:
            r = 2 * ratio
            g = 1.0
            b = 0.0
        else:
            r = 1.0
            g = 1.0 - 2 * (ratio - 0.5)
            b = 0.0
            
        return colors.Color(r, g, b, alpha=0.5)

    def _calculate_heatmap_bounds(self, df: pd.DataFrame, heatmaps: List[Any]) -> Dict[str, Any]:
        heatmap_bounds = {}
        for hm in (heatmaps or []):
            col = hm.column
            if col in df.columns:
                is_text = hm.dataType == "text"
                if is_text and getattr(hm, "textRules", None):
                    # Validate HexColors before storing
                    rules = {}
                    for rule in hm.textRules:
                        if re.match(r'^#[0-9A-Fa-f]{6}$', rule.color):
                            rules[rule.value] = rule.color
                    
                    if rules:
                        heatmap_bounds[col] = {
                            "is_text": True,
                            "rules": rules
                        }
                    continue
                
                is_date = hm.dataType == "date" or pd.api.types.is_datetime64_any_dtype(df[col])
                is_numeric = hm.dataType in ("number", "currency", "percentage", "numeric") or pd.api.types.is_numeric_dtype(df[col])
                
                if is_numeric or is_date:
                    series = df[col].dropna()
                    if series.empty:
                        continue
                    try:
                        if is_date:
                            series = pd.to_datetime(series, errors='coerce').dropna()
                            if series.empty:
                                continue
                            min_val = series.min().timestamp()
                            max_val = series.max().timestamp()
                        else:
                            cleaned_series = series.astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
                            series = pd.to_numeric(cleaned_series, errors='coerce').dropna()
                            if series.empty:
                                continue
                            min_val = float(series.min())
                            max_val = float(series.max())
                            
                        heatmap_bounds[col] = {
                            "min": min_val,
                            "max": max_val,
                            "direction": hm.direction,
                            "is_date": is_date
                        }
                    except Exception:
                        pass
        return heatmap_bounds

    def _determine_page_size(self, num_cols: int, schema_page_size: str | None):
        page_size_val = letter
        if schema_page_size:
            size_name = schema_page_size.upper()
            size_map = {
                "LETTER": letter, "LEGAL": legal,
                "A4": A4, "A3": A3, "A2": A2, "A1": A1, "A0": A0
            }
            page_size_val = size_map.get(size_name, letter)
        else:
            if num_cols >= 25:
                page_size_val = A0
            elif num_cols >= 20:
                page_size_val = A1
            elif num_cols >= 15:
                page_size_val = A2
            elif num_cols >= 10:
                page_size_val = A3
        return page_size_val

    def _build_table(self, df: pd.DataFrame, heatmap_bounds: Dict[str, Any], available_width: float) -> Table:
        data = [df.columns.tolist()]
        records = df.astype(str).replace('nan', '').values.tolist()
        data.extend(records)
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ])
        
        if not df.empty:
            # Vectorized color calculation
            for col_idx, col_name in enumerate(df.columns):
                if col_name in heatmap_bounds:
                    bounds = heatmap_bounds[col_name]
                    
                    if bounds.get("is_text"):
                        rules = bounds.get("rules", {})
                        for row_idx, val in enumerate(df[col_name], start=1):
                            if pd.isna(val):
                                continue
                            val_str = str(val).strip()
                            if val_str in rules:
                                bg_color = colors.HexColor(rules[val_str])
                                style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), bg_color)
                        continue

                    # Numeric/Date vectorization
                    series = df[col_name]
                    if bounds.get("is_date", False):
                        numeric_series = pd.to_datetime(series, errors='coerce').astype('int64') // 10**9
                        numeric_series = numeric_series.replace(-9223372036, np.nan) # Handle NaT which becomes large negative
                    else:
                        cleaned = series.astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
                        numeric_series = pd.to_numeric(cleaned, errors='coerce')
                    
                    min_val = float(bounds["min"])
                    max_val = float(bounds["max"])
                    direction = bounds["direction"]
                    
                    if min_val != max_val:
                        ratio = (numeric_series - min_val) / (max_val - min_val)
                        if direction == "desc":
                            ratio = 1 - ratio
                        
                        r = np.where(ratio < 0.5, 2 * ratio, 1.0)
                        g = np.where(ratio < 0.5, 1.0, 1.0 - 2 * (ratio - 0.5))
                        b = np.zeros_like(ratio)
                        
                        for row_idx, val in enumerate(ratio, start=1):
                            if pd.notna(val):
                                c = colors.Color(r[row_idx-1], g[row_idx-1], b[row_idx-1], alpha=0.5)
                                style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), c)

        num_cols = len(df.columns)
        if num_cols > 0:
            # Vectorized column width calculation
            str_df = pd.DataFrame(data)
            col_max_lengths = str_df.astype(str).apply(lambda c: c.str.len().max()).clip(lower=4).tolist()
            total_length = sum(col_max_lengths)
            col_widths = [available_width * (l / total_length) for l in col_max_lengths]
        else:
            col_widths = []
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(style)
        return t

    def generate_pdf_report(self, file_id: str, payload: ReportRequestPayload) -> io.BytesIO:
        file_path = self.file_service.get_file_path(file_id)
        
        try:
            # We assume it is a parquet file now
            df = pd.read_parquet(file_path)
        except Exception as e:
            raise FileProcessingDomainError(f"Error reading file for report: {str(e)}") from e

        # 1. Apply filters
        df = self._apply_filters(df, payload.filters or [])
        
        # 2. Apply sorting
        if payload.sort and payload.sort.column in df.columns:
            ascending = payload.sort.direction == "asc"
            df = df.sort_values(by=payload.sort.column, ascending=ascending)
            
        # 3. Select columns
        if payload.schema_:
            if payload.schema_.orderedColumns:
                visible_set = set(payload.schema_.visibleColumns)
                visible_cols = [c for c in payload.schema_.orderedColumns if c in visible_set and c in df.columns]
            else:
                visible_cols = [c for c in payload.schema_.visibleColumns if c in df.columns]
        else:
            visible_cols = df.columns.tolist()
        
        df = df[visible_cols]
        
        heatmap_bounds = self._calculate_heatmap_bounds(df, payload.heatmaps)
        
        schema_page_size = payload.schema_.pageSize if payload.schema_ else None
        page_size_val = self._determine_page_size(len(visible_cols), schema_page_size)
                
        # Generate PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(page_size_val), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Report", styles['Title']))
        
        t = self._build_table(df, heatmap_bounds, doc.width)
        elements.append(t)
        
        try:
            doc.build(elements)
        except Exception as e:
            raise FileProcessingDomainError(f"Error building PDF: {str(e)}") from e
            
        buffer.seek(0)
        
        return buffer
