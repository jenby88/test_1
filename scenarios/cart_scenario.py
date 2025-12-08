"""
시나리오 레이어: 장바구니 기능 테스트 시나리오
각 시나리오는 PASS/FAIL 결과를 반환
"""
from playwright.sync_api import Page
from typing import Dict, Tuple
import time


class CartScenario:
    """장바구니 관련 테스트 시나리오를 실행하는 클래스"""

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

    def _login(self, username: str = "standard_user", password: str = "secret_sauce") -> None:
        """로그인 수행 (장바구니 테스트를 위해서는 로그인 필요)"""
        self.page.locator('[data-test="username"]').fill(username)
        self.page.locator('[data-test="password"]').fill(password)
        self.page.locator('[data-test="login-button"]').click()
        time.sleep(0.5)

    def _add_to_cart(self, product_name: str) -> None:
        """상품을 장바구니에 추가"""
        try:
            # 상품명을 kebab-case로 변환 (예: "Sauce Labs Backpack" -> "sauce-labs-backpack")
            product_id = product_name.lower().replace(" ", "-")
            add_button = self.page.locator(f'[data-test="add-to-cart-{product_id}"]')

            # 버튼이 나타날 때까지 대기 후 클릭
            add_button.wait_for(state="visible", timeout=3000)
            add_button.click()
            time.sleep(0.3)
        except Exception as e:
            print(f"  [경고] 상품 '{product_name}' 추가 실패: {e}")

    def _remove_from_cart(self, product_name: str) -> None:
        """상품을 장바구니에서 제거"""
        product_id = product_name.lower().replace(" ", "-")
        remove_button = self.page.locator(f'[data-test="remove-{product_id}"]')
        if remove_button.is_visible():
            remove_button.click()
            time.sleep(0.3)

    def _go_to_cart(self) -> None:
        """장바구니 페이지로 이동"""
        self.page.locator('.shopping_cart_link').click()
        time.sleep(0.5)

    def _get_cart_badge_count(self) -> int:
        """장바구니 배지 카운트 가져오기"""
        try:
            badge = self.page.locator('.shopping_cart_badge')
            if badge.is_visible():
                return int(badge.text_content() or "0")
        except:
            pass
        return 0

    def _get_cart_items_count(self) -> int:
        """장바구니 페이지의 아이템 개수"""
        try:
            items = self.page.locator('.cart_item').all()
            return len(items)
        except:
            return 0

    def _is_on_cart_page(self) -> bool:
        """장바구니 페이지에 있는지 확인"""
        return "/cart.html" in self.page.url

    def _clear_cart(self) -> None:
        """장바구니의 모든 상품 제거 (테스트 격리를 위해)"""
        try:
            # 장바구니로 이동
            self._go_to_cart()
            time.sleep(0.3)

            # 모든 Remove 버튼 찾아서 클릭
            while True:
                remove_buttons = self.page.locator('button[class*="cart_button"]').all()
                if not remove_buttons:
                    break

                # 첫 번째 Remove 버튼 클릭
                remove_buttons[0].click()
                time.sleep(0.2)

            # 다시 상품 페이지로 이동
            self.page.goto(f"{self.base_url}/inventory.html")
            time.sleep(0.3)
        except Exception as e:
            # 장바구니 비우기 실패해도 계속 진행
            print(f"  [경고] 장바구니 초기화 실패: {e}")

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

            # 로그인 (장바구니 기능은 로그인 필요)
            self._navigate_to_login_page()

            # 장바구니 테스트는 기본 로그인 정보 사용
            # Username, Password 컬럼이 있으면 우선 사용 (없으면 기본값)
            username = test_data.get('Username', 'standard_user')
            password = test_data.get('Password', 'secret_sauce')

            self._login(username, password)

            # 로그인 후 inventory 페이지로 이동 대기
            self.page.wait_for_url("**/inventory.html", timeout=5000)

            # 테스트 격리: 장바구니 초기화 (이전 테스트의 상태 제거)
            self._clear_cart()

            # When
            print(f"  When: {when}")

            # 상품명 추출 (Given_value에서 파싱)
            product_name = "Sauce Labs Backpack"  # 기본값
            if 'Product' in test_data:
                product_name = test_data['Product']
            elif '추가대상상품' in given_value:
                # "추가대상상품 : Sauce Labs Backpack" 형식에서 상품명 추출
                parts = given_value.split('추가대상상품')
                if len(parts) > 1 and ':' in parts[1]:
                    product_name = parts[1].split(':', 1)[1].strip()
            elif '삭제대상상품' in given_value:
                # "삭제대상상품 : Sauce Labs Backpack" 형식에서 상품명 추출
                parts = given_value.split('삭제대상상품')
                if len(parts) > 1 and ':' in parts[1]:
                    product_name = parts[1].split(':', 1)[1].strip()

            # Then
            print(f"  Then: {then}")

            # 테스트 케이스별 검증 로직 (Google Sheets Feature 컬럼 기준)
            if "단일상품추가" in feature:
                # 단일 상품을 장바구니에 추가
                self._add_to_cart(product_name)
                badge_count = self._get_cart_badge_count()

                if badge_count == 1:
                    result = "PASS"
                else:
                    error_msg = f"단일 상품 추가 실패 (배지 카운트: {badge_count}, 기대값: 1)"

            elif "복수상품추가" in feature:
                # 복수 상품을 장바구니에 추가
                products = ["sauce-labs-backpack", "sauce-labs-bike-light"]
                for prod in products:
                    self._add_to_cart(prod)

                badge_count = self._get_cart_badge_count()
                if badge_count == len(products):
                    result = "PASS"
                else:
                    error_msg = f"복수 상품 추가 실패 (배지 카운트: {badge_count}, 기대값: {len(products)})"

            elif "상품삭제" in feature:
                # 상품 추가 후 제거
                self._add_to_cart(product_name)
                initial_count = self._get_cart_badge_count()
                self._remove_from_cart(product_name)
                final_count = self._get_cart_badge_count()

                if final_count == 0 and initial_count > 0:
                    result = "PASS"
                else:
                    error_msg = f"상품 삭제 실패 (초기: {initial_count}, 최종: {final_count})"

            elif "다른페이지이동" in feature:
                # 장바구니에 상품 추가 후 다른 페이지로 이동했다가 돌아와서 확인
                self._add_to_cart(product_name)
                initial_count = self._get_cart_badge_count()

                # 다른 페이지로 이동 (상품 페이지 재방문)
                self.page.goto(f"{self.base_url}/inventory.html")
                time.sleep(0.5)

                # 장바구니 카운트가 유지되는지 확인
                after_navigation_count = self._get_cart_badge_count()

                if after_navigation_count == initial_count and initial_count > 0:
                    result = "PASS"
                else:
                    error_msg = f"장바구니 상태 유지 실패 (초기: {initial_count}, 이동 후: {after_navigation_count})"

            elif "빈상태표시" in feature:
                # 장바구니가 비어있는지 확인
                self._go_to_cart()

                if self._is_on_cart_page() and self._get_cart_items_count() == 0:
                    result = "PASS"
                else:
                    error_msg = f"빈 장바구니 확인 실패 (아이템 수: {self._get_cart_items_count()})"

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

        scenario = CartScenario(page)

        # 테스트 데이터 예시
        test_data = {
            'TESTCASE_ID': 'CART_001',
            'FEATURE': '장바구니 추가',
            'Given': '로그인 후 상품 페이지',
            'When': '상품을 장바구니에 추가',
            'Then': '장바구니 배지에 카운트 표시',
            'Username': 'standard_user',
            'Password': 'secret_sauce',
            'Product': 'sauce-labs-backpack'
        }

        result = scenario.execute_test_case(test_data)
        print(f"결과: {result}")

        browser.close()
