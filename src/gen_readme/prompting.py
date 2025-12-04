import pathlib
import textwrap


class GeminiPromptBuilder:
    """Gemini를 위한 프롬프트 생성 로직을 캡슐화한 클래스."""

    _ROLE = "너는 복잡한 소프트웨어 시스템을 개발자들이 쉽게 이해하고 사용할 수 있도록 돕는 'Developer Advocate'다. 너의 핵심 임무는 코드베이스를 분석하여 명확하고, 실용적이며, 가독성 높은 README 문서를 작성하는 것이다."
    _USAGE_COMMON = textwrap.dedent("""
        사용 방법(중요):
        - 너는 이 저장소의 코드를 직접 읽을 수 있다고 가정한다.""" ).strip()
    _USAGE_READ_FILES = "- 특히, 위 디렉토리 경로 아래의 파일들을 직접 열어 구조와 책임을 파악하라."
    _USAGE_READ_FILES_AND_README = "- 특히, 위 디렉토리 경로 아래의 파일들과 README.md를 직접 열어 구조와 책임을 파악하라."
    _USAGE_HINT_DIFF = "- 아래 git diff는 \"무엇이 바뀌었는지\"를 빠르게 이해하기 위한 힌트로만 사용하라."
    _OUTPUT_FORMAT = textwrap.dedent("""
        출력 형식:
        - 최종 결과는 오직 하나의 마크다운 문서(수정된 README.md 전체)만 출력한다.
        - 설명, 가이드, 요약 같은 메타 텍스트는 출력하지 말 것.
        - README의 내용은 한국어로 작성해야 한다.""" ).strip()

    # --- Structured Prompt Methods ---

    def _build_base_prompt(
        self,
        package_path: pathlib.Path,
        extra_request: str,
        situation: str,
        objective: str,
        usage: str,
        template_text: str | None = None,
        diff_text: str | None = None,
    ) -> str:
        """프롬프트의 공통 구조를 만들고, 가변적인 부분을 조합하여 최종 프롬프트를 생성한다."""
        prompt = textwrap.dedent(
            f"""
            역할:
            - {self._ROLE}

            대상 디렉토리:
            - 디렉토리 루트 경로: {package_path}

            현재 상황:
            {situation}

            목적:
            {objective}

            {usage}

            사용자 추가 요청(선택):
            {extra_request or "별도의 추가 요청 없음"}

            {self._OUTPUT_FORMAT}
            """
        ).strip()

        if template_text:
            prompt += "\n\n" + textwrap.dedent(f"""
[README_TEMPLATE_START]
{template_text}
[README_TEMPLATE_END]""" ).strip()

        if diff_text:
            prompt += "\n\n" + textwrap.dedent(f"""
[GIT_DIFF_START]
{diff_text}
[GIT_DIFF_END]""" ).strip()

        return prompt

    def build_prompt_new(
        self,
        package_path: pathlib.Path,
        template_text: str | None,
        extra_request: str,
    ) -> str:
        situation = textwrap.dedent("""
            - 이 디렉토리에는 아직 README.md 파일이 존재하지 않는다.
            - 이 디렉토리의 코드/설정/모델을 기반으로, 요약 README를 새로 만들어야 한다.
        """ ).strip()

        if template_text:
            objective = textwrap.dedent("""
                - 다음 'README 템플릿'을 참고해서, 이 디렉토리에 대한 README.md를 "새로 생성"하라.
                - 역할, 아키텍처, 도메인 규칙, 서비스 인터페이스 등을 템플릿 구조에 맞게 정리하라.
            """ ).strip()
        else:
            objective = textwrap.dedent("""
                - 가독성과 실용성을 고려하여 최적의 구조를 직접 구상하고, 그에 맞춰 README.md를 "새로 생성"하라.
                - 역할, 아키텍처, 도메인 규칙, 서비스 인터페이스, 사용법 등 개발자에게 유용한 정보를 포함해야 한다.
            """ ).strip()
        
        objective += "\n- 실제 코드 구조(디렉토리 구조, 클래스 명, 함수, 설정 등)를 최대한 반영하라."
        usage = f"{self._USAGE_COMMON}\n{self._USAGE_READ_FILES}"
        
        return self._build_base_prompt(
            package_path=package_path,
            extra_request=extra_request,
            situation=situation,
            objective=objective,
            usage=usage,
            template_text=template_text,
        )

    def build_prompt_update_with_diff(
        self,
        package_path: pathlib.Path,
        template_text: str | None,
        diff_text: str,
        extra_request: str,
    ) -> str:
        situation = textwrap.dedent("""
            - 이 디렉토리에는 이미 README.md 파일이 존재한다.
            - 아래 git diff는 이 디렉토리 내에서 최근 변경된 코드/설정/파일을 보여준다.
            - 너는 이 diff와 실제 파일 내용을 참고해서 README를 최신 상태로 반영해야 한다.
        """ ).strip()
        
        if template_text:
            objective = textwrap.dedent("""
                - 다음 'README 템플릿'을 참고해서, 이 디렉토리의 README.md를 최신 상태로 "수정"하라.
                - README 구조는 템플릿의 섹션을 최대한 따르되, 필요에 따라 일부 섹션은 생략하거나 합쳐도 된다.
            """ ).strip()
        else:
            objective = textwrap.dedent("""
                - 기존 README의 구조와 내용을 분석하고, 가독성과 명확성을 높이는 방향으로 "수정"하라.
                - 필요하다면 새로운 섹션을 추가하거나 기존 섹션을 통합하여 구조를 개선할 수 있다.
            """ ).strip()
            
        objective += "\n- git diff에 나타난 변경 사항(새로 추가된 기능/필드/규칙 등)이 README에도 반영되도록 하라."
        usage = f"{self._USAGE_COMMON}\n{self._USAGE_READ_FILES_AND_README}\n{self._USAGE_HINT_DIFF}"
        
        return self._build_base_prompt(
            package_path=package_path,
            extra_request=extra_request,
            situation=situation,
            objective=objective,
            usage=usage,
            template_text=template_text,
            diff_text=diff_text,
        )

    def build_prompt_update_full_scan(
        self,
        package_path: pathlib.Path,
        template_text: str | None,
        extra_request: str,
    ) -> str:
        situation = textwrap.dedent("""
            - 이 디렉토리에는 이미 README.md 파일이 존재한다.
            - git diff 기준으로는 이 디렉토리에 대한 변경사항이 특별히 감지되지 않았다
              (또는 git 정보를 사용할 수 없다).
        """ ).strip()

        if template_text:
            objective = textwrap.dedent("""
                - 다음 'README 템플릿'을 참고해서, 이 디렉토리의 README.md를 정리/개선하라.
                - 기존 README에 유용한 정보가 있다면 그대로 반영하되, 템플릿 구조에 맞게 재구성한다.
            """ ).strip()
        else:
            objective = textwrap.dedent("""
                - 기존 README의 구조와 내용을 분석하고, 가독성과 명확성을 높이는 방향으로 "재구성 및 개선"하라.
                - 불필요하거나 오래된 정보는 삭제하고, 누락된 중요 정보를 코드에서 찾아 보충하라.
            """ ).strip()
            
        objective += "\n- 디렉토리 내의 코드/설정/모델을 직접 읽고, 도메인 개요, 아키텍처, 규칙, 서비스 계약 등을 문서화하라."
        usage = f"{self._USAGE_COMMON}\n{self._USAGE_READ_FILES_AND_README}"

        return self._build_base_prompt(
            package_path=package_path,
            extra_request=extra_request,
            situation=situation,
            objective=objective,
            usage=usage,
            template_text=template_text,
        )

    # --- Direct Prompt Methods ---

    def _generate_direct_prompt(self, task_description: str, package_path: pathlib.Path, extra_request: str) -> str:
        """모든 정보를 종합하여 직접적인 단일 프롬프트를 생성합니다."""
        request_clause = f"추가적으로 다음 요청을 반영해줘: {extra_request}" if extra_request else ""
        prompt = f"""당신은 Developer Advocate입니다. 지금부터 다음 디렉토리의 코드를 분석하여, 프로젝트의 목적, 아키텍처, 사용법, 도메인 규칙 등을 설명하는 README.md 파일을 한국어로 작성해 주세요. 대화나 다른 설명 없이, 완성된 README.md 파일의 내용만 생성해야 합니다. {request_clause} 분석할 디렉토리: {package_path}"""
        return textwrap.dedent(prompt).strip()

    def build_direct_prompt_new(self, package_path: pathlib.Path, extra_request: str) -> str:
        task = f"'{package_path}' 디렉토리의 코드를 분석하여 새로운 README.md 파일을 생성해줘."
        return self._generate_direct_prompt(task, package_path, extra_request)

    def build_direct_prompt_update_with_diff(self, package_path: pathlib.Path, diff_text: str, extra_request: str) -> str:
        task = f"'{package_path}' 디렉토리의 기존 README.md 파일을 코드 변경사항(diff 참조)을 반영하여 업데이트해줘. 다음은 코드 변경사항에 대한 git diff야:\n{diff_text}"
        return self._generate_direct_prompt(task, package_path, extra_request)

    def build_direct_prompt_update_full_scan(self, package_path: pathlib.Path, extra_request: str) -> str:
        task = f"'{package_path}' 디렉토리의 전체 코드를 다시 분석하여 기존 README.md 파일을 개선하고 업데이트해줘."
        return self._generate_direct_prompt(task, package_path, extra_request)