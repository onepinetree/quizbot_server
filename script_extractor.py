from youtube_transcript_api import YouTubeTranscriptApi
import asyncio

class ScriptExtractor:
    def __init__(self, url: str):
        self._youtube_transcript_api = YouTubeTranscriptApi()
        self._video_id = self._get_video_id(url)
        self._languages = ['ko', 'en']
        self._error_message = "자막을 불러올 수 없습니다: {}"
        self._url = url

    def _get_video_id(self, url: str) -> str:
        """
        유튜브 링크에서 video_id만 추출 (private method)
        예: https://www.youtube.com/watch?v=12345 -> 12345
        """
        if "watch?v=" in url:
            return url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("올바른 유튜브 URL을 넣어주세요.")

    async def _fetch_transcript(self) -> list:
        """
        자막 데이터를 가져오는 private method (비동기)
        """
        try:
            fetched_transcript = await asyncio.to_thread(
                self._youtube_transcript_api.fetch,
                self._video_id, 
                languages=self._languages
            )
            
            return fetched_transcript
            
        except Exception as e:
            return []

    def _process_transcript(self, transcript_data: list) -> str:
        """
        자막 데이터를 처리하여 문자열로 변환하는 private method
        """
        if not transcript_data:
            return self._error_message.format("자막 데이터가 없습니다")
        
        try:
            result = " ".join([snippet.text for snippet in transcript_data])
            return result
        except Exception as e:
            return self._error_message.format(f"자막 처리 중 오류: {e}")

    def _handle_error(self, error: Exception) -> str:
        """
        에러를 처리하는 private method
        """
        return self._error_message.format(str(error))

    async def extract_script(self) -> str:
        """
        유튜브 영상에서 자막을 추출하는 public method (비동기)
        
        Returns:
            str: 추출된 자막 텍스트
        """
        try:
            transcript_data = await self._fetch_transcript()
            return self._process_transcript(transcript_data)
            
        except Exception as e:
            return self._handle_error(e)


if __name__ == "__main__":
    # 테스트 실행 (비동기)
    async def main():
        youtube_url = "https://www.youtube.com/watch?v=ozW7y-y6Ymw"
        
        # ScriptExtractor 인스턴스 생성
        extractor = ScriptExtractor(youtube_url)
        
        # 자막 추출
        script = await extractor.extract_script()
        print("추출된 자막:")
        print(script)
    
    asyncio.run(main())
