import subprocess
import sys

def _execute_gemini_command(gemini_path: str, args: list[str]) -> subprocess.Popen:
    """gemini CLI 명령을 실행하고 Popen 객체를 반환한다."""
    command = [gemini_path] + args
    
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

def _wait_and_check_proc(proc: subprocess.Popen, error_message_prefix: str = "gemini 명령 실행 실패") -> str:
    """프로세스가 종료될 때까지 기다리고, 오류 발생 시 예외를 발생시킨다. stderr 내용을 반환한다."""
    stderr_output = proc.stderr.read() if proc.stderr else ""
    proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"{error_message_prefix} (코드 {proc.returncode}): {stderr_output.strip()}")
    
    return stderr_output