import paramiko
import getpass

def upload_text_file_to_mainframe(local_file, remote_file, hostname, username, password):
    try:
        print(f"🚀 Connecting to {hostname}...")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password)

        print("🔗 Connected successfully.")

        sftp = ssh.open_sftp()
        print(f"📤 Uploading {local_file} to {remote_file} (after converting to EBCDIC)...")

        # Step 1: Read local text file in UTF-8
        with open(local_file, 'r', encoding='utf-8') as f:
            utf8_text = f.read()

        # Step 2: Normalize newlines (Mainframes often prefer \r)
        utf8_text = utf8_text.replace('\n', '\r')

        # Step 3: Encode text to EBCDIC (cp037 for IBM mainframe)
        ebcdic_data = utf8_text.encode('cp037')

        # Step 4: Upload to remote mainframe
        with sftp.file(remote_file, mode='wb') as remote_file_obj:
            remote_file_obj.write(ebcdic_data)

        sftp.close()
        ssh.close()

        print(f"✅ Upload successful! {local_file} has been converted to EBCDIC and uploaded to {remote_file}")

    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    LOCAL_FILE = "C:/Users/SHIVNERI/Downloads/classified_complaints.txt"  # <- TXT file now
    REMOTE_FILE = "/z/z67429/classified_complaints.txt"  # <- TXT file on mainframe
    HOSTNAME = "204.90.115.200"
    USERNAME = "z67429"

    PASSWORD = getpass.getpass(prompt="🔒 Enter your mainframe password: ")

    upload_text_file_to_mainframe(LOCAL_FILE, REMOTE_FILE, HOSTNAME, USERNAME, PASSWORD)
