from fastapi import APIRouter  # router를 분리할 때 필요

from app.schemas.books_schema import BookCreate, BookResponse, BookUpdate

from typing import Optional

from fastapi import HTTPException, Query, Path

books_router = APIRouter(prefix="/books", tags=["도서"])

# DB 대신 사용할 딕셔너리
books_db: dict = {}

# 도서 등록 (POST /books)
@books_router.post("/books", response_model=BookResponse, status_code=201, tags=["도서"])
def create_book(book: BookCreate):
    """
    도서를 등록합니다.
    status_code=201 : 생성 성공을 의미하는 HTTP 코드
    """
    global next_id
    # Pydantic 객체를 딕셔너리로 변환 후 펼쳐주는 함수
    record = {"id": next_id, **book.model_dump()}

    books_db[next_id] = record  # 딕셔너리에 record 추가
    next_id += 1
    return record


# 도서 검색 (전체 도서목록, 개별 도서 검색)


# 전체도서 검색 (GET /books)
@books_router.get("/books", response_model=list[BookResponse], tags=["도서"])
def get_books(
    # Query Parameter : URL 뒤에 ?로 붙이는 쿼리스트링(선택적 옵션)
    category: Optional[str] = Query(
        None,
        description="카테고리 필터(예 : ?category=프로그래밍)",
    ),
):
    """
    도서 목록을 조회합니다.
    - ?category=프로그래밍 : 카테고리 필터
    """
    items = list(books_db.values())

    if category:
        items = [book for book in items if book["category"] == category]

    return items


# 개별도서 검색 (GET /books/{book_id}) - books_id : unique한 도서의 번호
@books_router.get("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def get_book(
    # Path Parameter : URL 경로에 포함된 값을 얻어올 때 사용
    book_id: int = Path(
        ...,
        ge=1,  # greater than or equals to
        description="도서 ID로 도서 검색 (ID는 1 이상)",
    ),
):
    """
    도서 ID로 도서 한 건 조회
    """
    if book_id not in books_db:
        raise HTTPException(
            status_code=404,
            detail=f"도서 {book_id}번을 찾을 수 없습니다.",
        )
    return books_db[book_id]


# 도서 수정 (PUT /books/{book_id})
@books_router.put("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def update_book(book_id: int, update: BookUpdate):
    """
    도서 정보를 수정합니다.
    변경할 필드만 보내도 됩니다. (나머지는 원래 값 유지됨)
    예 : {"price" : 200000} -> 가격만 변경
    """
    if book_id not in books_db:
        raise HTTPException(
            status_code=404,
            detail=f"도서 {book_id}번을 찾을 수 없습니다.",
        )

    # exclude_none=True None인 필드 제외
    changes = update.model_dump(exclude_none=True)

    # 딕셔너리의 모든 키를 순회하면 값을 변경
    for k, v in changes.items():
        books_db[book_id][k] = v  # book_id번 책의 k필드의 값을 v로 변경

    return books_db[book_id]


# 도서 삭제 (DELETE /books/{book_id})
@books_router.delete("/books/{book_id}", status_code=204, tags=["도서"])
def delete_book(book_id: int):
    """
    {book_id}번 도서를 삭제합니다
    status_code = 204. 삭제 성공
    """
    if book_id not in books_db:
        raise HTTPException(
            status_code=404,
            detail=f"도서 {book_id}번을 찾을 수 없습니다.",
        )

    del books_db[book_id]
    # status_code=204 -> 응답 본문이 없어도 됨. => return 생략 가능