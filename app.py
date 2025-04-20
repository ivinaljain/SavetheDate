from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import uvicorn
from utils import *
from send_email import *

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def capture_page(request: Request):
    return templates.TemplateResponse("camera.html", {"request": request})

@app.post("/process_image")
async def process_image(file: UploadFile = File(...)):
    with open("user_image.png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print("✅ Saved image as user_image.png")   # <‑‑ helpful to see in terminal
    result = analyse_event_poster("user_image.png")
    success = create_event_ics(result)  
    if success:
        create_send_email(request=result)
        return {"message": "Event file has been sent"}
    return {"message": "Event file creation failed, make sure you have uploaded a event image"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)