import asyncio
import magic
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from apils.schemas.file import FileResponseSchema
from apils.schemas.report import ReportRequestPayload
from apils.dependencies.services import get_file_service, get_report_service
from apils.domain.services.file_service import FileService
from apils.domain.services.report_service import ReportService
from apils.core.exceptions import FileProcessingDomainError
from apils.schemas.response import ApiResponse

router = APIRouter(prefix="/files", tags=["Archivos"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@router.post(
    "/upload",
    response_model=ApiResponse[FileResponseSchema],
    summary="Subir un archivo CSV o Excel",
    description=(
        "Sube un archivo (`multipart/form-data`, campo `file`) para analizarlo: detecta sus "
        "columnas, tipos de dato (texto/numérico/fecha) y estadísticas básicas por columna "
        "(valores únicos, mínimo, máximo). El `id` devuelto identifica el archivo procesado y se "
        "usa luego en `/files/{file_id}/report` para generar un PDF.\n\n"
        f"Límite de tamaño: {MAX_FILE_SIZE // (1024 * 1024)}MB. Formatos aceptados: "
        "`.csv`, `.xls`, `.xlsx` (se valida tanto la extensión como el contenido real del archivo)."
    ),
    responses={
        400: {"description": "Archivo demasiado grande, o formato/contenido no soportado (no es CSV ni Excel)."},
        422: {"description": "Falta el campo `file` en el multipart/form-data."},
    },
)
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    if getattr(file, 'size', 0) and file.size > MAX_FILE_SIZE:
        raise FileProcessingDomainError(f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB.")
        
    chunk = await file.read(2048)
    await file.seek(0)
    
    mime_type = magic.from_buffer(chunk, mime=True)
    allowed_mimes = ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
    if mime_type not in allowed_mimes and not (mime_type == "text/plain" and file.filename.endswith(".csv")):
        raise FileProcessingDomainError(f"Invalid file content. Detected {mime_type}, expected CSV or Excel.")

    if not file.filename.endswith((".csv", ".xls", ".xlsx")):
        raise FileProcessingDomainError("Invalid file format. Please upload a CSV or Excel file.")
    
    metadata = await asyncio.to_thread(file_service.process_file, file.file, file.filename)
    
    return ApiResponse(
        data=metadata,
        message="Archivo procesado correctamente"
    )

@router.post(
    "/{file_id}/report",
    summary="Generar un reporte PDF a partir de un archivo subido",
    description=(
        "Genera y descarga un PDF con los datos del archivo previamente subido en "
        "`/files/upload` (identificado por `file_id`). El `payload` es opcional y permite "
        "personalizar el reporte: qué columnas mostrar y en qué orden (`schema`), orden de filas "
        "(`sort`), filtros (`filters`) y mapas de calor por columna, incluyendo reglas de color "
        "para valores de texto (`heatmaps`). Sin `payload`, se usa la configuración por defecto.\n\n"
        "La respuesta es el PDF en streaming con `Content-Disposition: attachment`, listo para "
        "descargar como `report_{file_id}.pdf`."
    ),
    responses={
        400: {"description": "El `file_id` no corresponde a un archivo válido, o falló la generación del PDF."},
    },
)
async def generate_report(
    file_id: str,
    payload: ReportRequestPayload | None = None,
    report_service: ReportService = Depends(get_report_service)
):
    if payload is None:
        payload = ReportRequestPayload()
    buffer = await asyncio.to_thread(report_service.generate_pdf_report, file_id, payload)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{file_id}.pdf"
        }
    )
