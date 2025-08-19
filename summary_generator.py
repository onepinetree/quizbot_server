
from google import genai
from pydantic import BaseModel
from typing import Optional, Literal
from dotenv import load_dotenv
import os
import asyncio
import json
import time
import logging

load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class SummaryGeneratorResponse(BaseModel):
    response_status: Literal['success', 'gemini_api_error']
    exception_message: Optional[str] = None
    result: Optional[str] = None



class SummaryGenerator:

    def __init__(self):
        logger.info("SummaryGenerator 초기화 시작")
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            logger.error("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다")
            raise ValueError("GOOGLE_API_KEY가 필요합니다")
        
        self.client = genai.Client(api_key=api_key)
        logger.info("SummaryGenerator 초기화 완료 - Gemini 클라이언트 준비됨")

    async def getSummary(self, script: str) -> SummaryGeneratorResponse:
        '''gemini api를 사용하여 스크립트 요약을 반환 (비동기 실행)'''

        logger.info(f"요약 생성 시작 - 입력 스크립트 길이: {len(script)} 문자")
        logger.debug(f"입력 스크립트 미리보기: {script[:100]}...")

        max_try_count = 2
        current_try_count = 0

        while True:
            try:
                logger.info(f"Gemini API 호출 시도 - 시도 횟수: {current_try_count + 1}/{max_try_count + 1}")
                
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=''' 이 스크립트를 요약해줘.
                    스크립트: ''' + script,
                )

                logger.info("Gemini API 응답 수신 성공")
                logger.debug(f"API 응답 원본: {response.text[:200]}...")

                result = json.loads(response.text)
                logger.info(f"JSON 파싱 성공 - 결과 타입: {type(result)}")

                return SummaryGeneratorResponse(
                    response_status='success',
                    result=result
                )

            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류 - 응답을 문자열로 처리: {str(e)}")
                # JSON 파싱 실패 시 텍스트 그대로 반환
                return SummaryGeneratorResponse(
                    response_status='success',
                    result=response.text if 'response' in locals() else "응답 파싱 실패"
                )

            except Exception as e:
                current_try_count += 1
                logger.warning(f"Gemini API 오류 발생 - 시도 {current_try_count}/{max_try_count + 1}, 오류: {str(e)}")
                
                if current_try_count <= max_try_count:
                    logger.info(f"재시도 대기 중... (잠시 후 {current_try_count}번째 재시도)")
                    await asyncio.sleep(1)  # 1초 대기 후 재시도
                    continue
                else:
                    logger.error(f"모든 재시도 실패 - 최종 오류: {str(e)}")
                    return SummaryGeneratorResponse(
                        response_status='gemini_api_error',
                        result='요약 생성 실패',
                        exception_message=f'gemini_api_error, {e}',
                    )

