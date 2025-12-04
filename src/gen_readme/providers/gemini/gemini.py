import shutil

from ..base import ReadmeProvider
from ...prompting import GeminiPromptBuilder
from . import gemini_orchestrator # new import


class GeminiReadmeProvider(ReadmeProvider):
    """
    Gemini CLI와의 상호작용을 담당하는 제공자.

    - 프롬프트 생성은 GeminiPromptBuilder에 위임합니다.
    - CLI 실행 및 파싱은 gemini_orchestrator에 위임합니다.
    """

    def __init__(self):
        self.prompt_builder = GeminiPromptBuilder()
        self.gemini_path = shutil.which("gemini")
        if not self.gemini_path:
            raise RuntimeError("gemini CLI를 찾을 수 없습니다. PATH에 gemini 명령이 있어야 합니다.")

    # --- Structured Prompt Methods ---
    def build_prompt_new(self, package_path, template_text, extra_request):
        return self.prompt_builder.build_prompt_new(package_path, template_text, extra_request)

    def build_prompt_update_with_diff(self, package_path, template_text, diff_text, extra_request):
        return self.prompt_builder.build_prompt_update_with_diff(package_path, template_text, diff_text, extra_request)

    def build_prompt_update_full_scan(self, package_path, template_text, extra_request):
        return self.prompt_builder.build_prompt_update_full_scan(package_path, template_text, extra_request)

    # --- Direct Prompt Methods ---
    def build_direct_prompt_new(self, package_path, extra_request):
        return self.prompt_builder.build_direct_prompt_new(package_path, extra_request)

    def build_direct_prompt_update_with_diff(self, package_path, diff_text, extra_request):
        return self.prompt_builder.build_direct_prompt_update_with_diff(package_path, diff_text, extra_request)

    def build_direct_prompt_update_full_scan(self, package_path, extra_request):
        return self.prompt_builder.build_direct_prompt_update_full_scan(package_path, extra_request)

    # --- LLM Call Method ---
    def call_llm(self, prompt: str, prompt_mode: str = "structured") -> str:
        """
        선택된 프롬프트 모드에 따라 gemini CLI를 호출하고 최종 텍스트를 반환합니다.
        """
        try:
            if prompt_mode == "direct":
                response = gemini_orchestrator.run_one_shot(self.gemini_path, prompt)
                if response: # direct 모드가 성공하면 바로 반환
                    return response
            
            # 'direct' 모드가 실패하거나, 처음부터 'structured' 모드인 경우
            return gemini_orchestrator.run_conversation(
                self.gemini_path,
                self.prompt_builder._ROLE, # role_prompt는 prompt_builder에서 가져옴
                prompt
            )

        except RuntimeError as e: # gemini CLI 관련 오류는 여기서 처리
            raise RuntimeError(f"gemini CLI 호출 중 오류 발생: {e}")
        except Exception as e:
            raise RuntimeError(f"gemini 실행 중 예기치 않은 오류 발생: {e}")