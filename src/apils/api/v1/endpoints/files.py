from fastapi import APIRouter, UploadFile, File, Depends
from apils.schemas.file import FileResponseSchema
from apils.dependencies.services import get_file_service
from apils.domain.services.file_service import FileService
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
