"""
프레임워크 설정 파일
브라우저 옵션, 테스트 URL 등 설정 관리
"""


class Config:
    """테스트 프레임워크 설정"""

    # ========================================
    # 브라우저 설정
    # ========================================
    # 브라우저 표시 여부 (True/False 중 하나만 선택)
    #HEADLESS = True   # 브라우저 숨김 (빠른 실행, CI/CD용)
    HEADLESS = False  # 브라우저 보임 (디버깅용)

    SLOW_MO = 0  # 각 동작 사이 지연 시간(ms), 0이면 최대 속도
    BROWSER_TYPE = "chromium"  # chromium, firefox, webkit 중 선택

    # 테스트 URL
    BASE_URL = "https://www.saucedemo.com"

    # 데이터 설정
    URL_FILE_PATH = "url"  # Google Sheets URL이 저장된 파일

    # ========================================
    # Google Sheets 다운로드 설정
    # ========================================
    # 새로 다운로드할 시나리오 목록 (라벨 기준)
    # 예: ['로그인']           → 로그인만 다운로드, 나머지는 캐시 사용
    # 예: ['로그인', '장바구니'] → 둘 다 다운로드
    # 예: []                  → 모두 캐시 사용 (가장 빠름)
    SCENARIOS_TO_REFRESH = []  # 빈 리스트면 모두 로컬 캐시 사용

    # 캐시 디렉토리
    CACHE_DIR = "data/cache"

    # 리포트 설정
    REPORT_DIR = "reports"
    SCREENSHOT_ON_FAILURE = True  # 실패 시 스크린샷 저장 여부

    # 실행 옵션
    STOP_ON_FAILURE = False  # True: 실패 시 즉시 중단, False: 모든 테스트 실행

    @classmethod
    def get_browser_options(cls) -> dict:
        """브라우저 실행 옵션 반환"""
        return {
            "headless": cls.HEADLESS,
            "slow_mo": cls.SLOW_MO
        }

    @classmethod
    def toggle_headless(cls) -> None:
        """headless 모드 토글 (디버깅용)"""
        cls.HEADLESS = not cls.HEADLESS
        print(f"[설정] Headless 모드: {cls.HEADLESS}")


if __name__ == "__main__":
    # 설정 확인
    print("=== 현재 설정 ===")
    print(f"브라우저 타입: {Config.BROWSER_TYPE}")
    print(f"Headless: {Config.HEADLESS}")
    print(f"SlowMo: {Config.SLOW_MO}ms")
    print(f"Base URL: {Config.BASE_URL}")
    print(f"URL 파일: {Config.URL_FILE_PATH}")
    print(f"리포트 디렉토리: {Config.REPORT_DIR}")
