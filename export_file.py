import os
import sys
import paramiko
import pandas as pd
import re, datetime
from pathlib import Path

def download_from_sftp():
    sftp_host = os.environ.get("SFTP_HOST")
    sftp_user = os.environ.get("SFTP_USER")
    sftp_private_key = os.environ.get("SFTP_RSA_PRIVATE_KEY")

    if not all([sftp_host, sftp_user, sftp_private_key]):
        print("Error: One or more SFTP credentials are missing.")
        sys.exit(1)

    key_path = Path("sftp_key.pem")
    key_path.write_text(sftp_private_key)
    key_path.chmod(0o600)

    remote_file = "person.csv"
    export_timestamp = f"person_{datetime.datetime.today()}.csv"
    local_dir = Path("unanet_imu/data")
    local_dir.mkdir(parents=True, exist_ok=True)
    local_file = local_dir / "person.csv"

    try:
        key = paramiko.RSAKey.from_private_key_file(str(key_path))
        print("Connecting to SFTP server...")
        transport = paramiko.Transport((sftp_host, 22))
        transport.connect(username=sftp_user, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        print(f"Downloading {remote_file} to {local_file}...")
        sftp.put(str(local_file), remote_file)
        sftp.put(str(local_file), export_timestamp)

        if local_file.exists():
            print(f"Download successful: {local_file} ({local_file.stat().st_size} bytes)")
        else:
            print("Download failed: File not found after transfer.")

        sftp.close()
        transport.close()

    except Exception as e:
        print(f"Error during SFTP download: {e}")
        sys.exit(1)
    finally:
        if key_path.exists():
            key_path.unlink()

if __name__ == "__main__":
    download_from_sftp()
