import tempfile
import os
import atexit
import sys
from typing import List, Iterator

CHUNK_SIZE = 16 * 1024  # 16KB


def _cleanup_temp_file(path: str):
    """
    atexit 핸들러로 등록될 함수. 주어진 경로의 파일을 삭제합니다.
    """
    if path and os.path.exists(path):
        try:
            os.remove(path)
            print(f"[정보] 임시 파일이 삭제되었습니다: {path}")
        except OSError as e:
            print(f"[에러] 임시 파일 삭제 중 오류가 발생했습니다: {path} ({e})", file=sys.stderr)


def save_content_to_temp_files(content_iterator: Iterator[str], root_dir: str) -> List[str]:
    """
    주어진 내용 스트림(iterator)을 16KB 단위로 나누어 지정된 디렉터리에 임시 파일들로 저장하고,
    프로그램 종료 시 해당 파일들이 삭제되도록 atexit 핸들러를 등록합니다.

    :param content_iterator: 파일에 저장할 문자열 내용 스트림
    :param root_dir: 임시 파일을 생성할 디렉터리
    :return: 생성된 임시 파일들의 경로 리스트.
    """
    created_files: List[str] = []
    f = None
    file_path = None
    file_count = 0

    try:
        for chunk in content_iterator:
            if f is None:
                file_count += 1
                f = tempfile.NamedTemporaryFile(
                    "w",
                    encoding="utf-8",
                    suffix=f"_part_{file_count}.txt",
                    delete=False,
                    dir=root_dir, 
                )
                file_path = f.name
                created_files.append(file_path)
                atexit.register(_cleanup_temp_file, file_path)

            f.write(chunk)

            if f.tell() > CHUNK_SIZE:
                f.close()
                f = None
        
        if f is not None:
            f.close()
            
        if len(created_files) > 1:
            print(f"[정보] 수집된 컨텍스트가 {len(created_files)}개의 임시 파일로 분할 저장되었습니다.")
            for path in created_files:
                print(f"  - {path}")
        elif created_files:
            print(f"[정보] 수집된 컨텍스트가 임시 파일에 저장되었습니다: {created_files[0]}")
        
        return created_files

    except Exception as e:
        if f:
            f.close()
        print(f"[경고] 임시 파일 생성에 실패했습니다: {e}", file=sys.stderr)
        for path in created_files:
            _cleanup_temp_file(path)
        return []

def read_content_from_files(file_paths: List[str]) -> str:
    """
    파일 경로 리스트를 받아 내용을 하나의 문자열로 합쳐 반환합니다.
    """
    parts = []
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                parts.append(f.read())
        except Exception as e:
            print(f"[경고] 컨텍스트 파일 읽기 실패: {file_path} ({e})")
    return "".join(parts)