"""
리포트 생성 모듈: HTML 및 JSON 리포트 생성
"""
import json
import base64
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class HTMLReportGenerator:
    """HTML 및 JSON 리포트 생성 클래스"""

    def __init__(self, report_dir: Path):
        """
        Args:
            report_dir: 리포트 저장 디렉토리
        """
        self.report_dir = report_dir
        self.report_dir.mkdir(exist_ok=True)

    def _encode_screenshot(self, screenshot_path: str) -> str:
        """스크린샷을 Base64로 인코딩"""
        try:
            if not screenshot_path or not Path(screenshot_path).exists():
                return ""

            with open(screenshot_path, 'rb') as f:
                image_data = f.read()
                encoded = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/png;base64,{encoded}"
        except Exception as e:
            print(f"[경고] 스크린샷 인코딩 실패: {e}")
            return ""

    def generate_html_report(self, results: List[Dict], config: Dict, timestamp: str) -> str:
        """HTML 리포트 생성"""
        total = len(results)
        passed = sum(1 for r in results if r['result'] == 'PASS')
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        # 결과 테이블 생성
        table_rows = ""
        for idx, result in enumerate(results, 1):
            status_class = "pass" if result['result'] == 'PASS' else "fail"
            status_symbol = "✓" if result['result'] == 'PASS' else "✗"

            # 상세 정보 (실패 시)
            details = ""
            if result['result'] == 'FAIL':
                details = f'<div class="details">'

                # 에러 로그
                if result.get('error_msg'):
                    details += f'''
                    <div class="error-log-section">
                        <strong>❌ 에러 로그:</strong>
                        <pre class="error-log">{result['error_msg']}</pre>
                    </div>
                    '''

                # 브라우저 콘솔 로그
                if result.get('console_logs'):
                    console_log_text = '\n'.join(result['console_logs'])
                    details += f'''
                    <div class="console-log-section">
                        <strong>🖥️ 브라우저 콘솔 로그:</strong>
                        <pre class="console-log">{console_log_text}</pre>
                    </div>
                    '''

                # 네트워크 로그
                if result.get('network_logs'):
                    # 네트워크 로그가 너무 길 수 있으므로 처음 50개만 표시
                    network_logs_limited = result['network_logs'][:50]
                    network_log_text = '\n'.join(network_logs_limited)
                    log_count = len(result['network_logs'])
                    limit_notice = f" (총 {log_count}개 중 50개 표시)" if log_count > 50 else ""
                    details += f'''
                    <div class="network-log-section">
                        <strong>🌐 네트워크 로그{limit_notice}:</strong>
                        <pre class="network-log">{network_log_text}</pre>
                    </div>
                    '''

                # 스크린샷
                if result.get('screenshot'):
                    encoded_img = self._encode_screenshot(result['screenshot'])
                    if encoded_img:
                        details += f'''
                        <div class="screenshot-section">
                            <strong>📸 스크린샷:</strong>
                            <img src="{encoded_img}" alt="Screenshot" class="screenshot">
                        </div>
                        '''

                details += '</div>'

            table_rows += f'''
            <tr class="{status_class}">
                <td>{idx}</td>
                <td>{result['test_id']}</td>
                <td>{result['feature']}</td>
                <td class="status">{status_symbol} {result['result']}</td>
                <td>{result['elapsed_time']:.2f}s</td>
                <td>{result['timestamp']}</td>
            </tr>
            '''

            if details:
                table_rows += f'''
                <tr class="details-row">
                    <td colspan="6">{details}</td>
                </tr>
                '''

        # HTML 생성
        html_content = f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>테스트 리포트 - {timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 3px solid #e9ecef;
        }}

        .summary-item {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }}

        .summary-item:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}

        .summary-item h3 {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .summary-item .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .summary-item.total .value {{
            color: #667eea;
        }}

        .summary-item.passed .value {{
            color: #28a745;
        }}

        .summary-item.failed .value {{
            color: #dc3545;
        }}

        .summary-item.rate .value {{
            color: #17a2b8;
        }}

        .config {{
            padding: 20px 30px;
            background: #fff;
            border-bottom: 2px solid #e9ecef;
        }}

        .config h3 {{
            margin-bottom: 15px;
            color: #667eea;
            font-size: 1.2em;
        }}

        .config p {{
            margin: 8px 0;
            color: #555;
            font-size: 0.95em;
        }}

        .config strong {{
            color: #333;
            min-width: 120px;
            display: inline-block;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0;
        }}

        thead {{
            background: #667eea;
            color: white;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        thead th {{
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}

        tbody tr {{
            border-bottom: 1px solid #e9ecef;
            transition: background-color 0.2s;
        }}

        tbody tr:hover {{
            background-color: #f8f9fa;
        }}

        tbody td {{
            padding: 15px;
            font-size: 0.95em;
        }}

        tr.pass {{
            background-color: #f0fff4;
        }}

        tr.fail {{
            background-color: #fff5f5;
        }}

        .status {{
            font-weight: bold;
            font-size: 1em;
        }}

        tr.pass .status {{
            color: #28a745;
        }}

        tr.fail .status {{
            color: #dc3545;
        }}

        .details {{
            padding: 25px;
            background: #fafafa;
            border-left: 4px solid #667eea;
            margin: 10px 0;
        }}

        .details-row {{
            background: #fafafa !important;
        }}

        .details-row td {{
            padding: 0 !important;
        }}

        .error-log-section {{
            margin-bottom: 20px;
        }}

        .error-log {{
            background: #fff5f5;
            border-left: 4px solid #f44336;
            padding: 15px;
            margin-top: 10px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 13px;
            color: #d32f2f;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .console-log-section {{
            margin-bottom: 20px;
        }}

        .console-log {{
            background: #f5f5ff;
            border-left: 4px solid #3f51b5;
            padding: 15px;
            margin-top: 10px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 13px;
            color: #1a237e;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 300px;
            overflow-y: auto;
        }}

        .network-log-section {{
            margin-bottom: 20px;
        }}

        .network-log {{
            background: #f1f8f4;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin-top: 10px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 12px;
            color: #1b5e20;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 400px;
            overflow-y: auto;
        }}

        .screenshot-section {{
            margin-top: 15px;
        }}

        .screenshot {{
            max-width: 100%;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            margin-top: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        footer {{
            text-align: center;
            padding: 25px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
            border-top: 2px solid #e9ecef;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}

            thead {{
                position: static;
            }}

            .screenshot {{
                max-width: 600px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧪 테스트 자동화 리포트</h1>
            <p>생성 시간: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")}</p>
        </header>

        <div class="summary">
            <div class="summary-item total">
                <h3>Total Tests</h3>
                <div class="value">{total}</div>
                <p>총 테스트</p>
            </div>
            <div class="summary-item passed">
                <h3>Passed</h3>
                <div class="value">{passed}</div>
                <p>성공</p>
            </div>
            <div class="summary-item failed">
                <h3>Failed</h3>
                <div class="value">{failed}</div>
                <p>실패</p>
            </div>
            <div class="summary-item rate">
                <h3>Pass Rate</h3>
                <div class="value">{pass_rate:.1f}%</div>
                <p>성공률</p>
            </div>
        </div>

        <div class="config">
            <h3>⚙️ 테스트 환경 설정</h3>
            <p><strong>브라우저:</strong> {config.get('browser', 'chromium')}</p>
            <p><strong>Headless:</strong> {config.get('headless', False)}</p>
            <p><strong>Base URL:</strong> {config.get('base_url', 'N/A')}</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>테스트 ID</th>
                    <th>기능</th>
                    <th>결과</th>
                    <th>실행시간</th>
                    <th>타임스탬프</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <footer>
            <p>🤖 테스트 자동화 프레임워크 v1.0 | Python + Playwright</p>
            <p>리포트 ID: {timestamp}</p>
        </footer>
    </div>
</body>
</html>
        '''

        # HTML 파일 저장
        html_file = self.report_dir / f"report_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"[리포트 레이어] HTML 리포트 저장: {html_file}")
        return str(html_file)

    def save_json_report(self, results: List[Dict], config: Dict, timestamp: str) -> str:
        """JSON 리포트 저장"""
        report_data = {
            'timestamp': timestamp,
            'config': config,
            'summary': {
                'total': len(results),
                'passed': sum(1 for r in results if r['result'] == 'PASS'),
                'failed': sum(1 for r in results if r['result'] == 'FAIL'),
                'pass_rate': (sum(1 for r in results if r['result'] == 'PASS') / len(results) * 100) if results else 0
            },
            'results': results
        }

        json_file = self.report_dir / f"report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"[리포트 레이어] JSON 리포트 저장: {json_file}")
        return str(json_file)


if __name__ == "__main__":
    # 테스트용 코드
    from pathlib import Path

    report_dir = Path("../reports")
    generator = HTMLReportGenerator(report_dir)

    # 샘플 데이터
    sample_results = [
        {
            'test_id': 'TEST_001',
            'feature': '로그인 테스트',
            'result': 'PASS',
            'elapsed_time': 1.23,
            'screenshot': '',
            'error_msg': '',
            'timestamp': '2024-01-01 12:00:00'
        },
        {
            'test_id': 'TEST_002',
            'feature': '장바구니 테스트',
            'result': 'FAIL',
            'elapsed_time': 2.34,
            'screenshot': '',
            'error_msg': '장바구니 추가 실패',
            'timestamp': '2024-01-01 12:00:01'
        }
    ]

    config = {
        'browser': 'chromium',
        'headless': False,
        'base_url': 'https://www.saucedemo.com'
    }

    html_file = generator.generate_html_report(sample_results, config, '20240101_120000')
    json_file = generator.save_json_report(sample_results, config, '20240101_120000')

    print(f"HTML: {html_file}")
    print(f"JSON: {json_file}")
