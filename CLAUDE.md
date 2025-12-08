# 프로젝트 규칙 및 가이드라인

## 프로젝트 개요
- **프로젝트명**: TEST
- **기술 스택**: Python, Playwright
- **목적**: 웹 자동화 테스트 프레임워크
- **테스트 대상**: https://www.saucedemo.com
- **아키텍처**: 3-Layer (Data, Scenario, Execution/Report)

## 프레임워크 구조

### 3-Layer 아키텍처
```
┌─────────────────────────────────────────────────────────────┐
│  실행/리포트 레이어 (runner.py)                                │
│  - 브라우저 실행                                               │
│  - 테스트 오케스트레이션                                        │
│  - HTML/JSON 리포트 생성                                      │
│  - 브라우저 콘솔/네트워크 로그 수집                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  시나리오 레이어 (scenarios/)                                  │
│  - LoginScenario: 로그인 관련 테스트                           │
│  - CartScenario: 장바구니 관련 테스트                          │
│  - 각 시나리오는 PASS/FAIL 결과 반환                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  데이터 레이어 (data/data_loader.py)                           │
│  - Google Sheets에서 테스트 데이터 로드                        │
│  - CSV 형식으로 변환 및 파싱                                   │
│  - 라벨 기반 시나리오 매핑                                     │
│  - 로컬 캐싱 시스템 (선택적 새로고침 지원)                       │
└─────────────────────────────────────────────────────────────┘
```

### 디렉토리 구조
```
TEST/
├── runner.py                 # 메인 실행 파일
├── config.py                 # 프레임워크 설정
├── url                       # Google Sheets URL 목록
├── data/
│   ├── data_loader.py       # 데이터 로드 클래스
│   └── cache/               # 테스트 데이터 캐시 (자동 생성)
│       ├── 로그인.json
│       └── 장바구니.json
├── scenarios/
│   ├── login_scenario.py    # 로그인 시나리오
│   └── cart_scenario.py     # 장바구니 시나리오
├── reports/
│   └── report_generator.py  # HTML/JSON 리포트 생성
└── reports/                 # 리포트 출력 디렉토리
    ├── report_*.html
    ├── report_*.json
    └── screenshot_*.png
```

## 테스트 실행 방법

### 기본 실행
```bash
python3 runner.py
```

### 브라우저 표시/비표시 설정
`config.py` 파일에서 주석 전환:
```python
# HEADLESS = True   # 브라우저 숨김 (빠른 실행, CI/CD용)
HEADLESS = False  # 브라우저 보임 (디버깅용)
```

### 테스트 데이터 관리
1. Google Sheets에 테스트 케이스 작성
2. `url` 파일에 라벨과 URL 추가:
   ```
   로그인 : https://docs.google.com/spreadsheets/d/.../edit
   장바구니 : https://docs.google.com/spreadsheets/d/.../edit
   ```

### 데이터 캐싱 시스템
프레임워크는 Google Sheets 데이터를 로컬에 캐싱하여 테스트 실행 속도를 향상시킵니다.

**작동 방식**:
- 첫 실행 시: Google Sheets에서 다운로드 후 `data/cache/` 디렉토리에 JSON 형식으로 저장
- 이후 실행: 캐시에서 로드 (⚡ 표시) → 훨씬 빠른 실행
- 캐시 파일: `data/cache/로그인.json`, `data/cache/장바구니.json` 등

**선택적 새로고침** (`config.py`에서 설정):
```python
# 예시 1: 모든 시나리오 캐시 사용 (가장 빠름)
SCENARIOS_TO_REFRESH = []

# 예시 2: 로그인 시나리오만 새로 다운로드
SCENARIOS_TO_REFRESH = ['로그인']

# 예시 3: 여러 시나리오 새로 다운로드
SCENARIOS_TO_REFRESH = ['로그인', '장바구니']
```

**사용 시나리오**:
- 일반 테스트 실행: `SCENARIOS_TO_REFRESH = []` (캐시 사용)
- Google Sheets 데이터 업데이트 후: 해당 시나리오 라벨을 리스트에 추가
- 모든 데이터 강제 새로고침: 모든 라벨 추가

