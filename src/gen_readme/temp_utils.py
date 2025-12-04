import tempfile
import os
import shutil
import sys
from typing import List, Iterator, Optional

CHUNK_SIZE = 16 * 1024  # 16KB


class TempDirManager:
    """
    임시 디렉터리 및 그 안의 파일 생성을 관리하고 사용 후 정리하는 컨텍스트 관리자.

    사용 예시:
    with TempDirManager() as temp_manager:
        file_paths = temp_manager.save_content_to_temp_files(content_iterator)
        # ... 파일 처리 ...
    # 'with' 블록을 빠져나가면 임시 디렉터리와 모든 파일이 자동으로 삭제됩니다.
    """

    def __init__(self, root_dir: Optional[str] = None):
        self._root_dir = root_dir
        self.temp_dir: Optional[str] = None
        self.created_files: List[str] = []

    def __enter__(self) -> "TempDirManager":
        try:
            self.temp_dir = tempfile.mkdtemp(dir=self._root_dir)
            print(f"[정보] 임시 디렉터리가 생성되었습니다: {self.temp_dir}")
        except Exception as e:
            print(f"[에러] 임시 디렉터리 생성에 실패했습니다: {e}", file=sys.stderr)
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def save_content_to_temp_files(
        self, content_iterator: Iterator[str]
    ) -> List[str]:
        """
        주어진 내용 스트림을 16KB 단위로 나누어 임시 파일들로 저장합니다.
        파일은 관리자 인스턴스에 의해 추적됩니다.

        :param content_iterator: 파일에 저장할 문자열 내용 스트림
        :return: 생성된 임시 파일들의 경로 리스트.
        """
        if not self.temp_dir:
            raise Exception("임시 디렉터리가 설정되지 않았습니다. 'with' 구문 안에서 사용해야 합니다.")

        f = None
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
                        dir=self.temp_dir,
                    )
                    self.created_files.append(f.name)

                f.write(chunk)

                if f.tell() > CHUNK_SIZE:
                    f.close()
                    f = None

            if f is not None:
                f.close()

            if len(self.created_files) > 1:
                print(
                    f"[정보] 수집된 컨텍스트가 {len(self.created_files)}개의 임시 파일로 분할 저장되었습니다."
                )
                for path in self.created_files:
                    print(f"  - {path}")
            elif self.created_files:
                print(
                    f"[정보] 수집된 컨텍스트가 임시 파일에 저장되었습니다: {self.created_files[0]}"
                )

            return self.created_files

        except Exception as e:
            if f:
                f.close()
            print(f"[경고] 임시 파일 생성에 실패했습니다: {e}", file=sys.stderr)
            # 실패 시에도 __exit__에서 정리되므로 여기서 즉시 삭제할 필요는 없음
            return []

    def cleanup(self):
        """임시 디렉터리와 그 안의 모든 파일을 삭제합니다."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"[정보] 임시 디렉터리 및 모든 파일이 삭제되었습니다: {self.temp_dir}")
            except OSError as e:
                print(
                    f"[에러] 임시 디렉터리 삭제 중 오류가 발생했습니다: {self.temp_dir} ({e})",
                    file=sys.stderr,
                )
        self.temp_dir = None
        self.created_files = []


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
