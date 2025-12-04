import pathlib
import sys
from typing import Iterator

from . import dir_text_collector, temp_utils
from .providers import get_provider
from .config import parse_args, DEFAULT_README_NAME


def load_template(template_path: pathlib.Path) -> str:
    """템플릿 파일을 읽어서 반환"""
    if not template_path.is_file():
        raise RuntimeError(f"템플릿 파일이 존재하지 않습니다: {template_path}")
    try:
        return template_path.read_text(encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"템플릿 파일을 읽는 중 오류 발생: {e}") from e


def combine_streams(
    file_stream: Iterator[str],
    existing_readme_content: str | None,
    readme_path: str,
    template_content: str | None,
    template_path: str | None,
) -> Iterator[str]:
    """기존 README 및 템플릿 내용을 파일 내용 스트림에 추가합니다."""
    if template_content and template_path:
        yield f"===== FILE: {template_path} (README 템플릿) =====\n\n"
        yield template_content

    if existing_readme_content:
        yield f"===== FILE: {readme_path} (기존 README) =====\n\n"
        yield existing_readme_content

    yield from file_stream


from . import dir_text_collector
from .providers import get_provider
from .config import parse_args, DEFAULT_README_NAME
from .temp_utils import TempDirManager, read_content_from_files


def load_template(template_path: pathlib.Path) -> str:
    """템플릿 파일을 읽어서 반환"""
    if not template_path.is_file():
        raise RuntimeError(f"템플릿 파일이 존재하지 않습니다: {template_path}")
    try:
        return template_path.read_text(encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"템플릿 파일을 읽는 중 오류 발생: {e}") from e


def combine_streams(
    file_stream: Iterator[str],
    existing_readme_content: str | None,
    readme_path: str,
    template_content: str | None,
    template_path: str | None,
) -> Iterator[str]:
    """기존 README 및 템플릿 내용을 파일 내용 스트림에 추가합니다."""
    if template_content and template_path:
        yield f"===== FILE: {template_path} (README 템플릿) =====\n\n"
        yield template_content

    if existing_readme_content:
        yield f"===== FILE: {readme_path} (기존 README) =====\n\n"
        yield existing_readme_content

    yield from file_stream


def run() -> int:
    """애플리케이션의 메인 실행 로직"""
    args = parse_args()

    provider = get_provider(args.provider)

    pkg = pathlib.Path(args.package_path).resolve()
    if not pkg.exists() or not pkg.is_dir():
        raise RuntimeError(f"패키지 경로가 존재하지 않거나 디렉터리가 아닙니다: {pkg}")

    # 템플릿 처리
    template_content: str | None = None
    template_path: pathlib.Path | None = None
    if args.template:
        template_path = pathlib.Path(args.template).resolve()
        template_content = load_template(template_path)

    # 기존 README 처리
    readme_path = pkg / DEFAULT_README_NAME
    readme_exists = readme_path.exists()
    existing_readme_content: str | None = None
    if readme_exists:
        try:
            existing_readme_content = readme_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[경고] 기존 README 파일을 읽는 데 실패했습니다: {e}", file=sys.stderr)

    with TempDirManager(root_dir=str(pkg)) as temp_manager:
        # 모든 컨텍스트(템플릿, 기존 README, 파일 목록)를 스트림으로 결합
        file_content_stream = dir_text_collector.stream_all_files(str(pkg))
        full_content_stream = combine_streams(
            file_stream=file_content_stream,
            existing_readme_content=existing_readme_content,
            readme_path=str(readme_path),
            template_content=template_content,
            template_path=str(template_path) if template_path else None,
        )

        # 스트림을 임시 파일로 저장
        temp_file_paths = temp_manager.save_content_to_temp_files(
            full_content_stream
        )
        if not temp_file_paths:
            raise RuntimeError("컨텍스트를 임시 파일에 저장하지 못했습니다.")

        action = "new" if not readme_exists else "update"
        print(f"'{action}' 액션을 시작합니다.")

        # 프롬프트 생성 및 LLM 호출
        generated_prompt = ""
        if action == "new":
            generated_prompt = provider.build_prompt_new(
                temp_file_paths, args.request
            )
        else:  # update
            generated_prompt = provider.build_prompt_update(
                temp_file_paths, args.request
            )

        readme_content = provider.call_llm(generated_prompt)

        # 결과 출력/저장
        if args.stdout:
            sys.stdout.write(readme_content)
        else:
            readme_path.write_text(readme_content, encoding="utf-8")
            print(f"[정보] README 갱신 완료: {readme_path}")

    return 0


def main() -> int:
    try:
        return run()
    except (ValueError, RuntimeError) as e:
        print(f"[에러] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[치명적 에러] 예상치 못한 오류가 발생했습니다: {e}", file=sys.stderr)
        return 1
