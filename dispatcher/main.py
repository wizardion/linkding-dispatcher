import os
import httpx
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from cache_manager import CacheManager
from urllib.parse import quote_plus
from urllib.parse import urlencode

from settings import settings
from core import get_tags, get_bundles, check_url, encode_url
from models import SaveRequest

import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
cache = CacheManager()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/get", response_class=HTMLResponse)
async def get_dispatcher(request: Request, url: str = Query("")):
    async with asyncio.TaskGroup() as tg:
        tags_task = tg.create_task(
            get_tags(cache, settings.linkding_url, settings.linkding_token)
        )

        bundles_task = tg.create_task(
            get_bundles(cache, settings.linkding_url, settings.linkding_token)
        )

        bookmark, metadata = await check_url(url, settings.linkding_url, settings.linkding_token)
    
    all_tags = tags_task.result()
    bundles = bundles_task.result()

    return templates.TemplateResponse(
        request=request, 
        name=f"dispatcher.html",
        context={
            "url": url, 
            "all_tags": all_tags,
            "available_tags": (
                list(set(all_tags) - set([x["all_tags"] for x in bundles if x.get("all_tags")]))
            ),
            "bundles": bundles, 
            "bookmark": bookmark,
            "metadata": metadata
        }
    )

@app.get("/list", response_class=HTMLResponse)
async def get_dispatcher(request: Request, url: str = Query(""), theme: str | None = None):
    headers = {"Authorization": f"Token {settings.linkding_token}"}
    bookmarks = []

    async with httpx.AsyncClient() as client:
        try:
            c_res = await client.get(f"{settings.linkding_url}/api/bookmarks/?limit=25&offset=0", headers=headers, timeout=5.0)
            if c_res.status_code == 200:
                data = c_res.json()
                bookmarks = data.get("results", [])
        except Exception as e:
            print(f"Error fetching bookmark data from Linkding API. {e}")

    return templates.TemplateResponse(
        request=request, 
        name="list.html",
        context={
            "bookmarks": bookmarks,
        }
    )

@app.get("/check")
async def check_bookmark(request: Request, url: str = Query("")):
    headers = {"Authorization": f"Token {settings.linkding_token}"}
    
    bundles = []
    metadata = {}
    bookmark_data = {}

    async with httpx.AsyncClient() as client:
        # 1. Fetch cached Bundles
        try:
            b_res = await client.get(f"{settings.linkding_url}/api/bundles/", headers=headers, timeout=5.0)
            if b_res.status_code == 200:
                bundles = b_res.json().get("results", [])
                print("Fetched bundles:")
                print(bundles)
        except Exception:
            pass

        # 2. Check if URL already exists
        if url:
            try:
                c_res = await client.get(f"{settings.linkding_url}/api/bookmarks/check/?url={url}", headers=headers, timeout=5.0)
                if c_res.status_code == 200:
                    data = c_res.json()
                    bookmark_data = data.get("bookmark")
                    metadata = data.get("metadata")
                    print("Fetched bookmark data:")
                    print(bookmark_data)
            except Exception:
                pass

    return {
        "url": url, 
        "bundles": bundles, 
        "bookmark": bookmark_data,
        "metadata": metadata
    }

@app.post("/save", response_class=HTMLResponse)
async def save_bookmark(
    request: Request,
    bookmark_id: str = Form(...),          # Hidden field to identify if this is an edit (existing bookmark) or a new bookmark
    url: str = Form(...),                  # '...' means this field is strictly Required
    title: str = Form(""),                 # Defaults to empty string if left blank
    bundle: str = Form(""),                # Matches the 'name="bundle"' we added
    tag_names: str = Form(""),             # Matches 'name="tag_names"'
    is_archived: bool = Form(False),       # Checkboxes send nothing if unchecked; Form(False) handles it safely
    description: str = Form("")            # Matches the description textarea
):
    if not url:
        return templates.TemplateResponse(
        request=request, 
        name="response.html", 
        context={
            "url": url,
            "success": False,
            "error": "URL is required to save a bookmark."
        }
    )

    error = None
    status_message = "Bookmark saved!"
    headers = {"Authorization": f"Token {settings.linkding_token}"}
    tag_list = list(filter(None, set([bundle] + [t.strip() for t in tag_names.split(",")])))
    payload = {
        "url": encode_url(url),
        "title": title,
        "tag_names": tag_list,
        "is_archived": is_archived,
        "description": description
    }

    print(f"================== Saving bookmark with data =================")
    import json
    print(json.dumps(payload, indent=2))
    print('------------------------------------------------')

    async with httpx.AsyncClient() as client:
        try:
            if bookmark_id and bookmark_id != "0":
                # Update existing bookmark
                res = await client.put(f"{settings.linkding_url}/api/bookmarks/{bookmark_id}/", json=payload, headers=headers)
                print(f"Updating bookmark ID {bookmark_id} at {settings.linkding_url}/api/bookmarks/{bookmark_id}/")
            else:
                # Create new bookmark
                res = await client.post(f"{settings.linkding_url}/api/bookmarks/", json=payload, headers=headers)
            
            print(f"Received response with status code: {res.status_code}")
            print(json.dumps(res.json(), indent=2))

            if res.status_code in (200, 201):
                data = res.json()
                print("Bookmark saved successfully. Response data:")
                print(data)
                print('------------------------------------------------')
                # data.get("detail", "No error details provided.")
                # await cache.reset()
            else:
                status_message = "Failed to save bookmark!"
                data = res.json()
                error = f"{data.get("detail", {}).get("msg", "Unknown error")}"
                print(error)
        except Exception as e:
            status_message = "Failed to save bookmark!"
            error = f"Unexpected error occurred on deleting bookmark."
            print(f"Error fetching bookmark data from Linkding API. {e}")

    return templates.TemplateResponse(
        request=request, 
        name="response.html", 
        context={
            "error": error,
            "status_message": status_message
        }
    )

# @app.delete("/delete/{bookmark_id}")
# @app.post("/delete/{bookmark_id}", response_class=HTMLResponse)
@app.post("/delete", response_class=HTMLResponse)
async def save_bookmark(
    request: Request,
    bookmark_id: str = Form(...),          # Hidden field to identify if this is an edit (existing bookmark) or a new bookmark
):
# async def delete_bookmark(bookmark_id: int):
    headers = {"Authorization": f"Token {settings.linkding_token}"}
    error = None
    status_message = "Bookmark removed!"

    print(f"================== Deleting bookmark with ID: {bookmark_id} =================")

    if bookmark_id and bookmark_id != "0":
        async with httpx.AsyncClient() as client:
            try:
                res = await client.delete(f"{settings.linkding_url}/api/bookmarks/{bookmark_id}/", headers=headers)
                if res.status_code not in (204, 200):
                    status_message = "Failed to delete bookmark!"
                    error = f"Status code: {res.status_code}"
            except Exception as e:
                status_message = "Failed to delete bookmark!"
                error = f"Unexpected error occurred on deleting bookmark."
                print(error)
    
    return templates.TemplateResponse(
        request=request, 
        name="response.html", 
        context={
            "error": error,
            "status_message": status_message
        }
    )