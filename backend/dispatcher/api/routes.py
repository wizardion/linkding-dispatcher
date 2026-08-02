import asyncio

from arq import ArqRedis
from arq.jobs import Job
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from dispatcher.core import settings
from dispatcher.schemas.bookmark import BookmarkPayload
from dispatcher.schemas.jobs import JobDetails
from dispatcher.schemas.user import AuthUser
from dispatcher.services import BookmarkService, LinkdingService, UserSessionService

from .dependencies import (
    get_arq_pool,
    get_bookmark_service,
    get_session_service,
    get_user,
)

router = APIRouter(prefix="/bookmark")


@router.get("/check", response_model_by_alias=False)
async def check_bookmark(
    url: str = Query(""),
    bookark_service: BookmarkService = Depends(get_bookmark_service),
):
    bookmark = await bookark_service.check_bookmark(url)

    return {
        "url": bookmark.url if bookmark else url,
        "bookmark": bookmark.model_dump() if bookmark else None,
    }


@router.get("/metadata", response_model_by_alias=False)
async def check_bookmark_linkding(
    url: str = Query(""),
    user: AuthUser = Depends(get_user),
    bookark_service: BookmarkService = Depends(get_bookmark_service),
):
    bundles_set = await bookark_service.get_bundles_set()
    linkding_service = LinkdingService(user.token, settings.linkding, bundles_set)
    bookmark, metadata = await linkding_service.check_bookmark(url)

    return {
        "url": bookmark.url if bookmark else metadata.url if metadata else url,
        "bookmark": bookmark.model_dump() if bookmark else None,
        "metadata": metadata,
    }


@router.get("/info")
async def get_info(
    bookark_service: BookmarkService = Depends(get_bookmark_service),
    session_service: UserSessionService = Depends(get_session_service),
):
    async with asyncio.TaskGroup() as tg:
        bundles_task = tg.create_task(bookark_service.get_bundles())
        tags_task = tg.create_task(bookark_service.get_tags())

        user_preference = await session_service.get()

    all_tags = tags_task.result()
    bundles = bundles_task.result()

    return {
        "tags": all_tags,
        "bundles": bundles,
        "preference": user_preference,
    }


@router.get("/job/status/{job_id}")
async def get_job_status(request: Request, job_id: str):
    arq_pool: ArqRedis = request.app.state.arq_pool
    job = Job(job_id=job_id, redis=arq_pool)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found or already purged.")

    status = await job.status()

    if not status:
        raise HTTPException(status_code=404, detail="Status not found.")

    info = await job.result_info()
    return {
        "jobId": job.job_id,
        "status": status.value,
        "info": (
            JobDetails.model_validate(info).model_dump(by_alias=True) if info else None
        ),
    }


@router.post("/save", status_code=status.HTTP_202_ACCEPTED)
async def save_bookmark(
    bookmark: BookmarkPayload,
    response: Response,
    user: AuthUser = Depends(get_user),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    if not bookmark.url:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Bookmark URL is required."}

    job = await arq_pool.enqueue_job(
        "process_bookmark:save", user.token, bookmark.model_dump()
    )

    if not job:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Processing data is Unsuccessful."}

    return {"status": "processing", "jobId": job.job_id}


@router.delete("/{bookmark_id}", status_code=status.HTTP_202_ACCEPTED)
async def remove_bookmark(
    bookmark_id: int,
    response: Response,
    user: AuthUser = Depends(get_user),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    if not bookmark_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Bookmark ID is required."}

    job = await arq_pool.enqueue_job("process_bookmark:remove", user.token, bookmark_id)

    if not job:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Processing data is Unsuccessful."}

    return {"status": "processing", "jobId": job.job_id}


@router.post("/migrate", status_code=status.HTTP_202_ACCEPTED)
async def migrate_bookmarks(
    response: Response,
    user: AuthUser = Depends(get_user),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    job = await arq_pool.enqueue_job("process_bookmark:migrate", user.token)

    if not job:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Processing data is Unsuccessful."}

    return {"status": "processing", "jobId": job.job_id}
