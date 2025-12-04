import textwrap
from typing import List

from . import temp_utils


class GeminiPromptBuilder:
    """Gemini를 위한 프롬프트 생성 로직을 캡슐화한 클래스."""

    _ROLE = textwrap.dedent("""
        너는 복잡한 소프트웨어 시스템을 개발자들이 쉽게 이해하고 사용할 수 있도록 돕는 'Developer Advocate'다.
        너의 핵심 임무는 코드베이스를 분석하여 명확하고, 실용적이며, 가독성 높은 README 문서를 작성하는 것이다.
        중요: 너에게 제공되는 파일(@로 시작하는 경로)들은 이미 분석에 필요한 코드를 모두 정리해 둔 것이니, 다른 파일을 직접 읽으려고 시도하지 말고 제공된 파일들의 내용에만 집중해야 한다.
        """).strip()
    _OUTPUT_FORMAT = textwrap.dedent("""
        출력 형식: 다른 대화나 서두 없이, 오직 README.md 본문에 들어갈 마크다운 형식의 텍스트만 출력해라. 어떠한 추가 설명이나 대화 내용도 포함하지 마라. README의 내용은 한국어로 작성해야 한다.
        """).strip()

    def get_role_prompt(self) -> str:
        """대화형 API를 위한 역할 프롬프트를 반환합니다."""
        return self._ROLE

    def _build_base_prompt(
        self,
        request: str | None,
        situation: str,
        objective: str,
        file_path_str: str,
    ) -> str:
        """프롬프트의 각 부분을 한 줄로 합쳐 최종 프롬프트를 생성한다."""
    
        role_cleaned = ' '.join(self._ROLE.split())
        situation_cleaned = ' '.join(situation.split())
        objective_cleaned = ' '.join(objective.split())
        request_cleaned = ' '.join(request.split()) if request else "별도의 추가 요청 없음"
        output_format_cleaned = ' '.join(self._OUTPUT_FORMAT.split())

        parts = [
            f"역할: {role_cleaned}",
            f"현재 상황: {situation_cleaned}",
            f"목적: {objective_cleaned}",
            f"사용자 추가 요청(선택): {request_cleaned}",
            output_format_cleaned,
            f"분석 대상 코드 경로: {file_path_str}"
        ]
        
        # 모든 부분을 공백 한 칸으로 구분하여 최종 프롬프트를 만듭니다.
        return " ".join(parts)


    def build_prompt_new(
        self, file_paths: List[str], request: str | None
    ) -> str:
        """새로운 README.md 파일을 생성하기 위한 프롬프트를 구성합니다."""
        file_path_str = " , ".join([f"@{p}" for p in file_paths])
        
        situation = textwrap.dedent("""
            - 이 프로젝트에는 아직 README.md 파일이 존재하지 않는다.
            """).strip()
        objective = textwrap.dedent("""
            - 아래 제공된 "분석 대상 코드 경로"들을 참고하여, 가독성과 실용성을 고려한 최적의 구조로 README.md를 "새로 생성"하라.
            - 역할, 아키텍처, 도메인 규칙, 서비스 인터페이스, 사용법 등 개발자에게 유용한 정보를 포함해야 한다.
            """).strip()
        
        return self._build_base_prompt(
            request=request,
            situation=situation,
            objective=objective,
            file_path_str=file_path_str,
        )

    def build_prompt_update(
        self, file_paths: List[str], request: str | None
    ) -> str:
        """기존 README.md를 수정하기 위한 프롬프트를 구성합니다."""
        file_path_str = " , ".join([f"@{p}" for p in file_paths])

        situation = textwrap.dedent("""
            - 이 프로젝트에는 이미 README.md 파일이 존재하며, 아래 "분석 대상 코드 경로" 목록에는 기존 README 내용이 포함되어 있다.
            """).strip()
        objective = textwrap.dedent("""
            - 아래 제공된 "분석 대상 코드 경로"들을 참고하고, 기존 README 내용을 종합적으로 분석하여, README.md를 최신 상태로 "재구성 및 개선"하라.
            - 불필요하거나 오래된 정보는 삭제하고, 누락된 중요 정보를 코드에서 찾아 보충하라.
            """).strip()
        
        return self._build_base_prompt(
            request=request,
            situation=situation,
            objective=objective,
            file_path_str=file_path_str,
        )