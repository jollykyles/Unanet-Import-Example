from pathlib import Path
import shutil

def move_file_to_imu():
    cwd = Path.cwd()
    print(f"Current working directory: {cwd}")
    print("Files in current directory:")
    for f in cwd.iterdir():
        print(f" - {f.name}")

    remote_file = cwd / "expenses.csv"
    local_dir = cwd / "unanet_imu/data"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_file = local_dir / "import.csv"

    if remote_file.exists():
        shutil.move(str(remote_file), str(local_file))
        print(f"Moved {remote_file} to {local_file}")
    else:
        print(f"{remote_file} does not exist.")

if __name__ == "__main__":
