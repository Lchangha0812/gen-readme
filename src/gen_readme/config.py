import argparse

from .providers import get_available_providers

DEFAULT_README_NAME = "README.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="패키지 경로를 기반으로 README.md를 생성/수정하는 도구"
    )
    parser.add_argument(
        "package_path",
        nargs="?", 
        default=".",
        help="분석할 도메인/서비스 패키지 루트 디렉터리 경로 (기본값: 현재 디렉터리 './')",
    )
    
    parser.add_argument(
        "-t",
        "--template",
        default=None,
        help="참고할 README 템플릿 마크다운 파일 경로. 지정하지 않으면 LLM이 구조를 직접 생성합니다.",
    )
    parser.add_argument(
        "-r",
        "--request",
        default="",
        help="LLM에게 전달할 추가 요청/설명 (예: '주문 생성부터 결제/배송까지 담당하는 도메인이다')",
    )
    parser.add_argument(
        "-p",
        "--provider",
        default="gemini",
        help=f"사용할 LLM 제공자 (기본값: gemini)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="README.md 파일로 저장하지 않고 결과를 stdout으로만 출력",
    )
    return parser.parse_args()