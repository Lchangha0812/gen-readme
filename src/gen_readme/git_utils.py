import pathlib
import subprocess


def run_cmd(cmd, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def find_git_root(start: pathlib.Path) -> pathlib.Path | None:
    """
    start 기준으로 상위 디렉터리를 올라가며 git 루트를 찾는다.
    안전성을 위해 사용자의 홈 디렉터리까지만 탐색한다.
    """
    current = start.resolve()
    home = pathlib.Path.home()

    for parent in [current, *current.parents]:
        # parent가 디렉터리가 아니면 건너뜀 (예: 잘못된 경로)
        if not parent.is_dir():
            continue

        result = run_cmd(["git", "rev-parse", "--show-toplevel"], cwd=parent)
        if result.returncode == 0:
            return pathlib.Path(result.stdout.strip())

        # 홈 디렉터리까지 탐색했으면 더 이상 올라가지 않고 종료
        if parent == home:
            break
    return None


def get_git_diff_for_path(path: pathlib.Path) -> str | None:
    """
    특정 path에 대한 git diff가 있는지 확인하고, 있으면 diff 텍스트를 반환한다.
    우선 staged(--cached), 없으면 워킹트리 diff를 본다.
    """
    git_root = find_git_root(path)
    if git_root is None:
        return None

    rel = path.resolve().relative_to(git_root)

    # 1) staged diff
    cached = run_cmd(["git", "diff", "--cached", "--", str(rel)], cwd=git_root)
    if cached.returncode == 0 and cached.stdout.strip():
        return cached.stdout

    # 2) working tree diff
    working = run_cmd(["git", "diff", "--", str(rel)], cwd=git_root)
    if working.returncode == 0 and working.stdout.strip():
        return working.stdout

    return None
