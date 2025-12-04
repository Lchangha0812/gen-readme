"""
패키지를 `python -m gen_readme`로 실행할 수 있도록 합니다.
"""
import sys

from gen_readme.app import main

if __name__ == "__main__":
    # gen_readme.main.main()은 종료 코드를 반환하므로 sys.exit()로 전달합니다.
    sys.exit(main())
