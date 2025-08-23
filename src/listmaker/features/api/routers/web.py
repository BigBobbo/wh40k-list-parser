"""Web interface routes for HTML pages."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Get the templates directory (go up from routers -> api -> features -> listmaker -> templates)
templates_dir = Path(__file__).parent.parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/parse", response_class=HTMLResponse)
async def parse_page(request: Request):
    """Render the army list parser page."""
    return templates.TemplateResponse("parse.html", {"request": request})