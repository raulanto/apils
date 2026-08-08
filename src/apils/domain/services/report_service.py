import io
import re
import pandas as pd
from typing import List, Dict, Any
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
        
        # If direction is asc, lower values are green (good) and higher are red (bad)
        # If direction is desc, higher values are green and lower are red.
        if direction == "desc":
            ratio = 1 - ratio
            
        # Map ratio (0 to 1) to Green -> Yellow -> Red
        if ratio < 0.5:
            # Green to Yellow: Red increases from 0 to 1, Green is 1, Blue is 0
            # 0 -> (0, 1, 0)
            # 0.5 -> (1, 1, 0)
            r = 2 * ratio
            g = 1.0
            b = 0.0
        else:
            # Yellow to Red: Red is 1, Green decreases from 1 to 0, Blue is 0
            # 0.5 -> (1, 1, 0)
            # 1.0 -> (1, 0, 0)
            r = 1.0
            g = 1.0 - 2 * (ratio - 0.5)
            b = 0.0
            
        return colors.Color(r, g, b, alpha=0.5)

    def generate_pdf_report(self, file_id: str, payload: ReportRequestPayload) -> io.BytesIO:
        file_path = self.file_service.get_file_path(file_id)
        
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            raise FileProcessingDomainError(f"Error reading file for report: {str(e)}")

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
        
        # Calculate heatmap bounds
        heatmap_bounds = {}
        for hm in (payload.heatmaps or []):
            col = hm.column
            if col in df.columns:
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
                            # Clean currency and percentage strings before parsing
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
        
        # Determine page size
        page_size_val = letter
        if payload.schema_ and payload.schema_.pageSize:
            size_name = payload.schema_.pageSize.upper()
            size_map = {
                "LETTER": letter, "LEGAL": legal,
                "A4": A4, "A3": A3, "A2": A2, "A1": A1, "A0": A0
            }
            page_size_val = size_map.get(size_name, letter)
        else:
            # Auto-scale if not explicitly provided
            if len(visible_cols) >= 25:
                page_size_val = A0
            elif len(visible_cols) >= 20:
                page_size_val = A1
            elif len(visible_cols) >= 15:
                page_size_val = A2
            elif len(visible_cols) >= 10:
                page_size_val = A3
                
        # Generate PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(page_size_val), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Report", styles['Title']))
        
        # Prepare data for table
        data = [df.columns.tolist()]
        
        # Convert df to list of lists, handling NaNs
        records = df.astype(str).replace('nan', '').values.tolist()
        data.extend(records)
        
        # Create table style
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
        
        # Apply heatmap background colors
        if not df.empty:
            for row_idx, (_, row) in enumerate(df.iterrows(), start=1):
                for col_idx, col_name in enumerate(df.columns):
                    if col_name in heatmap_bounds:
                        val = row[col_name]
                        if pd.notna(val) and val != '':
                            bounds = heatmap_bounds[col_name]
                            try:
                                if bounds["is_date"]:
                                    val_parsed = pd.to_datetime(val, errors='coerce')
                                    if pd.isna(val_parsed):
                                        continue
                                    val_num = val_parsed.timestamp()
                                else:
                                    cleaned_val = re.sub(r'[^\d\.\-]', '', str(val))
                                    val_num = float(cleaned_val) if cleaned_val else 0.0
                                    
                                bg_color = self._get_color_for_value(
                                    val_num, 
                                    float(bounds["min"]), 
                                    float(bounds["max"]), 
                                    bounds["direction"]
                                )
                                style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), bg_color)
                            except Exception:
                                pass
        
        # Dynamic column widths based on available width and content length
        available_width = doc.width
        num_cols = len(visible_cols)
        
        if num_cols > 0:
            col_max_lengths = []
            for col_idx in range(num_cols):
                # Calculate the max character length in each column
                max_len = max(len(str(row[col_idx])) for row in data)
                # Keep a reasonable minimum length
                col_max_lengths.append(max(max_len, 4))
                
            total_length = sum(col_max_lengths)
            # Allocate width proportionally
            col_widths = [available_width * (l / total_length) for l in col_max_lengths]
        else:
            col_widths = []
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(style)
        
        elements.append(t)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
