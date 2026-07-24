# 파일 위치 : fastapi_basic/app/routers/llm_router.py
# 역할 : HTTP 요청(클라이언트가 보낸 request(클라이어트가 보낸 모든 요청정보(데이터포함)))을 받아, Service단을 호출하고,
#       Client에게 응답을 반환한다.

from fastapi import APIRouter  # router를 분리할 때 필요
from fastapi import UploadFile, File, Form, HTTPException, Depends
from app.schemas.file_llm import (
    ImageAnalysisResponse,
    TextSummaryResponse,
    ImageAnalysisForm,
    TextSummaryForm,
)

from app.services.file_analyze_service import (
    validate_image,
    analyze_image_with_llm,
    validate_text_file,
    summarize_text_with_llm,
)

file_llm_router = APIRouter(prefix="/imagellm", tags=["LLM"])


# "/imagellm/analyze_image"
# 파일 + 텍스트 함께 받기
# JSON Body와 File은 함께 쓸 수가 없다
# Form : 나머지 텍스트 데이터를 받는.. (form 태그의 데이터)
@file_llm_router.post(
    "/analyaze_image",
    response_model=ImageAnalysisResponse,
    status_code=201,
    tags=["LLM 이미지분석"],
    summary="이미지 설명 생성(Vision Model API 이용)",
)
async def analyze_image(
    file: UploadFile = File(...),  # 이미지 파일
    form: ImageAnalysisForm = Depends(),  # 나머지 텍스트 데이터
):
    """
    이미지를 업로드하면 GPT-4o Vision이 설명을 생성합니다.

    Form 파라미터:
    - `prompt`  : 분석 지시 (기본값 제공)
    - `language`: 출력 언어 ko/en
    """
    contents = await file.read()  # 파일 읽기
    validate_image(file.content_type, len(contents))  # 검증

    result = await analyze_image_with_llm(contents, form.prompt, form.language)
    return ImageAnalysisResponse(
        filename=file.filename,
        size_bytes=len(contents),
        description=result.get("description", ""),
        objects=result.get("objects", []),
        mood=result.get("mood", ""),
    )


@file_llm_router.post(
    "/text",
    response_model=TextSummaryResponse,
    status_code=201,
    summary="텍스트 파일 요약",
)
async def analyze_text_file(
    file: UploadFile = File(..., description="요약할 텍스트 파일 (.txt)"),
    form: TextSummaryForm = Depends(),  # Form 파라미터 묶음 주입
):
    """
    텍스트 파일을 업로드하면 GPT-4o가 요약합니다.

    Form 파라미터:
    - `max_length`: 요약 최대 길이 (기본값 200)
    - `language`  : 출력 언어 ko/en
    """
    contents = await file.read()
    text = contents.decode("utf-8", errors="ignore")

    validate_text_file(file.content_type, len(contents), text)  # 검증

    summary = await summarize_text_with_llm(  # LLM
        text, form.max_length, form.language
    )

    return TextSummaryResponse(
        filename=file.filename or "unknown.txt",
        original_length=len(text),
        summary=summary,
    )
