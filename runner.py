"""
실행/리포트 레이어: 테스트 실행 및 결과 요약
Playwright 브라우저를 실행하고 모든 테스트케이스를 순차 실행
"""
from playwright.sync_api import sync_playwright, Browser, Page
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

from config import Config
from data.data_loader import DataLoader
from scenarios.login_scenario import LoginScenario
from scenarios.cart_scenario import CartScenario
from reports.report_generator import HTMLReportGenerator

# ============================================================================
# 새로운 시나리오 추가 방법
# ============================================================================
# 1. scenarios/ 폴더에 새 시나리오 파일 생성
#    예: scenarios/signup_scenario.py, scenarios/product_scenario.py
#
# 2. 아래에 시나리오 import 추가
#    예: from scenarios.signup_scenario import SignupScenario
#
# 3. SCENARIO_MAP에 키워드와 시나리오 클래스 추가
#    - url 파일의 라벨(예: "로그인")이 우선 적용
#    - 라벨이 없으면 Feature 컬럼에서 키워드 검색
# ============================================================================

# 시나리오 매핑 (키워드 → 시나리오 클래스)
# url 파일의 라벨이나 Feature 컬럼에 키워드가 포함되면 해당 시나리오 실행
SCENARIO_MAP = {
    '로그인': LoginScenario,
    '장바구니': CartScenario,
    # 새 시나리오 추가 예시:
    # '회원가입': SignupScenario,
    # '상품': ProductScenario,
}


