# gen-readme

LLM을 활용하여 프로젝트의 `README.md` 파일을 자동으로 생성하고 관리하는 CLI 도구입니다.

## 🚀 주요 기능

- **코드베이스 자동 분석**: 지정된 디렉터리의 모든 소스 코드를 재귀적으로 탐색하고 분석하여 컨텍스트를 수집합니다.
- **신규 README 생성**: `README.md` 파일이 없는 프로젝트에서 코드 분석을 바탕으로 최적의 구조와 내용을 담은 새로운 README를 생성합니다.
- **기존 README 업데이트 및 개선**: 이미 `README.md` 파일이 존재하는 경우, 코드 변경사항을 반영하여 내용을 최신 상태로 업데이트하고 구조를 개선합니다.
- **유연한 LLM 연동**: Provider 패턴을 통해 Gemini 외 다른 LLM 모델로 확장이 용이한 구조로 설계되었습니다.
- **간편한 사용법**: 직관적인 CLI 인터페이스를 통해 복잡한 설정 없이 즉시 사용할 수 있습니다.

## 🏗️ 아키텍처

`gen-readme`는 명확한 역할 분리를 통해 효율적으로 동작하도록 설계되었습니다.

1.  **컨텍스트 수집 (`dir_text_collector.py`)**
    -   지정된 경로의 모든 텍스트 기반 소스 코드를 스트림(stream) 형태로 읽어들입니다.
    -   바이너리 파일, 링크, 숨김 파일(`.git`, `.vscode` 등)은 자동으로 제외하여 노이즈를 최소화합니다.

2.  **컨텍스트 관리 (`temp_utils.py`)**
    -   수집된 대용량 컨텍스트를 LLM에 안전하게 전달하기 위해 일정 크기(`16KB`)의 임시 파일들로 분할하여 저장합니다.
    -   프로그램 종료 시 생성된 임시 파일들을 자동으로 정리합니다.

3.  **프롬프트 엔지니어링 (`prompting.py`)**
    -   'Developer Advocate'로서의 역할을 부여하는 시스템 프롬프트를 정의합니다.
    -   README 신규 생성(`build_prompt_new`)과 업데이트(`build_prompt_update`) 상황에 맞춰 최적화된 프롬프트를 동적으로 구성합니다.

4.  **LLM 연동 (`providers/`)**
    -   `ReadmeProvider` 추상 클래스를 통해 다양한 LLM 서비스를 지원할 수 있는 확장 포인트를 제공합니다.
    -   현재 `GeminiReadmeProvider`가 구현되어 있으며, 시스템에 설치된 `gemini` CLI를 호출하여 작업을 수행합니다.

5.  **대화형 오케스트레이션 (`gemini_orchestrator.py`)**
    -   단순한 단방향 호출이 아닌, `gemini` CLI와 대화형 세션(interactive session)을 생성하고 관리합니다.
    -   초기 프롬프트 전달 후, 완전한 마크다운 결과물을 얻기 위해 필요시 추가적인 확인/요청 메시지를 자동으로 전송하여 결과물의 품질을 보장합니다.

6.  **메인 애플리케이션 (`app.py`)**
    -   CLI 인자를 파싱하고 전체 작업 흐름을 총괄합니다.
    -   LLM으로부터 최종 생성된 `README.md` 콘텐츠를 표준 출력(stdout)으로 보여주거나 실제 파일에 저장합니다.

## 📦 설치

1.  **사전 요구사항**: 이 도구는 `gemini` CLI를 내부적으로 호출합니다. 따라서 시스템의 `PATH` 환경변수에 `gemini` 명령이 등록되어 있어야 합니다.

2.  **패키지 설치**:
    ```bash
    # 저장소를 클론합니다.
    git clone https://github.com/your-username/gen-readme.git
    cd gen-readme

    # pip를 사용하여 설치합니다.
    pip install .
    ```

## ⚙️ 사용법

`gen-readme` CLI는 터미널에서 다음과 같이 사용할 수 있습니다.

### 기본 사용법

-   **현재 디렉터리 기준 README 생성/업데이트**:
    ```bash
    python -m gen-readme
    ```

-   **특정 프로젝트 디렉터리 지정**:
    ```bash
    python -m gen-readme /path/to/your/project
    ```

### 옵션

-   **추가 요청 전달 (`-r`, `--request`)**: LLM에게 특정 맥락이나 요구사항을 추가로 전달할 수 있습니다.
    ```bash
    python -m gen-readme -r "이 프로젝트는 FastAPI 기반의 주문 처리 마이크로서비스입니다. 주요 도메인 모델 중심으로 설명해주세요."
    ```

-   **결과를 파일 대신 화면에 출력 (`--stdout`)**: `README.md` 파일을 직접 생성/수정하지 않고, 생성될 내용을 터미널에서 먼저 확인하고 싶을 때 유용합니다.
    ```bash
    python -m gen-readme --stdout
    ```

-   **LLM 프로바이더 선택 (`-p`, `--provider`)**: 사용할 LLM 프로바이더를 선택합니다. (현재 `gemini`가 기본값이며 유일한 옵션)
    ```bash
    python -m gen-readme -p gemini
    ```