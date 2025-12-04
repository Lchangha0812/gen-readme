from typing import Any
import sys
from halo import Halo # Import Halo

from .gemini_client import _execute_gemini_command, _wait_and_check_proc
from .gemini_parser import parse_gemini_stream


def run_one_shot(gemini_path: str, prompt: str) -> str | None:
    """'direct' 모드를 위한 단일 호출을 실행합니다."""
    spinner = Halo(text='Gemini CLI에 직접 프롬프트 전송 중...', spinner='dots')
    spinner.start()
    proc = None
    try:
        proc = _execute_gemini_command(
            gemini_path,
            ["--output-format", "stream-json", prompt],
        )
        response = parse_gemini_stream(proc, parse_for_final_content=True)
        _wait_and_check_proc(proc, error_message_prefix="gemini 'direct' 모드 실행 실패")
        
        # 마크다운 제목으로 시작하지 않는 응답은 대화형 답변으로 간주
        if response and not response.startswith("#"):
            spinner.info("[정보] 'direct' 모드가 대화형으로 응답하여 'structured' 모드로 전환합니다.")
            return None
        spinner.succeed("Gemini CLI 직접 프롬프트 응답 완료!")
        return response
    except RuntimeError as e:
        spinner.fail(f"Gemini CLI 직접 프롬프트 실행 실패: {e}")
        print(f"[정보] 'direct' 모드 실행 실패: {e}. 'structured' 모드로 전환합니다.", file=sys.stderr)
        return None
    finally:
        if proc:
            proc.kill() # 혹시 모를 좀비 프로세스 방지


def run_conversation(gemini_path: str, role_prompt: str, task_prompt: str) -> str:
    """'structured' 모드를 위한 다단계 대화형 호출을 실행합니다."""

    MAX_CONVERSATION_TURNS = 5 # 무한 루프 방지를 위한 최대 턴 수
    spinner = Halo(text='Gemini CLI와 대화 시작 중...', spinner='dots')
    spinner.start()

    try:
        # 1. 세션 초기화 (역할 부여)
        spinner.text = "Gemini CLI에 역할 부여 중..."
        proc_init = _execute_gemini_command(gemini_path, [role_prompt])
        _wait_and_check_proc(proc_init, error_message_prefix="gemini 세션 초기화 실패")
        
        # 2. 메인 프롬프트 전달 (작업 내용 할당)
        spinner.text = "Gemini CLI에 주요 작업 전달 중..."
        proc_task = _execute_gemini_command(gemini_path, ["--resume", "latest", task_prompt])
        _wait_and_check_proc(proc_task, error_message_prefix="gemini 메인 프롬프트 전달 실패")

        # 3. 대화형 루프를 통해 최종 결과 요청
        for i in range(MAX_CONVERSATION_TURNS):
            final_command = (
                "지금까지의 지시와 대화를 바탕으로, 다른 대화나 추가 설명 없이, 오직 README.md 파일의 최종 마크다운 내용만 출력해줘. 이것이 최종 결과물이다."
                if i == MAX_CONVERSATION_TURNS - 1 # 마지막 턴에서는 더 강한 명령 사용
                else "계속해서 작업을 진행해줘." # 중간 턴에서는 진행 요청
            )

            spinner.text = f"대화형 턴 {i+1}/{MAX_CONVERSATION_TURNS} - 명령: '{final_command}'"
            
            proc_turn = _execute_gemini_command(
                gemini_path,
                ["--resume", "latest", "--output-format", "stream-json", final_command],
            )
            response_content = parse_gemini_stream(proc_turn, parse_for_final_content=True)
            _wait_and_check_proc(proc_turn, error_message_prefix=f"gemini 대화 턴 {i+1} 실패")

            # 응답이 마크다운 제목으로 시작하면 최종 결과로 간주하고 반환
            if response_content and response_content.startswith("#"):
                spinner.succeed("Gemini CLI 대화 완료 및 README 생성 성공!")
                return response_content
        
        spinner.fail(f"{MAX_CONVERSATION_TURNS}번의 시도 후에도 유효한 README 콘텐츠를 생성하지 못했습니다.")
        raise RuntimeError(f"{MAX_CONVERSATION_TURNS}번의 시도 후에도 유효한 README 콘텐츠를 생성하지 못했습니다.")
    except Exception as e:
        spinner.fail(f"Gemini CLI 대화 중 오류 발생: {e}")
        raise # 오류 다시 발생