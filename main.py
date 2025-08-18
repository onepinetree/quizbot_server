import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
import uvicorn
from pydantic import BaseModel, Field
from typing import Literal, Optional
import os
import logging
import json
from dotenv import load_dotenv
# 사용하지 않는 import들 제거
from script_extractor import ScriptExtractor
from summary_generator import SummaryGenerator
load_dotenv()


app = FastAPI()



### 새로 설정한 부분 시작
# CORS 설정
ALLOWED_ORIGINS = [
    "https://quizbot-yqez.onrender.com",  # <<<<< 배포된 프론트엔드 페이지 넣기
    "http://127.0.0.1:5500",                     # 로컬 Live Server
    "http://localhost:5500",                     # 로컬 개발 환경
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,                      # 쿠키/인증 미사용 시 False
    allow_methods=["POST", "OPTIONS"],           # POST, OPTIONS 허용
    allow_headers=["Content-Type", "Accept", "*"],  # 헤더 허용
    max_age=86400,                                # 프리플라이트 응답 캐시 시간 (24시간)
)
### 새로 설정한 부분 끝

# 로깅 설정 (시간 제거)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s - %(message)s"
)
logger = logging.getLogger("fastapi-logger")

# OpenAI 및 HTTP 라이브러리 로그 수준 조정
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)






# 유튜브 자막 추출 및 요약 API 엔드포인트
class YouTubeUrlRequest(BaseModel):
    youtube_url: str = Field(..., description="유튜브 URL")

class YouTubeSummaryResponse(BaseModel):
    response_status: Literal['success', 'script_error', 'summary_error']
    summary: Optional[str] = None
    error_message: Optional[str] = None

@app.post("/youtube-summary", response_model=YouTubeSummaryResponse)
async def get_youtube_summary(request: YouTubeUrlRequest):
    """
    유튜브 URL을 받아서 자막을 추출하고 요약을 생성하는 API
    """
    try:
        # 1. 자막 추출
        script_extractor = ScriptExtractor(request.youtube_url)
        script = script_extractor.extract_script()
        
        if not script or script.startswith("자막을 불러올 수 없습니다"):
            return YouTubeSummaryResponse(
                response_status='script_error',
                error_message=f"자막 추출 실패: {script}"
            )
        
        # 2. 요약 생성
        summary_generator = SummaryGenerator()
        summary_response = await summary_generator.getSummary(script)
        
        if summary_response.response_status == 'success':
            return YouTubeSummaryResponse(
                response_status='success',
                summary=summary_response.result
            )
        else:
            return YouTubeSummaryResponse(
                response_status='summary_error',
                error_message=summary_response.exception_message
            )
            
    except Exception as e:
        return YouTubeSummaryResponse(
            response_status='summary_error',
            error_message=f"API 실행 중 오류 발생: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

