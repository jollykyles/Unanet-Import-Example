from pathlib import Path
import shutil

def move_file_to_imu():
    cwd = Path.cwd()
    print(f"Current working directory: {cwd}")

    # Go up one level to find expenses.csv
    remote_file = cwd.parent / "expenses.csv"
    local_dir = cwd / "data"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_file = local_dir / "import.csv"

    if remote_file.exists():
        shutil.move(str(remote_file), str(local_file))
        print(f"Moved {remote_file} to {local_file}")
    else:
        print(f"{remote_file} does not exist.")

if __name__ == "__main__":
    move_file_to_imu()
