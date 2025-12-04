import os
from typing import Callable, Iterator
from . import git_utils


def is_probably_binary(file_path: str, block_size: int = 1024) -> bool:
    """
    파일의 앞부분을 조금 읽어서 바이너리 여부를 대략 판별한다.
    NULL 바이트(\0)가 있으면 바이너리 파일로 간주.
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(block_size)
        if b"\x00" in chunk:
            return True
        return False
    except Exception:
        # 열 수 없는 파일은 바이너리 취급해서 스킵
        return True


def _stream_files_from_git(root_dir: str, chunk_size: int) -> Iterator[str]:
    """Git 추적 파일을 스트리밍합니다."""
    tracked_files = git_utils.get_tracked_files(root_dir)
    if not tracked_files:
        print("[정보] Git 추적 파일을 찾을 수 없습니다.")
        return

    print(f"[정보] .gitignore를 기준으로 {len(tracked_files)}개의 파일을 수집합니다.")
    for file_path in tracked_files:
        if not os.path.exists(file_path) or os.path.islink(file_path):
            continue
        if is_probably_binary(file_path):
            continue
        
        relative_path = os.path.relpath(file_path, root_dir)
        yield f"\n\n===== FILE: {relative_path} =====\n\n"
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            print(f"[경고] 파일 읽기 실패: {file_path} ({e})")
            continue


def _stream_files_from_walk(
    root_dir: str, skip_hidden: bool, chunk_size: int
) -> Iterator[str]:
    """os.walk를 사용하여 모든 파일을 스트리밍합니다."""
    print("[정보] Git 저장소가 아니므로, 숨김 파일을 제외하고 모든 파일을 수집합니다.")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if skip_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if skip_hidden and filename.startswith("."):
                continue

            file_path = os.path.join(dirpath, filename)
            if os.path.islink(file_path) or is_probably_binary(file_path):
                continue
            
            relative_path = os.path.relpath(file_path, root_dir)
            yield f"\n\n===== FILE: {relative_path} =====\n\n"
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                print(f"[경고] 파일 읽기 실패: {file_path} ({e})")
                continue


def stream_all_files(
    root_dir: str,
    skip_hidden: bool = True,
    **kwargs, # 이전 버전 호환성을 위해 file_filter 등의 인자를 받음
) -> Iterator[str]:
    """
    디렉터리 파일 내용을 스트림으로 반환합니다.
    Git 저장소인 경우 .gitignore를 존중하고, 그렇지 않은 경우 모든 파일을 탐색합니다.
    """
    CHUNK_SIZE = 16 * 1024
    
    # git_utils.find_git_root는 pathlib.Path 객체를 요구합니다.
    from pathlib import Path

    if git_utils.find_git_root(Path(root_dir)):
        yield from _stream_files_from_git(root_dir, CHUNK_SIZE)
    else:
        yield from _stream_files_from_walk(root_dir, skip_hidden, CHUNK_SIZE)
