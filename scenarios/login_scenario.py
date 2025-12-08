"""
시나리오 레이어: 로그인 기능 테스트 시나리오
각 시나리오는 PASS/FAIL 결과를 반환
"""
from playwright.sync_api import Page
from typing import Dict, Tuple
import time


class LoginScenario:
    """로그인 관련 테스트 시나리오를 실행하는 클래스"""

    def __init__(self, page: Page, base_url: str = "https://www.saucedemo.com"):
        """
        Args:
            page: Playwright Page 객체
            base_url: 테스트 대상 URL
        """
        self.page = page
        self.base_url = base_url

    def _navigate_to_login_page(self) -> None:
        """로그인 페이지로 이동"""
        self.page.goto(self.base_url)

    def _login(self, username: str, password: str) -> None:
        """로그인 수행"""
        self.page.locator('[data-test="username"]').fill(username)
        self.page.locator('[data-test="password"]').fill(password)
        self.page.locator('[data-test="login-button"]').click()
        time.sleep(0.5)  # 페이지 로드 대기

    def _is_login_successful(self) -> bool:
        """로그인 성공 여부 확인"""
        return "/inventory.html" in self.page.url

    def _get_error_message(self) -> str:
        """에러 메시지 텍스트 가져오기"""
        try:
            return self.page.locator('[data-test="error"]').text_content() or ""
        except:
            return ""

    def execute_test_case(self, test_data: Dict[str, str]) -> Tuple[str, str, str, str]:
        """
        테스트 케이스 실행

        Args:
            test_data: 테스트 데이터 (TC_ID, Feature, Given, Given_value, When, Then 등)

        Returns:
            Tuple[테스트ID, 기능명, 결과(PASS/FAIL), 에러메시지]
        """
        # Google Sheets 컬럼명에 맞게 매핑
        test_id = test_data.get('TC_ID', test_data.get('TESTCASE_ID', 'UNKNOWN'))
        feature = test_data.get('Feature', test_data.get('FEATURE', 'UNKNOWN'))
        given = test_data.get('Given', '')
        given_value = test_data.get('Given_value', '')
        when = test_data.get('When', '')
        then = test_data.get('Then', '')

        start_time = time.time()
        result = "FAIL"
        error_msg = ""

        try:
            # Given
            print(f"\n[시나리오 레이어] {test_id} 실행 시작")
            print(f"  Given: {given}")
            self._navigate_to_login_page()

            # When
            print(f"  When: {when}")

            # Given_value에서 아이디와 비밀번호 파싱
            username = ''
            password = ''

            if given_value:
                # "비밀번호" 키워드로 분리
                if '비밀번호' in given_value:
                    parts = given_value.split('비밀번호')
                    # 아이디 부분
                    if '아이디' in parts[0]:
                        username = parts[0].split(':', 1)[1].strip() if ':' in parts[0] else ''
                    # 비밀번호 부분
                    if len(parts) > 1 and ':' in parts[1]:
                        password = parts[1].split(':', 1)[1].strip()
                # 줄바꿈이 있는 경우 (기존 로직)
                elif '\n' in given_value:
                    lines = given_value.split('\n')
                    for line in lines:
                        if '아이디' in line or 'username' in line.lower():
                            username = line.split(':', 1)[1].strip() if ':' in line else ''
                        elif '비밀번호' in line or 'password' in line.lower():
                            password = line.split(':', 1)[1].strip() if ':' in line else ''

            # Username, Password 컬럼이 있으면 우선 사용
            username = test_data.get('Username', username)
            password = test_data.get('Password', password)

            self._login(username, password)

            # Then
            print(f"  Then: {then}")

            # 테스트 케이스별 검증 로직
            if "정상로그인" in feature or "정상 로그인" in feature or "successful" in feature.lower():
                if self._is_login_successful():
                    result = "PASS"
                else:
                    error_msg = "로그인 실패: inventory 페이지로 이동하지 않음"

            elif "비밀번호 오류" in feature or "비밀번호오류" in feature or "잘못된 비밀번호" in feature or "invalid password" in feature.lower():
                error = self._get_error_message()
                if error and "do not match" in error:
                    result = "PASS"
                else:
                    error_msg = f"예상한 에러 메시지가 표시되지 않음: {error}"

            elif "잠긴 계정" in feature or "잠긴계정" in feature or "locked" in feature.lower():
                error = self._get_error_message()
                if error and "locked out" in error.lower():
                    result = "PASS"
                else:
                    error_msg = f"예상한 에러 메시지가 표시되지 않음: {error}"

            elif "아이디 없음" in feature or "아이디없음" in feature or "아이디 공백" in feature or "empty username" in feature.lower():
                error = self._get_error_message()
                if error and "Username is required" in error:
                    result = "PASS"
                else:
                    error_msg = f"예상한 에러 메시지가 표시되지 않음: {error}"

            elif "비밀번호 없음" in feature or "비밀번호없음" in feature or "비밀번호 공백" in feature or "empty password" in feature.lower():
                error = self._get_error_message()
                if error and "Password is required" in error:
                    result = "PASS"
                else:
                    error_msg = f"예상한 에러 메시지가 표시되지 않음: {error}"

            else:
                error_msg = f"알 수 없는 테스트 케이스 유형: {feature}"

        except Exception as e:
            result = "FAIL"
            error_msg = str(e)

        elapsed_time = time.time() - start_time

        # 콘솔에 결과 출력
        status_color = '\033[92m' if result == "PASS" else '\033[91m'
        reset_color = '\033[0m'
        status_symbol = '✓' if result == "PASS" else '✗'

        print(f"{status_color}{'='*80}")
        print(f"테스트 결과: {status_symbol} {result}")
        print(f"테스트 ID: {test_id}")
        print(f"기능: {feature}")
        print(f"실행 시간: {elapsed_time:.2f}초")
        if error_msg:
            print(f"에러: {error_msg}")
        print(f"{'='*80}{reset_color}\n")

        return test_id, feature, result, error_msg


if __name__ == "__main__":
    # 테스트용 코드
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        scenario = LoginScenario(page)

        # 테스트 데이터 예시
        test_data = {
            'TESTCASE_ID': 'TESTCASE_001',
            'FEATURE': '정상 로그인',
            'Given': '로그인 페이지 접속',
            'When': '유효한 아이디와 비밀번호 입력',
            'Then': '로그인 성공',
            'Username': 'standard_user',
            'Password': 'secret_sauce'
        }

        result = scenario.execute_test_case(test_data)
        print(f"결과: {result}")

        browser.close()
