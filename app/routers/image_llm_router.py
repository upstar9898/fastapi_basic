# 파일 위치 : fastapi_basic/app/routers/llm_router.py
# 역할 : HTTP 요청(클라이언트가 보낸 request(클라이어트가 보낸 모든 요청정보(데이터포함)))을 받아, Service단을 호출하고,
#       Client에게 응답을 반환한다.

from fastapi import APIRouter  # router를 분리할 때 필요
from fastapi import UploadFile, File, Form, HTTPException
from app.schemas.image_llm import ImageAnalysisResponse, TextSummaryResponse

image_llm_router = APIRouter(prefix="/imagellm", tags=["LLM"])


# "/imagellm/analyze_image"
@image_llm_router.POST(
    "/analyaze_image",
    response_model=ImageAnalysisResponse,
    status_code=201,
    tags=["LLM 이미지분석"],
    summary="이미지 설명 생성(Vision Model API 이용)",
)
