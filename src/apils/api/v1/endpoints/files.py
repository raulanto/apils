from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from apils.schemas.file import FileResponseSchema
from apils.schemas.report import ReportRequestPayload
from apils.dependencies.services import get_file_service, get_report_service
from apils.domain.services.file_service import FileService
from apils.domain.services.report_service import ReportService
from apils.core.exceptions import FileProcessingDomainError
from apils.schemas.response import ApiResponse

router = APIRouter()

@router.post("/upload", response_model=ApiResponse[FileResponseSchema])
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    if not file.filename.endswith((".csv", ".xls", ".xlsx")):
        raise FileProcessingDomainError("Invalid file format. Please upload a CSV or Excel file.")
    

    metadata = file_service.process_file(file.file, file.filename)
    
    return ApiResponse(
        data=metadata,
        message="Archivo procesado correctamente"
    )

@router.post("/{file_id}/report")
async def generate_report(
    file_id: str,
    payload: ReportRequestPayload | None = None,
    report_service: ReportService = Depends(get_report_service)
):
    if payload is None:
        payload = ReportRequestPayload()
    buffer = report_service.generate_pdf_report(file_id, payload)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{file_id}.pdf"
        }
    )
