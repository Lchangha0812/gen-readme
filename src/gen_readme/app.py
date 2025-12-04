import pathlib
import sys

from . import git_utils
from .providers import get_provider
from .config import parse_args, DEFAULT_README_NAME, DEFAULT_TEMPLATE_FILE


def load_template(template_path: pathlib.Path) -> str:
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise RuntimeError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
    except UnicodeDecodeError:
        raise RuntimeError(f"템플릿 파일을 UTF-8로 읽을 수 없습니다: {template_path}")


def main() -> int:
    args = parse_args()

    try:
        provider = get_provider(args.provider)
    except ValueError as e:
        print(f"[에러] {e}", file=sys.stderr)
        return 1

    pkg = pathlib.Path(args.package_path).resolve()
    if not pkg.exists() or not pkg.is_dir():
        print(f"[에러] 패키지 경로가 존재하지 않거나 디렉터리가 아닙니다: {pkg}", file=sys.stderr)
        return 1

    template_text: str | None = None
    if args.template:
        template_path = pathlib.Path(args.template)
        try:
            template_text = load_template(template_path)
        except RuntimeError as e:
            print(f"[에러] {e}", file=sys.stderr)
            return 1

    readme_path = pkg / DEFAULT_README_NAME
    readme_exists = readme_path.exists()

    diff_text = None
    try:
        diff_text = git_utils.get_git_diff_for_path(pkg)
    except Exception:
        # git이 없거나, repo가 아니거나, 에러가 나면 그냥 무시하고 diff 없음으로 처리
        diff_text = None

    # 1. 파일 상태에 따라 액션 결정
    action = ""
    if not readme_exists:
        action = "new"
        print(f"[{args.prompt_mode} mode] 신규 README 생성을 시작합니다.")
    elif diff_text:
        action = "update_with_diff"
        print(f"[{args.prompt_mode} mode] Git diff를 기반으로 README 수정을 시작합니다.")
    else:
        action = "update_full_scan"
        print(f"[{args.prompt_mode} mode] 전체 코드를 기반으로 README 개선을 시작합니다.")

    # 2. 모드와 액션에 따라 적절한 프롬프트 생성 메서드 호출
    generated_prompt = ""
    if args.prompt_mode == "direct":
        if action == "new":
            generated_prompt = provider.build_direct_prompt_new(pkg, args.request)
        elif action == "update_with_diff":
            generated_prompt = provider.build_direct_prompt_update_with_diff(pkg, diff_text, args.request)
        else:  # update_full_scan
            generated_prompt = provider.build_direct_prompt_update_full_scan(pkg, args.request)
    else:  # structured
        if action == "new":
            generated_prompt = provider.build_prompt_new(pkg, template_text, args.request)
        elif action == "update_with_diff":
            generated_prompt = provider.build_prompt_update_with_diff(pkg, template_text, diff_text, args.request)
        else:  # update_full_scan
            generated_prompt = provider.build_prompt_update_full_scan(pkg, template_text, args.request)
    
    # LLM 호출
    try:
        readme_content = provider.call_llm(generated_prompt, prompt_mode=args.prompt_mode)
    except RuntimeError as e:
        print(f"[에러] {e}", file=sys.stderr)
        return 1

    if args.stdout:
        sys.stdout.write(readme_content)
    else:
        readme_path.write_text(readme_content, encoding="utf-8")
        print(f"[정보] README 갱신 완료: {readme_path}")

    return 0