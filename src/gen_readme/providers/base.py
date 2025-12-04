from abc import ABC, abstractmethod
import pathlib


class ReadmeProvider(ABC):
    """
    모든 README 생성 제공자가 상속해야 하는 추상 기본 클래스.
    """

    @abstractmethod
    def build_prompt_new(
        self,
        package_path: pathlib.Path,
        template_text: str | None,
        extra_request: str,
    ) -> str:
        """(구조화된) 새로운 README.md 파일을 생성하기 위한 프롬프트를 구성한다."""
        pass

    @abstractmethod
    def build_prompt_update_with_diff(
        self,
        package_path: pathlib.Path,
        template_text: str | None,
        diff_text: str,
        extra_request: str,
    ) -> str:
        """(구조화된) git diff를 기반으로 기존 README.md를 수정하기 위한 프롬프트를 구성한다."""
        pass

    @abstractmethod
    def build_prompt_update_full_scan(
        self,
        package_path: pathlib.Path,
        template_text: str | None,
        extra_request: str,
    ) -> str:
        """(구조화된) 전체 코드 스캔을 기반으로 기존 README.md를 수정하기 위한 프롬프트를 구성한다."""
        pass
    
    @abstractmethod
    def build_direct_prompt_new(self, package_path: pathlib.Path, extra_request: str) -> str:
        """(직접적인) 새로운 README.md 파일을 생성하기 위한 프롬프트를 구성한다."""
        pass

    @abstractmethod
    def build_direct_prompt_update_with_diff(self, package_path: pathlib.Path, diff_text: str, extra_request: str) -> str:
        """(직접적인) git diff를 기반으로 기존 README.md를 수정하기 위한 프롬프트를 구성한다."""
        pass

    @abstractmethod
    def build_direct_prompt_update_full_scan(self, package_path: pathlib.Path, extra_request: str) -> str:
        """(직접적인) 전체 코드 스캔을 기반으로 기존 README.md를 수정하기 위한 프롬프트를 구성한다."""
        pass

    @abstractmethod
    def call_llm(self, prompt: str) -> str:
        """LLM을 호출하여 결과를 반환한다."""
        pass