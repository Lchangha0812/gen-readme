import argparse

from .providers import get_available_providers

DEFAULT_TEMPLATE_FILE = "readme-template.md"  # 템플릿 파일 이름
DEFAULT_README_NAME = "README.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="콘텐츠(디렉터리 또는 텍스트)를 기반으로 README.md를 생성/수정하는 도구"
    )
    # package_path 또는 input_file 중 하나만 필수
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "package_path",
        nargs="?",  # 선택적 인자로 변경
        help="도메인/서비스 패키지 루트 디렉터리 경로 (예: src/main/java/com/example/order)",
    )
    group.add_argument(
        "-i",
        "--input-file",
        dest="input_file",
        help="분석할 텍스트 파일 경로. '-'를 사용하면 stdin에서 입력을 받습니다.",
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
        choices=get_available_providers(),
        help=f"사용할 LLM 제공자 (기본값: gemini)",
    )
    parser.add_argument(
        "--prompt-mode",
        default="structured",
        choices=["structured", "direct"],
        help="프롬프트 생성 방식을 선택합니다: 'structured' (기본값, 상세 구조) 또는 'direct' (직접 명령).",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="README.md 파일로 저장하지 않고 결과를 stdout으로만 출력",
    )
    return parser.parse_args()