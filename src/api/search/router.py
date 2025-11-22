from fastapi import APIRouter, HTTPException
from src.logger import get_logger
from src.api.search import service as search_service
from src.api.search.schemas import SearchUserResult, SearchBlogsResult

logger = get_logger()
router = APIRouter(
    prefix="/search",
    tags=["search"],
)

from fastapi import APIRouter, Depends, status, Path, Query

@router.get(
    "/user",
    response_model=SearchUserResult,
    status_code=status.HTTP_200_OK,
    summary="Search user by username",
    description=(
        "Search for a user by username and return the user info plus a paginated list "
        "of blogs authored by that user."
    ),
)
async def search_user_endpoint(
    username: str = Query(..., min_length=1, description="Exact username to search"),
    #page: int = Query(1, ge=1, description="Page number (1-based) for the user's blogs"),
    #size: int = Query(10, ge=1, le=50, description="Page size for the user's blogs"),
):
    """
    Search by username:
    - If the user exists: return username and user_id
    - If the user does not exist: user = null
    """
    #logger.info("Search user by username, username=%s, page=%s, size=%s", username, page, size)
    logger.info("Search user by username, username=%s", username)
    result = await search_service.search_user_with_blogs(
        username=username,
        #page=page,
        #size=size,
    )
    return result


@router.get(
    "/blogs",
    response_model=SearchBlogsResult,
    status_code=status.HTTP_200_OK,
    summary="Search blogs by title keyword",
    description=(
        "Search blogs whose title contains the given keyword (case-insensitive), "
        "and return a paginated list of blog previews."
    ),
)
async def search_blogs_endpoint(
    keyword: str = Query(..., min_length=1, description="Keyword to match in blog titles"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(10, ge=1, le=50, description="Page size"),
):
    """
    Search blog titles by keyword:
    - Title contains the keyword (case-insensitive)
    - Return the paginated results
    """
    logger.info("Search blogs by keyword, keyword=%s, page=%s, size=%s", keyword, page, size)
    result = await search_service.search_blogs_by_keyword(
        keyword=keyword,
        page=page,
        size=size,
    )
    return result