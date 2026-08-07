import uvicorn
from apils.main import app

def main() -> None:
    uvicorn.run("apils.main:app", host="127.0.0.1", port=8000, reload=True)
