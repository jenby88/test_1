"""
데이터 레이어: Google Sheets에서 테스트 데이터를 로드
"""
import csv
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import urllib.request


class DataLoader:
    """Google Sheets 데이터를 CSV로 로드하는 클래스"""

    def __init__(self, url_file_path: str, cache_dir: str = "data/cache", scenarios_to_refresh: Optional[List[str]] = None):
        """
        Args:
            url_file_path: Google Sheets URL이 저장된 파일 경로
            cache_dir: 캐시 파일 저장 디렉토리
            scenarios_to_refresh: Google Sheets에서 새로 다운로드할 시나리오 라벨 리스트
        """
        self.url_file_path = Path(url_file_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.scenarios_to_refresh = scenarios_to_refresh or []
        self.test_data: List[Dict[str, str]] = []

    def load_google_sheets_urls(self) -> List[Tuple[str, str]]:
        """URL 파일에서 모든 Google Sheets 주소와 라벨 읽기 (여러 URL 지원)

        Returns:
            List[Tuple[라벨, CSV_URL]]
        """
        try:
            with open(self.url_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            url_data = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                label = ""
                url = line

                # URL 추출 (라벨이 있는 경우 처리)
                if ':' in line and 'http' in line:
                    # "로그인 : https://..." 형식
                    parts = line.split(':', 1)
                    label = parts[0].strip()
                    url = parts[1].strip()

                # Google Sheets URL을 CSV export 형식으로 변환
                if '/edit' in url:
                    csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
                    csv_url = csv_url.replace('/edit?usp=sharing', '/export?format=csv')
                else:
                    csv_url = url

                url_data.append((label, csv_url))

            print(f"[데이터 레이어] Google Sheets URL {len(url_data)}개 로드 완료")
            return url_data

        except Exception as e:
            raise Exception(f"URL 파일 읽기 실패: {e}")

    def _get_cache_file(self, label: str) -> Path:
        """라벨에 대한 캐시 파일 경로 반환"""
        # 라벨을 파일명으로 사용 (공백을 언더스코어로 변환)
        safe_label = label.replace(" ", "_").replace("/", "_")
        return self.cache_dir / f"{safe_label}.json"

    def _save_to_cache(self, label: str, data: List[Dict[str, str]]) -> None:
        """데이터를 캐시 파일에 저장"""
        cache_file = self._get_cache_file(label)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[데이터 레이어] 캐시 저장: {cache_file}")
        except Exception as e:
            print(f"[경고] 캐시 저장 실패: {e}")

    def _load_from_cache(self, label: str) -> Optional[List[Dict[str, str]]]:
        """캐시 파일에서 데이터 로드"""
        cache_file = self._get_cache_file(label)
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"[데이터 레이어] 캐시 로드: {cache_file}")
            return data
        except Exception as e:
            print(f"[경고] 캐시 로드 실패: {e}")
            return None

    def fetch_csv_data(self) -> List[Dict[str, str]]:
        """모든 Google Sheets에서 CSV 데이터를 가져와서 딕셔너리 리스트로 반환 (캐시 지원)"""
        try:
            url_data_list = self.load_google_sheets_urls()
            all_test_data = []

            for idx, (label, csv_url) in enumerate(url_data_list, 1):
                label_display = f"'{label}'" if label else "라벨 없음"

                # 시나리오가 새로고침 목록에 있는지 확인
                should_refresh = label in self.scenarios_to_refresh if label else False

                data = None

                if should_refresh:
                    # Google Sheets에서 다운로드 (강제 새로고침)
                    print(f"[데이터 레이어] {idx}/{len(url_data_list)} Google Sheets에서 다운로드 중... ({label_display}) 🔄")
                    data = self._download_from_sheets(csv_url, label)
                    if data:
                        self._save_to_cache(label, data)
                else:
                    # 캐시에서 로드 시도
                    data = self._load_from_cache(label)

                    if data is None:
                        # 캐시가 없으면 Google Sheets에서 다운로드
                        print(f"[데이터 레이어] {idx}/{len(url_data_list)} 캐시 없음. Google Sheets에서 다운로드 중... ({label_display})")
                        data = self._download_from_sheets(csv_url, label)
                        if data:
                            self._save_to_cache(label, data)
                    else:
                        print(f"[데이터 레이어] {idx}/{len(url_data_list)} 캐시 사용 ({label_display}) ⚡")

                if data:
                    print(f"[데이터 레이어] {len(data)}건 로드 완료")
                    all_test_data.extend(data)

            self.test_data = all_test_data
            print(f"[데이터 레이어] 총 테스트 데이터 {len(self.test_data)}건 로드 완료")
            return self.test_data

        except Exception as e:
            raise Exception(f"CSV 데이터 로드 실패: {e}")

    def _download_from_sheets(self, csv_url: str, label: str) -> Optional[List[Dict[str, str]]]:
        """Google Sheets에서 CSV 데이터 다운로드"""
        try:
            # CSV 데이터 다운로드
            with urllib.request.urlopen(csv_url) as response:
                csv_content = response.read().decode('utf-8')

            # CSV 파싱 (빈 줄 및 쉼표로만 이루어진 줄 제거)
            lines = [line for line in csv_content.splitlines()
                    if line.strip() and line.strip().replace(',', '')]
            csv_reader = csv.DictReader(lines)
            data = list(csv_reader)

            # 각 데이터에 출처 라벨 추가
            for row in data:
                row['_source_label'] = label

            return data
        except Exception as e:
            print(f"[경고] Google Sheets 다운로드 실패: {e}")
            return None

    def get_test_data(self) -> List[Dict[str, str]]:
        """테스트 데이터 반환 (캐싱)"""
        if not self.test_data:
            self.fetch_csv_data()
        return self.test_data

    def get_test_case_by_id(self, test_id: str) -> Dict[str, str]:
        """특정 테스트 케이스 ID로 데이터 조회"""
        for data in self.get_test_data():
            if data.get('TESTCASE_ID') == test_id:
                return data
        raise ValueError(f"테스트 케이스 ID '{test_id}'를 찾을 수 없습니다")


if __name__ == "__main__":
    # 테스트용 코드
    loader = DataLoader("../url")
    data = loader.fetch_csv_data()
    print(f"\n총 {len(data)}개의 테스트 케이스:")
    for item in data:
        print(f"  - {item.get('TESTCASE_ID')}: {item.get('FEATURE')}")
