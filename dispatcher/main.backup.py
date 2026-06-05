import os
import httpx
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from cache_manager import CacheManager, CacheStrategy
# from starlette.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
cache = CacheManager()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Points to the Linkding container inside the Docker bridge network
LINKDING_HOST = os.getenv("LINKDING_HOST", "linkding")
LINKDING_PORT = os.getenv("LINKDING_PORT", "9090")
LINKDING_TOKEN = os.getenv("LINKDING_TOKEN", "")
LINKDING_URL = f"http://{LINKDING_HOST}:{LINKDING_PORT}"

class SaveRequest(BaseModel):
    url: str
    tags: list[str]


@app.get("/get", response_class=HTMLResponse)
async def get_dispatcher(request: Request, url: str = Query(""), theme: str | None = None):
    print("---------------------------------------------------")
    print("url:", [url])

    headers = {"Authorization": f"Token {LINKDING_TOKEN}"}
    
    bundles = await cache.get("linkding:bundles") or []
    all_tags = await cache.get("linkding:all_tags") or []
    metadata = {}
    bookmark_data = {}

    
    print("---------------------------------------------------")
    print("cache:all_tags:", all_tags)

    async with httpx.AsyncClient() as client:
        if not all_tags:
            try:
                t_res = await client.get(f"{LINKDING_URL}/api/tags/", headers=headers, timeout=5.0)
                results = t_res.json().get("results", [])
                if isinstance(results, list):
                    all_tags = [x["name"] for x in results if x.get("name")]
                    await cache.set("linkding:all_tags", all_tags, CacheStrategy.ONE_WEEK)
            except Exception as e:
                print(f"Error fetching tags from Linkding API. {e}")
        
        # 1. Fetch cached Bundles
        if not bundles:
            try:
                b_res = await client.get(f"{LINKDING_URL}/api/bundles/", headers=headers, timeout=5.0)
                if b_res.status_code == 200:
                    results = b_res.json().get("results", [])

                    if isinstance(results, list):
                        bundles = results
                        await cache.set("linkding_bundles", bundles, CacheStrategy.ONE_WEEK)
            except Exception as e:
                print(f"Error fetching bundles from Linkding API. {e}")

        # 2. Check if URL already exists
        if url:
            try:
                params = {"url": url}
                c_res = await client.get(f"{LINKDING_URL}/api/bookmarks/check/", headers=headers, timeout=5.0, params=params)
                if c_res.status_code == 200:
                    data = c_res.json()
                    print("Fetched bookmark data:")
                    print(data)
                    print("---------------------------------------------------")
                    bookmark_data = data.get("bookmark")
                    metadata = data.get("metadata")
                else:
                    print(f"Failed to check bookmark. Status code: {c_res.status_code}")
                    print(f"Response content: {c_res.text}")
            except Exception as e:
                print(f"Error fetching bookmark data from Linkding API. {e}")

    print("---------------------------------------------------")
    print("all_tags:", all_tags)
    print("bundles:", [x["all_tags"] for x in results if x.get("all_tags")])
    print("tags:", bookmark_data)
    print("metadata:", metadata)
    print("---------------------------------------------------")

    return templates.TemplateResponse(
        request=request, 
        name=f"dispatcher-{theme or 'light'}.html",
        context={
            "url": url, 
            "all_tags": all_tags,
            "available_tags": list(set(all_tags) - set([x["all_tags"] for x in results if x.get("all_tags")])),
            "bundles": bundles, 
            "bookmark": bookmark_data,
            "metadata": metadata
        }
    )


@app.get("/list", response_class=HTMLResponse)
async def get_dispatcher(request: Request, url: str = Query(""), theme: str | None = None):
    headers = {"Authorization": f"Token {LINKDING_TOKEN}"}
    bookmarks = []

    async with httpx.AsyncClient() as client:
        try:
            c_res = await client.get(f"{LINKDING_URL}/api/bookmarks/?limit=25&offset=0", headers=headers, timeout=5.0)
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
    headers = {"Authorization": f"Token {LINKDING_TOKEN}"}
    
    bundles = []
    metadata = {}
    bookmark_data = {}

    async with httpx.AsyncClient() as client:
        # 1. Fetch cached Bundles
        try:
            b_res = await client.get(f"{LINKDING_URL}/api/bundles/", headers=headers, timeout=5.0)
            if b_res.status_code == 200:
                bundles = b_res.json().get("results", [])
                print("Fetched bundles:")
                print(bundles)
        except Exception:
            pass

        # 2. Check if URL already exists
        if url:
            try:
                c_res = await client.get(f"{LINKDING_URL}/api/bookmarks/check/?url={url}", headers=headers, timeout=5.0)
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

# @app.post("/save-data")
# async def save_bookmark_data(data: SaveRequest):
#     return JSONResponse(status_code=200, content={"accepted": True, "data": data})

@app.post("/save", response_class=HTMLResponse)
# @app.post("/save")
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

    print("Saving bookmark with data:")
    print()
    print("------------------------------------------------")
    success = True
    error = None
    headers = {"Authorization": f"Token {LINKDING_TOKEN}"}
    tag_list = list(filter(None, set([bundle] + [t.strip() for t in tag_names.split(",")])))
    payload = {
        "url": url,
        "title": title,
        "tag_names": tag_list,
        "is_archived": is_archived,
        "description": description
    }

    print("---------------------------------------------------")
    print("bundle:", {"bundle": bundle})
    print("tag_names:", {"tag_names": tag_names})
    print("---------------------------------------------------")
    print("tag_list:", tag_list)
    print("bookmark_id:", {"bookmark_id": bookmark_id})
    print("---------------------------------------------------")

    async with httpx.AsyncClient() as client:
        try:
            if bookmark_id and bookmark_id != "0":
                # Update existing bookmark
                res = await client.put(f"{LINKDING_URL}/api/bookmarks/{bookmark_id}/", json=payload, headers=headers)
                print(f"Updating bookmark ID {bookmark_id} at {LINKDING_URL}/api/bookmarks/{bookmark_id}/")
            else:
                # Create new bookmark
                res = await client.post(f"{LINKDING_URL}/api/bookmarks/", json=payload, headers=headers)

            if res.status_code in (200, 201):
                data = res.json()
                print("Bookmark saved successfully. Response data:")
                print(data)
                print('------------------------------------------------')
                # data.get("detail", "No error details provided.")
                # await cache.reset()
            else:
                success = False
                data = res.json()
                error = f"{data.get("detail", {}).get("msg", "Unknown error")}"
                # return JSONResponse(status_code=res.status_code, content={"error": res.text})
                print(error)
        except Exception as e:
            print(f"Error fetching bookmark data from Linkding API. {e}")

    return templates.TemplateResponse(
        request=request, 
        name="response.html", 
        context={
            "url": url,
            "success": success,
            "error": error
        }
    )

@app.delete("/delete/{bookmark_id}")
async def delete_bookmark(bookmark_id: int):
    headers = {"Authorization": f"Token {LINKDING_TOKEN}"}
    async with httpx.AsyncClient() as client:
        res = await client.delete(f"{LINKDING_URL}/api/bookmarks/{bookmark_id}/", headers=headers)
        if res.status_code in (204, 200):
            return {"status": "deleted"}
        return JSONResponse(status_code=res.status_code, content={"error": res.text})