### 새 시나리오 추가 방법
1. `scenarios/` 폴더에 새 시나리오 파일 생성
   ```python
   # scenarios/product_scenario.py
   class ProductScenario:
       def execute_test_case(self, test_data):
           # 테스트 로직 구현
           return test_id, feature, result, error_msg
   ```

2. `runner.py`에 import 추가
   ```python
   from scenarios.product_scenario import ProductScenario
   ```

3. `SCENARIO_MAP`에 키워드 추가
   ```python
   SCENARIO_MAP = {
       '로그인': LoginScenario,
       '장바구니': CartScenario,
       '상품': ProductScenario,  # 추가
   }
   ```

## 리포트
- **HTML 리포트**: 시각적 테스트 결과, 스크린샷, 로그 포함
- **JSON 리포트**: 프로그래밍 방식 분석용 데이터
- **콘솔 출력**: 실시간 테스트 진행 상황 및 결과

### 리포트 내용
- 테스트 실행 결과 요약 (성공/실패/성공률)
- 각 테스트 케이스 상세 정보
- 실패 시: 에러 로그, 스크린샷, 브라우저 콘솔 로그, 네트워크 로그
- 실행 시간 및 타임스탬프

## 테스트 케이스 규칙
- **모든 테스트는 독립적으로 실행**: 각 테스트 시작 시 상태 초기화
- **GWT 구조 사용**: Given-When-Then 패턴
- **결과는 콘솔과 리포트에 모두 표시**
- **실패 시 자동 스크린샷 캡처**

## 코딩 규칙

### 1. 컴포넌트 작성
- 모든 컴포넌트는 함수형으로 작성

### 2. 에러 처리
- API 에러는 모두 try-catch 처리

### 3. 보안
- .env 파일은 git에 절대 커밋 금지

## Python 코드 스타일
- 들여쓰기: 4칸 (스페이스)
- 변수명: snake_case
- 클래스명: PascalCase
- 상수: UPPER_SNAKE_CASE
- 최대 줄 길이: 100자

## 테스트
- 새로운 기능은 반드시 테스트 시나리오 작성
- 시나리오 파일: `scenarios/*_scenario.py` 형식
- 각 시나리오는 `execute_test_case()` 메서드 구현 필수
- 반환값: (test_id, feature, result, error_msg)
- 모든 테스트는 독립적으로 실행되어야 함

## Git 워크플로우
- 커밋 메시지: 명령형으로 시작 ("Add", "Fix", "Update", "Refactor")
- 브랜치 네이밍:
  - `feature/기능명` - 새로운 기능
  - `bugfix/버그명` - 버그 수정
  - `hotfix/수정명` - 긴급 수정
- 커밋 전 테스트 실행 필수

## 자주 사용하는 명령어
```bash
# 테스트 실행 (브라우저 표시)
python3 runner.py

# 의존성 설치
pip3 install -r requirements.txt

# Playwright 브라우저 설치
/Users/bongyeoljeon/Library/Python/3.9/bin/playwright install chromium

# 설정 확인
python3 config.py

# 데이터 로더 테스트
python3 data/data_loader.py
```

## 금지 사항
- ❌ .env 파일 커밋
- ❌ API 키, 시크릿 하드코딩
- ❌ 테스트 없는 기능 추가
- ❌ 커밋 메시지 없이 커밋
- ❌ 테스트 간 상태 공유 (각 테스트는 독립적으로)

## 권장 사항
- ✅ 의미 있는 변수명 사용
- ✅ 함수는 한 가지 일만 수행
- ✅ 복잡한 로직은 주석 추가
- ✅ 타입 힌트 사용 (Python 3.5+)
- ✅ docstring 작성
- ✅ 테스트 결과는 콘솔과 리포트에 모두 표시
- ✅ Given-When-Then 패턴 준수
- ✅ 시나리오별 독립적인 헬퍼 메서드 구현
