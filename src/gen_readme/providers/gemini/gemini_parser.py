import json
import sys
import subprocess # for Popen and PIPE

def parse_gemini_stream(proc: subprocess.Popen, parse_for_final_content: bool) -> str | None:
    """
    Popen 프로세스의 stdout, stderr 스트림을 처리합니다.
    parse_for_final_content 플래그에 따라 최종 콘텐츠를 파싱하거나, 스트림을 무시합니다.
    """
    final_content = None
    
    if parse_for_final_content:
        response_parts = []
        if proc.stdout:
            for line in proc.stdout:
                try:
                    data = json.loads(line)
                    if data.get("type") == "message" and data.get("role") == "assistant" and "content" in data:
                        response_parts.append(data["content"])
                    elif data.get("type") == "thought" and "content" in data:
                        print(f"[생각] {data['content']}", file=sys.stderr, flush=True)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # 첫 번째 message content가 실제 생성된 README일 가능성이 높음
        if response_parts:
            final_content = response_parts[0].strip()

    # 프로세스 종료까지 기다리고, 에러 메시지 처리 (gemini_client로 이동)
    # stderr_output = proc.stderr.read() if proc.stderr else ""
    # proc.wait()

    # if proc.returncode != 0:
    #     raise RuntimeError(f"gemini 실행 실패 (코드 {proc.returncode}): {stderr_output.strip()}")

    if parse_for_final_content and not final_content:
        # 이 에러는 호출하는 곳에서 프로세스 종료 후 체크하는 것이 더 적절 (stderr_output 필요)
        pass # raise RuntimeError(f"gemini CLI에서 유효한 텍스트 응답을 추출하지 못했습니다. Stderr:\n{stderr_output.strip()}")

    return final_content
