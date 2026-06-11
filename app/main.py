# ============================================================
# 파일 위치: book_api/app/main.py
# 실행 방법: uvicorn app.main:app --reload
# ============================================================
# FastAPI:
# - FastAPI 애플리케이션 객체를 만들 때 사용합니다.
# - 이 객체에 GET, POST, PUT, DELETE 같은 API 주소를 등록합니다.
#
# HTTPException:
# - API 처리 중 오류가 발생했을 때 HTTP 상태 코드와 메시지를 반환할 때 사용합니다.
# - 예: 없는 도서를 조회하면 404 Not Found를 반환합니다.
#
# Path:
# - URL 경로에 포함되는 값을 검증할 때 사용합니다.
# - 예: /books/1 에서 1은 book_id라는 Path Parameter입니다.
#
# Query:
# - URL 뒤에 ?key=value 형태로 붙는 값을 검증할 때 사용합니다.
# - 예: /books?category=프로그래밍 에서 category는 Query Parameter입니다.

from pathlib import Path as FilePath

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# List:
# - 여러 개의 데이터를 리스트 형태로 반환할 때 타입 힌트로 사용합니다.
# - 예: List[BookResponse]는 BookResponse 여러 개를 담은 리스트라는 뜻입니다.
#
# Optional:
# - 값이 있을 수도 있고 없을 수도 있음을 의미합니다.
# - 예: Optional[str]은 문자열이거나 None일 수 있습니다.

from app.routers.llm_router import llm_router
from app.routers.books_router import books_router
from app.routers.file_llm_router import file_llm_router

from dotenv import load_dotenv

load_dotenv()

# FastAPI 객체 생성
app = FastAPI(
    title="도서관리 API",
    description="FastAPI 기초 실습 - 도서관리 CRUD를 할 수 있는 엔드포인트",
    version="1.0.0",
)  # APIRouter를 함께 가지고 있다.

# 라우터 추가 등록
app.include_router(llm_router)
app.include_router(books_router)
app.include_router(file_llm_router)

# CORS 설정: 브라우저(프론트엔드)에서 API를 호출할 수 있게 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# frontend 폴더 경로 (프로젝트 루트/frontend)
frontend_dir = FilePath(__file__).resolve().parent.parent / "frontend"


# ------------------------------------
# 서버 상태 확인용 API
# ------------------------------------
@app.get("/health", summary="서버 상태 확인", tags=["시스템"])
def health_check():
    """
    서버가 정상적으로 실행 중인지 확인하는 API입니다.
    실무에서는 health check API를 자주 사용합니다.
    예:
    - 서버 배포 후 정상 실행 여부 확인
    - 로드밸런서가 서버 상태 확인
    - 모니터링 시스템이 주기적으로 호출
    요청:
    GET /health
    응답:
    {
        "status": "ok",
        "version": "1.0.0"
    }
    """
    # 딕셔너리를 FastAPI가 자동으로 json으로 변환한다.
    return {"status": "ok", "version": "1.0.0"}


# ----------------------------------------------
# 프론트엔드 페이지 제공 (맨 마지막에 등록)
# - http://127.0.0.1:8000/         → index.html
# - http://127.0.0.1:8000/frontend/ → index.html
# ----------------------------------------------
@app.get("/", include_in_schema=False)
def serve_root_page():
    """루트 주소 접속 시 프론트엔드 페이지를 바로 보여줍니다."""
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(
            status_code=404, detail="frontend/index.html 파일을 찾을 수 없습니다."
        )
    return FileResponse(index_file)


@app.get("/frontend", include_in_schema=False)
def redirect_frontend():
    """/frontend → /frontend/ 로 이동 (슬래시 없이 접속해도 동작)"""
    return RedirectResponse(url="/frontend/")


# StaticFiles는 반드시 API 라우트 등록 후 맨 마지막에 mount
if frontend_dir.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(frontend_dir), html=True),
        name="frontend",
    )
