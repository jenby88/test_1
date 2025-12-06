# 프로젝트 규칙 및 가이드라인

## 프로젝트 개요
- **프로젝트명**: TEST
- **기술 스택**: Python, Playwright, pytest
- **목적**: 웹 자동화 테스트

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
- 새로운 기능은 반드시 테스트 작성
- 테스트 파일: `tests/test_*.py` 형식
- pytest 사용
- 커버리지 최소 80% 목표

## Git 워크플로우
- 커밋 메시지: 명령형으로 시작 ("Add", "Fix", "Update", "Refactor")
- 브랜치 네이밍:
  - `feature/기능명` - 새로운 기능
  - `bugfix/버그명` - 버그 수정
  - `hotfix/수정명` - 긴급 수정
- 커밋 전 테스트 실행 필수

## 자주 사용하는 명령어
```bash
# 테스트 실행
/Users/bongyeoljeon/Library/Python/3.9/bin/pytest tests/

# HTML 리포트 생성
/Users/bongyeoljeon/Library/Python/3.9/bin/pytest tests/ --html=report.html --self-contained-html

# 특정 브라우저로 테스트
/Users/bongyeoljeon/Library/Python/3.9/bin/pytest tests/ --browser chromium

# 의존성 설치
pip3 install -r requirements.txt

# Playwright 브라우저 설치
/Users/bongyeoljeon/Library/Python/3.9/bin/playwright install chromium
```

## 금지 사항
- ❌ .env 파일 커밋
- ❌ API 키, 시크릿 하드코딩
- ❌ print() 디버깅 (로깅 사용)
- ❌ 테스트 없는 기능 추가
- ❌ 커밋 메시지 없이 커밋

## 권장 사항
- ✅ 의미 있는 변수명 사용
- ✅ 함수는 한 가지 일만 수행
- ✅ 복잡한 로직은 주석 추가
- ✅ 타입 힌트 사용 (Python 3.5+)
- ✅ docstring 작성
