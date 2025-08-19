from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import asyncio
import logging

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ScriptExtractor:
    def __init__(self, url: str):
        logger.info(f"ScriptExtractor 초기화 시작 - URL: {url}")
        
        # Webshare 프록시 설정
        proxy_config = WebshareProxyConfig(
            proxy_username="auvuympl",
            proxy_password="cywxjxsjhr8a",
            filter_ip_locations=["de", "us"],
        )
        
        self._youtube_transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        logger.info("Webshare 프록시 설정으로 YouTubeTranscriptApi 초기화 완료")
        
        self._video_id = self._get_video_id(url)
        self._languages = ['ko', 'en']
        self._error_message = "자막을 불러올 수 없습니다: {}"
        self._url = url
        logger.info(f"ScriptExtractor 초기화 완료 - Video ID: {self._video_id}, 지원 언어: {self._languages}")

    def _get_video_id(self, url: str) -> str:
        """
        유튜브 링크에서 video_id만 추출 (private method)
        예: https://www.youtube.com/watch?v=12345 -> 12345
        """
        logger.debug(f"Video ID 추출 시작 - URL: {url}")
        
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            logger.info(f"Video ID 추출 성공 (watch?v= 형식) - ID: {video_id}")
            return video_id
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            logger.info(f"Video ID 추출 성공 (youtu.be/ 형식) - ID: {video_id}")
            return video_id
        else:
            logger.error(f"지원되지 않는 URL 형식: {url}")
            raise ValueError("올바른 유튜브 URL을 넣어주세요.")

    async def _fetch_transcript(self) -> list:
        """
        자막 데이터를 가져오는 private method (비동기)
        """
        logger.info(f"자막 데이터 가져오기 시작 - Video ID: {self._video_id}, 언어: {self._languages}")
        
        try:
            fetched_transcript = await asyncio.to_thread(
                self._youtube_transcript_api.fetch,
                self._video_id, 
                languages=self._languages
            )
            
            logger.info(f"자막 데이터 가져오기 성공 - 자막 개수: {len(fetched_transcript)}")
            logger.debug(f"자막 데이터 샘플: {fetched_transcript[:3] if len(fetched_transcript) > 3 else fetched_transcript}")
            return fetched_transcript
            
        except Exception as e:
            logger.error(f"자막 데이터 가져오기 실패 - Video ID: {self._video_id}, 오류: {str(e)}")
            return []

    def _process_transcript(self, transcript_data: list) -> str:
        """
        자막 데이터를 처리하여 문자열로 변환하는 private method
        """
        logger.info(f"자막 데이터 처리 시작 - 데이터 개수: {len(transcript_data)}")
        
        if not transcript_data:
            logger.warning("자막 데이터가 비어있음")
            return self._error_message.format("자막 데이터가 없습니다")
        
        try:
            result = " ".join([snippet.text for snippet in transcript_data])
            logger.info(f"자막 데이터 처리 성공 - 결과 길이: {len(result)} 문자")
            logger.debug(f"처리된 자막 미리보기: {result[:100]}...")
            return result
        except Exception as e:
            logger.error(f"자막 데이터 처리 실패 - 오류: {str(e)}")
            return self._error_message.format(f"자막 처리 중 오류: {e}")

    def _handle_error(self, error: Exception) -> str:
        """
        에러를 처리하는 private method
        """
        logger.error(f"에러 처리 - 에러 타입: {type(error).__name__}, 메시지: {str(error)}")
        return self._error_message.format(str(error))

    async def extract_script(self) -> str:
        """
        유튜브 영상에서 자막을 추출하는 public method (비동기)
        
        Returns:
            str: 추출된 자막 텍스트
        """
        logger.info(f"자막 추출 프로세스 시작 - URL: {self._url}")
        
        try:
            transcript_data = await self._fetch_transcript()
            result = self._process_transcript(transcript_data)
            
            if result.startswith("자막을 불러올 수 없습니다"):
                logger.warning(f"자막 추출 완료 (오류 포함): {result}")
            else:
                logger.info(f"자막 추출 프로세스 성공적으로 완료 - 결과 길이: {len(result)} 문자")
            
            return result
            
        except Exception as e:
            logger.error(f"자막 추출 프로세스 실패 - 오류: {str(e)}")
            return self._handle_error(e)


if __name__ == "__main__":
    # 테스트 실행 (비동기)
    async def main():
        logger.info("=== ScriptExtractor 테스트 시작 ===")
        youtube_url = "https://www.youtube.com/watch?v=ozW7y-y6Ymw"
        
        # ScriptExtractor 인스턴스 생성
        extractor = ScriptExtractor(youtube_url)
        
        # 자막 추출
        script = await extractor.extract_script()
        print("추출된 자막:")
        print(script)
        logger.info("=== ScriptExtractor 테스트 완료 ===")
    
    # 이미 실행 중인 이벤트 루프가 있는 경우 대비
    try:
        asyncio.run(main())
    except RuntimeError:
        # Jupyter 노트북 등에서 실행할 때
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(main())
