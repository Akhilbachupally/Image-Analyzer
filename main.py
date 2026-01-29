import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-flash-latest")
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "main.html",
        {"request": request, "image_data": None, "ai_description": None}
    )
@app.post("/", response_class=HTMLResponse)
async def analyze_image(
    request: Request,
    image: UploadFile = File(...)
):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, image.filename)
        with open(filepath, "wb") as f:
            f.write(await image.read())
        with Image.open(filepath) as img:
            image_data = {
                "filename": image.filename,
                "format": img.format,
                "width": img.width,
                "height": img.height
            }
        with Image.open(filepath) as img:
            response = model.generate_content(
                ["Describe this image clearly and simply.", img]
            )
        return templates.TemplateResponse(
            "main.html",
            {
                "request": request,
                "image_data": image_data,
                "ai_description": response.text
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
