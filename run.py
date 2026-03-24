import sys
import os
import subprocess
import signal

# --- Config ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY    = os.path.join(SCRIPT_DIR, "main.py")
PYTHON     = sys.executable # Tự động dùng python từ venv nếu được gọi từ venv

def main():
    # 1. Khởi động API Server ở một Terminal mới (CREATE_NEW_CONSOLE)
    # Cách này nhanh hơn 'start cmd' vì gọi thẳng process mới từ OS
    api_proc = subprocess.Popen(
        [PYTHON, MAIN_PY],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=SCRIPT_DIR, # Chạy tại path cụ thể
        close_fds=True
    )

    try:
        # 2. Chạy lệnh claude ở terminal hiện tại, forward tất cả arg
        # Dùng Popen.wait() để bắt tín hiệu Ctrl+C mượt hơn
        claude_proc = subprocess.Popen(["claude"] + sys.argv[1:])
        claude_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()