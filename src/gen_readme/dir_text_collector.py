import os
from typing import Callable, Iterator


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


def stream_all_files(
    root_dir: str,
    skip_hidden: bool = True,
    file_filter: Callable[[str], bool] | None = None,
) -> Iterator[str]:
    """
    주어진 디렉터리를 재귀적으로 돌면서 '읽을 수 있는' 파일 내용을
    16KB 스트림(generator)으로 반환한다.

    :param root_dir: 시작 디렉터리 경로
    :param skip_hidden: 숨김 파일/디렉터리(.으로 시작)를 건너뛸지 여부
    :param file_filter: 파일 경로를 받아 True/False를 리턴하는 필터 함수.
    :return: 파일 내용을 청크 단위로 yield하는 제너레이터
    """
    CHUNK_SIZE = 16 * 1024

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 숨김 디렉터리 스킵
        if skip_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if skip_hidden and filename.startswith("."):
                continue

            file_path = os.path.join(dirpath, filename)

            if os.path.islink(file_path):
                continue

            if file_filter is not None and not file_filter(file_path):
                continue

            if is_probably_binary(file_path):
                continue

            yield f"\n\n===== FILE: {file_path} =====\n\n"

            try:
                # 스트리밍 방식에서는 인코딩을 미리 확정해야 하므로,
                # 가장 무난한 utf-8(에러 무시)를 사용합니다.
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    while True:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                print(f"[WARN] 파일 스트리밍 읽기 실패: {file_path} ({e})")
                continue
