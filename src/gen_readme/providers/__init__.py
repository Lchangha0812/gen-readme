from .base import ReadmeProvider
from .gemini.gemini import GeminiReadmeProvider

# 사용 가능한 제공자들을 매핑합니다.
# 새로운 제공자를 추가하려면 여기에 추가하세요.
# 키는 CLI에서 사용할 이름 (소문자), 값은 제공자 클래스입니다.
PROVIDERS = {
    "gemini": GeminiReadmeProvider,
    # 예: "openai": OpenaiReadmeProvider,
}


def get_provider(name: str) -> ReadmeProvider:
    """
    지정된 이름의 README 제공자 인스턴스를 반환합니다.
    """
    provider_class = PROVIDERS.get(name.lower())
    if not provider_class:
        raise ValueError(f"알 수 없는 제공자입니다: {name}")
    return provider_class()

