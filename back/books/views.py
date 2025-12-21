from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Book, Profile
from .serilizers import (
    BookCardSerializer,
    BookDetailSerializer,
    SignupSerializer,
    BooktiSubmitSerializer,
)
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

def _get_aladin_key():
    """
    settings에 키가 어떤 이름으로 들어있든 대응 (ALADIN_API_KEY / ALADIN_TTB_KEY)
    """
    return getattr(settings, "ALADIN_API_KEY", None) or getattr(settings, "ALADIN_TTB_KEY", None)


@api_view(["GET"])
def main_page(request):
    ttbkey = _get_aladin_key()
    if not ttbkey:
        return Response(
            {"detail": "알라딘 API 키가 없습니다. settings.ALADIN_API_KEY 또는 settings.ALADIN_TTB_KEY 확인"},
            status=500,
        )

    res = requests.get(
        "https://www.aladin.co.kr/ttb/api/ItemList.aspx",
        params={
            "ttbkey": ttbkey,
            "QueryType": "Bestseller",
            "MaxResults": 10,
            "SearchTarget": "Book",
            "Output": "js",        # ✅ 대문자 권장
            "Version": "20131101",
        },
        timeout=10,
    )

    # JSON 파싱 실패 시 원문 일부라도 보여주기
    try:
        data = res.json()
    except Exception:
        return Response(
            {
                "detail": "알라딘 응답이 JSON이 아닙니다. Output 파라미터/키를 확인하세요.",
                "status_code": res.status_code,
                "text_preview": res.text[:500],
            },
            status=502,
        )

    # 알라딘 자체 오류도 그대로 반환
    if data.get("errorCode"):
        return Response(
            {"detail": "알라딘 API 오류", "errorCode": data.get("errorCode"), "errorMessage": data.get("errorMessage")},
            status=502,
        )

    return Response(data)


@api_view(["GET"])
def book_detail(request, book_id):
    # ✅ get_list_or_404 -> get_object_or_404 (단건 조회)
    book = get_object_or_404(Book, id=book_id)
    serializer = BookDetailSerializer(book)
    return Response(serializer.data)


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "회원가입 성공!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "name": user.profile.name,
                    "birth_date": str(user.profile.birth_date),
                },
            },
            status=status.HTTP_201_CREATED,
        )


User = get_user_model()

AXIS_TAGS = {
    "P": ["실용서", "습관", "업무", "커리어"],
    "E": ["에세이", "힐링", "위로", "자기이해"],
    "F": ["입문", "기초", "정리", "베스트"],
    "C": ["신간", "트렌드", "추천", "새로운"],
    "L": ["핵심", "쉽게", "짧은", "요약"],
    "D": ["심화", "해설", "원리", "분석"],
    "R": ["몰입", "완독", "혼독", "집중"],
    "A": ["리뷰", "추천", "기록", "목록"],
}

TYPE_SPECIAL = {
    "PFLR": ["핵심정리", "업무"],
    "PFLA": ["리뷰", "습관"],
    "PFDR": ["전략", "프레임워크"],
    "PFDA": ["정리법", "노트"],
    "PCLR": ["트렌드", "신간"],
    "PCLA": ["추천목록", "베스트"],
    "PCDR": ["인사이트", "융합"],
    "PCDA": ["심화", "해설"],
    "EFLR": ["위로", "일상"],
    "EFLA": ["공감", "짧은감상"],
    "EFDR": ["장편", "몰입"],
    "EFDA": ["세계관", "해석"],
    "ECLR": ["분위기", "자유독서"],
    "ECLA": ["테마추천", "감성목록"],
    "ECDR": ["성찰", "문장"],
    "ECDA": ["메시지", "해석리뷰"],
}


