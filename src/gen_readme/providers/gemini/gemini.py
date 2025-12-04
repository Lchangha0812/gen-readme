import shutil
from typing import List

from ..base import ReadmeProvider
from ...prompting import GeminiPromptBuilder
from . import gemini_orchestrator


class GeminiReadmeProvider(ReadmeProvider):
    """
    Gemini CLI와의 상호작용을 담당하는 제공자.
    """

    def __init__(self):
        self.prompt_builder = GeminiPromptBuilder()
        self.gemini_path = shutil.which("gemini")
        if not self.gemini_path:
            raise RuntimeError("gemini CLI를 찾을 수 없습니다. PATH에 gemini 명령이 있어야 합니다.")

    def build_prompt_new(self, file_paths: List[str], request: str | None) -> str:
        return self.prompt_builder.build_prompt_new(file_paths, request)

    def build_prompt_update(self, file_paths: List[str], request: str | None) -> str:
        return self.prompt_builder.build_prompt_update(file_paths, request)

    def call_llm(self, prompt: str) -> str:
        """
        gemini CLI를 호출하고 최종 텍스트를 반환합니다.
        """
        try:
            return gemini_orchestrator.run_conversation(
                self.gemini_path,
                prompt
            )
        except RuntimeError as e:
            raise RuntimeError(f"gemini CLI 호출 중 오류 발생: {e}")
        except Exception as e:
            raise RuntimeError(f"gemini 실행 중 예기치 않은 오류 발생: {e}")
