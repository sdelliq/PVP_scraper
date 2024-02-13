from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import pandas as pd
import uvicorn
from source.Main import main_function
import os
from starlette.responses import FileResponse

app = FastAPI()
'''
@app.get("/")
def run_spiders():
    try:
        main_function()
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running spider: {e.stderr}")  
'''

'''
#this does the scraping without downloading the file to the computer's downloads, but you can finder on the docker container file windows 
@app.post("/scrape")
def upload_file(file: UploadFile, OUTPUT_EXCEL_FOLDER: str = 'output', OUTPUT_EXCEL_NAME: str = "output.xlsx"):   
    if not file.content_type.startswith("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
        raise HTTPException(400, detail="Invalid document type. Please upload an Excel file.")
    
    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(400, detail=f"Error reading Excel file: {str(e)}")

    try:
        OUTPUT_EXCEL_PATH = f'{OUTPUT_EXCEL_FOLDER}/{OUTPUT_EXCEL_NAME}'
        main_function(df, OUTPUT_EXCEL_PATH)
        return JSONResponse(content={"status": "success", "output": "yay"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running spider: {str(e)}") 
'''

@app.post("/scrape")
def upload_file(file: UploadFile, OUTPUT_EXCEL_FOLDER: str = 'output', OUTPUT_EXCEL_NAME: str = "output.xlsx"):   
    if not file.content_type.startswith("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
        raise HTTPException(400, detail="Invalid document type. Please upload an Excel file.")
    
    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(400, detail=f"Error reading Excel file: {str(e)}")

    try:
        main_function(df, OUTPUT_EXCEL_FOLDER, OUTPUT_EXCEL_NAME)
        OUTPUT_EXCEL_PATH = f'{OUTPUT_EXCEL_FOLDER}/{OUTPUT_EXCEL_NAME}'
        return FileResponse(OUTPUT_EXCEL_PATH, filename=OUTPUT_EXCEL_NAME, media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running spider: {str(e)}")



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)