def build_queries(bookti: str) -> list[str]:
    """
    알라딘 ItemSearch는 키워드를 많이 섞으면 0건이 되는 경우가 많아서,
    짧은 쿼리부터 여러 개 후보를 만들어 순차 시도한다.
    """
    bookti = (bookti or "").strip().upper()

    # 축별 대표 키워드(너무 구체적이면 결과가 안 나올 수 있으니 1개만)
    axis_keywords = []
    for ch in bookti:
        if ch in AXIS_TAGS:
            axis_keywords.append(AXIS_TAGS[ch][0])  # 축당 대표 1개

    # 유형별 특화 키워드 (2개 정도만)
    special = TYPE_SPECIAL.get(bookti, [])[:2]

    # ✅ 후보 쿼리 (짧은 것 → 긴 것)
    candidates = []

    # 1) 유형 특화 키워드가 있으면 그것만 먼저
    if special:
        candidates.append(" ".join(special))

    # 2) 목적(P/E)만 (실용서/에세이 등)
    if len(axis_keywords) >= 1:
        candidates.append(axis_keywords[0])

    # 3) 목적 + 범위 (예: 실용서 + 입문)
    if len(axis_keywords) >= 2:
        candidates.append(" ".join(axis_keywords[:2]))

    # 4) 목적 + 범위 + 깊이 (예: 실용서 입문 핵심)
    if len(axis_keywords) >= 3:
        candidates.append(" ".join(axis_keywords[:3]))

    # 5) 목적 + 범위 + 깊이 + (특화 1개)
    if len(axis_keywords) >= 3 and special:
        candidates.append(" ".join(axis_keywords[:3] + [special[0]]))

    # 6) 기존처럼 길게(마지막 fallback)
    long_query = " ".join(axis_keywords + special)
    if long_query:
        candidates.append(long_query)

    # 중복 제거
    dedup = []
    for q in candidates:
        q = q.strip()
        if q and q not in dedup:
            dedup.append(q)

    return dedup


@api_view(["POST"])
def bookti_submit(request):
    """
    body: { "user_id": 1, "bookti_code": "PFLR" }
    """
    serializer = BooktiSubmitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_id = serializer.validated_data["user_id"]
    bookti_code = serializer.validated_data["bookti_code"]

    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)

    profile.bookti_code = bookti_code
    profile.save()

    return Response(
        {"message": "BOOKTI 저장 완료", "user_id": user_id, "bookti_code": bookti_code},
        status=status.HTTP_200_OK,
    )

@api_view(["GET"])
def bookti_recommendations(request):
    """
    GET /api/bookti/recommendations/?bookti=PFLR
    """
    bookti = request.GET.get("bookti", "").strip().upper()
    if not bookti:
        return Response({"detail": "bookti query param이 필요합니다. 예) ?bookti=PFLR"}, status=400)

    ttbkey = _get_aladin_key()
    if not ttbkey:
        return Response(
            {"detail": "알라딘 API 키가 없습니다. settings.ALADIN_API_KEY 또는 settings.ALADIN_TTB_KEY 확인"},
            status=500,
        )

    queries = build_queries(bookti)
    tried = []

    for q in queries:
        tried.append(q)

        res = requests.get(
            "https://www.aladin.co.kr/ttb/api/ItemSearch.aspx",
            params={
                "ttbkey": ttbkey,
                "Query": q,
                "QueryType": "Keyword",
                "SearchTarget": "Book",
                "MaxResults": 12,
                "start": 1,
                "Sort": "SalesPoint",
                "Output": "js",
                "Version": "20131101",
            },
            timeout=10,
        )

        # JSON 파싱 실패
        try:
            data = res.json()
        except Exception:
            return Response(
                {
                    "detail": "알라딘 응답이 JSON이 아닙니다.",
                    "status_code": res.status_code,
                    "text_preview": res.text[:500],
                    "bookti": bookti,
                    "tried_queries": tried,
                },
                status=502,
            )

        # 알라딘 오류
        if data.get("errorCode"):
            return Response(
                {
                    "detail": "알라딘 API 오류",
                    "errorCode": data.get("errorCode"),
                    "errorMessage": data.get("errorMessage"),
                    "bookti": bookti,
                    "tried_queries": tried,
                },
                status=502,
            )

        items = data.get("item", []) or []
        if not items:
            continue  # 다음 후보 쿼리로 재시도

        simplified = []
        for it in items:
            simplified.append({
                "title": it.get("title"),
                "author": it.get("author"),
                "cover": it.get("cover"),
                "link": it.get("link"),
                "categoryName": it.get("categoryName"),
                "description": it.get("description"),
                "isbn13": it.get("isbn13"),
            })

        return Response(
            {
                "bookti": bookti,
                "query": q,              # ✅ 실제로 성공한 쿼리
                "tried_queries": tried,  # ✅ 어떤 쿼리를 시도했는지
                "items": simplified,
            },
            status=200,
        )

    # 끝까지 다 시도했는데도 없으면
    return Response(
        {
            "bookti": bookti,
            "query": queries[-1] if queries else "",
            "tried_queries": tried,
            "items": [],
            "detail": "알라딘 검색 결과가 없습니다. (쿼리/키워드 조합을 조정하세요)",
        },
        status=200,
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    profile = request.user.profile
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "name": profile.name,
        "birth_date": str(profile.birth_date),
        "bookti_code": profile.bookti_code,
    })