class TestRunner:
    """테스트 실행 및 리포트 생성 클래스"""

    def __init__(self):
        """초기화"""
        self.config = Config()
        self.data_loader = DataLoader(
            self.config.URL_FILE_PATH,
            cache_dir=self.config.CACHE_DIR,
            scenarios_to_refresh=self.config.SCENARIOS_TO_REFRESH
        )
        self.results: List[Dict] = []
        self.browser: Browser = None
        self.page: Page = None
        self.report_dir = Path(self.config.REPORT_DIR)
        self.report_dir.mkdir(exist_ok=True)
        self.report_generator = HTMLReportGenerator(self.report_dir)

        # 로그 수집용 리스트
        self.console_logs: List[str] = []
        self.network_logs: List[str] = []

    def _setup_browser(self, playwright) -> None:
        """브라우저 설정 및 실행"""
        print("\n" + "="*80)
        print("[실행 레이어] 브라우저 초기화 중...")
        print(f"  - 브라우저 타입: {self.config.BROWSER_TYPE}")
        print(f"  - Headless: {self.config.HEADLESS}")
        print(f"  - SlowMo: {self.config.SLOW_MO}ms")
        print("="*80 + "\n")

        browser_options = self.config.get_browser_options()

        if self.config.BROWSER_TYPE == "chromium":
            self.browser = playwright.chromium.launch(**browser_options)
        elif self.config.BROWSER_TYPE == "firefox":
            self.browser = playwright.firefox.launch(**browser_options)
        elif self.config.BROWSER_TYPE == "webkit":
            self.browser = playwright.webkit.launch(**browser_options)
        else:
            raise ValueError(f"지원하지 않는 브라우저 타입: {self.config.BROWSER_TYPE}")

        self.page = self.browser.new_page()

        # 브라우저 콘솔 로그 수집
        def handle_console(msg):
            log_entry = f"[{msg.type.upper()}] {msg.text}"
            self.console_logs.append(log_entry)

        self.page.on("console", handle_console)

        # 네트워크 로그 수집 (요청/응답)
        def handle_request(request):
            log_entry = f"→ {request.method} {request.url}"
            self.network_logs.append(log_entry)

        def handle_response(response):
            log_entry = f"← {response.status} {response.url}"
            self.network_logs.append(log_entry)

        self.page.on("request", handle_request)
        self.page.on("response", handle_response)

        print("[실행 레이어] 콘솔 및 네트워크 로그 수집 활성화")

    def _teardown_browser(self) -> None:
        """브라우저 종료"""
        if self.browser:
            self.browser.close()
            print("\n[실행 레이어] 브라우저 종료 완료")

    def _take_screenshot(self, test_id: str) -> str:
        """스크린샷 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.report_dir / f"screenshot_{test_id}_{timestamp}.png"
            self.page.screenshot(path=str(screenshot_path))
            return str(screenshot_path)
        except Exception as e:
            print(f"  [경고] 스크린샷 저장 실패: {e}")
            return ""

    def run_all_tests(self) -> None:
        """모든 테스트 케이스 실행"""
        # 1. 데이터 로드
        print("\n" + "="*80)
        print("[실행 레이어] 테스트 데이터 로드 중...")
        print("="*80)
        test_data_list = self.data_loader.fetch_csv_data()

        # 2. Playwright 실행
        with sync_playwright() as playwright:
            self._setup_browser(playwright)

            # ========================================================================
            # 3. 시나리오 실행 (SCENARIO_MAP 기반 자동 선택)
            # ========================================================================

            for idx, test_data in enumerate(test_data_list, 1):
                test_id = test_data.get('TC_ID', test_data.get('TESTCASE_ID', f'TEST_{idx}'))
                feature = test_data.get('Feature', test_data.get('FEATURE', 'UNKNOWN'))
                source_label = test_data.get('_source_label', '')

                print(f"\n[{idx}/{len(test_data_list)}] {test_id} 실행 중...")

                # 시나리오 선택 (라벨 우선, Feature 보조)
                scenario = None
                selected_by = ""

                # 1. 먼저 라벨로 시나리오 선택 시도
                if source_label:
                    for keyword, scenario_class in SCENARIO_MAP.items():
                        if keyword.lower() in source_label.lower():
                            scenario = scenario_class(self.page, self.config.BASE_URL)
                            selected_by = f"라벨 '{source_label}' → 키워드 '{keyword}'"
                            break

                # 2. 라벨로 찾지 못하면 Feature 컬럼으로 시도
                if scenario is None:
                    for keyword, scenario_class in SCENARIO_MAP.items():
                        if keyword.lower() in feature.lower():
                            scenario = scenario_class(self.page, self.config.BASE_URL)
                            selected_by = f"Feature '{feature}' → 키워드 '{keyword}'"
                            break

                # 매칭되는 시나리오가 없으면 건너뛰기
                if scenario is None:
                    print(f"  ⚠️  알 수 없는 시나리오: 라벨='{source_label}', Feature='{feature}'")
                    print(f"     SCENARIO_MAP에 추가 필요")
                    continue

                print(f"  [시나리오 선택] {scenario.__class__.__name__} ({selected_by})")

                # 로그 초기화 (각 테스트마다 새로 수집)
                self.console_logs.clear()
                self.network_logs.clear()

                # 시나리오 실행
                start_time = datetime.now()
                test_id, feature, result, error_msg = scenario.execute_test_case(test_data)
                end_time = datetime.now()
                elapsed_time = (end_time - start_time).total_seconds()

                # 실패 시 스크린샷
                screenshot_path = ""
                if result == "FAIL" and self.config.SCREENSHOT_ON_FAILURE:
                    screenshot_path = self._take_screenshot(test_id)

                # 로그 복사 (실패 시만 저장)
                console_log_copy = list(self.console_logs) if result == "FAIL" else []
                network_log_copy = list(self.network_logs) if result == "FAIL" else []

                # 결과 저장
                self.results.append({
                    'test_id': test_id,
                    'feature': feature,
                    'result': result,
                    'elapsed_time': elapsed_time,
                    'screenshot': screenshot_path,
                    'error_msg': error_msg if result == "FAIL" else "",
                    'console_logs': console_log_copy,
                    'network_logs': network_log_copy,
                    'timestamp': start_time.strftime("%Y-%m-%d %H:%M:%S")
                })

                # 실패 시 중단 옵션
                if result == "FAIL" and self.config.STOP_ON_FAILURE:
                    print("\n[실행 레이어] 테스트 실패로 인해 실행 중단")
                    break

            # 4. 브라우저 종료
            self._teardown_browser()

    def generate_summary(self) -> None:
        """테스트 결과 요약 출력"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['result'] == 'PASS')
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print("\n" + "="*80)
        print("테스트 실행 결과 요약")
        print("="*80)
        print(f"총 테스트: {total}개")
        print(f"성공: \033[92m{passed}개\033[0m")
        print(f"실패: \033[91m{failed}개\033[0m")
        print(f"성공률: {pass_rate:.1f}%")
        print("="*80)

        # 전체 테스트 결과 상세 출력
        print("\n" + "="*80)
        print("전체 테스트 케이스 상세 결과")
        print("="*80)
        for idx, result in enumerate(self.results, 1):
            status = '✓ PASS' if result['result'] == 'PASS' else '✗ FAIL'
            color = '\033[92m' if result['result'] == 'PASS' else '\033[91m'
            reset = '\033[0m'

            print(f"\n[{idx}/{total}] {color}{status}{reset}")
            print(f"  테스트 ID: {result['test_id']}")
            print(f"  기능: {result['feature']}")
            print(f"  실행 시간: {result['elapsed_time']:.2f}초")
            print(f"  타임스탬프: {result['timestamp']}")

            if result['result'] == 'FAIL':
                if result['error_msg']:
                    print(f"  {color}에러: {result['error_msg']}{reset}")
                if result['screenshot']:
                    print(f"  스크린샷: {result['screenshot']}")
                if result['console_logs']:
                    print(f"  콘솔 로그: {len(result['console_logs'])}개")
                if result['network_logs']:
                    print(f"  네트워크 로그: {len(result['network_logs'])}개")

        # 실패한 테스트 요약 (있는 경우)
        if failed > 0:
            print("\n" + "="*80)
            print("실패한 테스트 요약")
            print("="*80)
            for idx, result in enumerate(self.results, 1):
                if result['result'] == 'FAIL':
                    print(f"\n✗ [{idx}] {result['test_id']}")
                    print(f"   기능: {result['feature']}")
                    print(f"   에러: {result['error_msg']}")
                    if result['screenshot']:
                        print(f"   스크린샷: {result['screenshot']}")

    def save_reports(self) -> Tuple[str, str]:
        """HTML 및 JSON 리포트 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        config_data = {
            'headless': self.config.HEADLESS,
            'browser': self.config.BROWSER_TYPE,
            'base_url': self.config.BASE_URL
        }

        # HTML 리포트 생성
        html_file = self.report_generator.generate_html_report(
            results=self.results,
            config=config_data,
            timestamp=timestamp
        )

        # JSON 리포트 생성
        json_file = self.report_generator.save_json_report(
            results=self.results,
            config=config_data,
            timestamp=timestamp
        )

        return html_file, json_file

    def run(self) -> int:
        """
        테스트 실행 메인 함수

        Returns:
            int: 종료 코드 (0: 성공, 1: 실패)
        """
        start_time = datetime.now()

        print("\n" + "╔" + "="*78 + "╗")
        print("║" + " "*20 + "테스트 자동화 프레임워크 시작" + " "*28 + "║")
        print("╚" + "="*78 + "╝")

        try:
            # 테스트 실행
            self.run_all_tests()

            # 결과 요약
            self.generate_summary()

            # HTML 및 JSON 리포트 저장
            html_file, json_file = self.save_reports()
            print(f"\n[리포트] HTML: {html_file}")
            print(f"[리포트] JSON: {json_file}")

        except Exception as e:
            print(f"\n\033[91m[에러] 테스트 실행 중 오류 발생: {e}\033[0m")
            return 1

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        print(f"\n총 실행 시간: {total_time:.2f}초")
        print("="*80 + "\n")

        # 실패한 테스트가 있으면 종료 코드 1 반환
        failed_count = sum(1 for r in self.results if r['result'] == 'FAIL')
        return 1 if failed_count > 0 else 0


def main():
    """메인 실행 함수"""
    runner = TestRunner()
    exit_code = runner.run()
    exit(exit_code)


if __name__ == "__main__":
    main()
