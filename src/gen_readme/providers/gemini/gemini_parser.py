import json
import sys
import subprocess


def parse_gemini_stream(proc: subprocess.Popen) -> tuple[str | None, str | None]:
    """
    Popen 프로세스의 stdout 스트림을 처리하여 세션 ID와 최종 콘텐츠를 추출합니다.
    스트리밍되는 'message' 타입의 content들을 모두 합쳐서 최종 콘텐츠를 만듭니다.
    """
    session_id: str | None = None
    response_parts = []
    
    if proc.stdout:
        for line in proc.stdout:
            # print(f"[DEBUG] Raw JSON: {line.strip()}", file=sys.stderr)
            try:
                data = json.loads(line)
                
                # type: init -> 세션 ID 추출
                if data.get("type") == "init" and "session_id" in data:
                    session_id = data["session_id"]
                    print(f"[DEBUG] 세션 ID 발견: {session_id}", file=sys.stderr)

                # type: thought -> CoT 과정에서 독백이 있다면 출력
                elif data.get("type") == "thought" and "content" in data:
                    print(f"[CoT] {data['content']}", file=sys.stderr, flush=True)

                # type: message -> content 조각 수집
                elif data.get("type") == "message" and data.get("role") == "assistant" and "content" in data:
                    response_parts.append(data["content"])
                
                # type: result, status: success -> 성공적인 스트림 종료 확인
                elif data.get("type") == "result" and data.get("status") == "success":
                    print(f"[DEBUG] 스트림 성공적으로 종료됨.", file=sys.stderr)

            except (json.JSONDecodeError, KeyError):
                continue
    
    final_content = "".join(response_parts).strip() if response_parts else None

    return session_id, final_content