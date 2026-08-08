from apils.domain.services.file_service import FileService
from apils.domain.services.report_service import ReportService

def get_file_service() -> FileService:
    return FileService()

def get_report_service() -> ReportService:
    return ReportService(file_service=get_file_service())
