from abc import ABC, abstractmethod
from typing import List


class ReadmeProvider(ABC):
    """
    모든 README 생성 제공자가 상속해야 하는 추상 기본 클래스.
    """



    @abstractmethod
    def build_prompt_new(
        self, file_paths: List[str], request: str | None
    ) -> str:
        """새로운 README.md 파일을 생성하기 위한 프롬프트를 구성한다."""
        pass

    @abstractmethod
    def build_prompt_update(
        self, file_paths: List[str], request: str | None
    ) -> str:
        """기존 README.md를 수정하기 위한 프롬프트를 구성한다."""
        pass

    @abstractmethod
    def call_llm(self, prompt: str) -> str:
        """LLM을 호출하여 결과를 반환한다."""
        pass
