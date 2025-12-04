import sys
from halo import Halo

from .gemini_client import _execute_gemini_command, _wait_and_check_proc
from .gemini_parser import parse_gemini_stream


def run_conversation(gemini_path: str, task_prompt: str) -> str:
    """'structured' 모드를 위한 UUID 기반 세션 대화형 호출을 실행합니다."""

    MAX_CONVERSATION_TURNS = 5
    spinner = Halo(text='Gemini CLI와 대화 시작 중...', spinner='dots')
    spinner.start()

    try:
        spinner.text = "Gemini CLI 세션 초기화 및 작업 전달 중..."
        proc_init = _execute_gemini_command(gemini_path, ["--output-format", "stream-json", task_prompt])
        session_id, final_content = parse_gemini_stream(proc_init)
        _wait_and_check_proc(proc_init, error_message_prefix="gemini 세션 초기화 및 작업전달 실패")

        if not session_id:
            raise RuntimeError("Gemini CLI에서 세션 ID를 획득하지 못했습니다.")
        spinner.info(f"Gemini 세션 시작됨 (ID: ...{session_id[-6:]})")
        
        if not final_content:
            #  혹시 바로 마크다운 안줄수도 있으니 대화형 루프를 통해 최종 결과 요청
            for i in range(MAX_CONVERSATION_TURNS):
                final_command = (
                    "지금까지의 지시와 대화를 바탕으로, 다른 대화나 추가 설명 없이, 오직 README.md 파일의 최종 마크다운 내용만 출력해줘. 이것이 최종 결과물이다."
                    if i == MAX_CONVERSATION_TURNS - 1
                    else "계속해서 작업을 진행해줘."
                )
                spinner.text = f"대화형 턴 {i+1}/{MAX_CONVERSATION_TURNS}..."
                
                proc_turn = _execute_gemini_command(
                    gemini_path,
                    ["--resume", session_id, "--output-format", "stream-json", final_command],
                )
                _, response_content = parse_gemini_stream(proc_turn)
    
                _wait_and_check_proc(proc_turn, error_message_prefix=f"gemini 대화 턴 {i+1} 실패")
                if response_content and response_content.startswith("#"):
                    spinner.succeed("Gemini CLI 대화 완료 및 README 생성 성공!")
                    return response_content
            
            spinner.fail(f"{MAX_CONVERSATION_TURNS}번의 시도 후에도 유효한 README 콘텐츠를 생성하지 못했습니다.")
            raise RuntimeError(f"{MAX_CONVERSATION_TURNS}번의 시도 후에도 유효한 README 콘텐츠를 생성하지 못했습니다.")

        spinner.succeed("Gemini CLI 대화 완료 및 README 생성 성공!")
        return final_content

    except Exception as e:
        spinner.fail(f"Gemini CLI 대화 중 오류 발생: {e}")
        raise

