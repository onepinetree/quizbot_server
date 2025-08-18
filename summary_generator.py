
from google import genai
from pydantic import BaseModel
from typing import Optional, Literal
from dotenv import load_dotenv
import os
import asyncio
import json
import time

load_dotenv()


class SummaryGeneratorResponse(BaseModel):
    response_status: Literal['success', 'gemini_api_error']
    exception_message: Optional[str] = None
    result: Optional[str] = None



class SummaryGenerator:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    async def getSummary(self, script: str) -> SummaryGeneratorResponse:
        '''gemini api를 사용하여 스크립트 요약을 반환 (비동기 실행)'''

        max_try_count = 2
        current_try_count = 0

        while True:
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=''' 이 스크립트를 요약해줘.
                    스크립트: ''' + script,
                )

                result = json.loads(response.text)

                return SummaryGeneratorResponse(
                    response_status='success',
                    result=result
                )

            except Exception as e:
                if current_try_count < max_try_count:
                    current_try_count += 1
                    print(f'gemini api 재시도 중 {current_try_count}번째 시도, Exception: {e}')
                    continue
                else:
                    return SummaryGeneratorResponse(
                        response_status='gemini_api_error',
                        result='요약 생성 실패',
                        exception_message=f'gemini_api_error, {e}',
                    )


