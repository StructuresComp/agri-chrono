#!/usr/bin/env python3

import os
import datetime
import smtplib, ssl
import time
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from glob import glob
import subprocess
import getpass

user = getpass.getuser()

# === Configuration ===
sender_email = " "
receiver_emails = [" "]
password = " "  # Gmail app password

today = datetime.datetime.now()
today_str = today.strftime("%Y%m%d")
date_human = today.strftime("%Y.%m.%d")
base_src = f"/home/{user}/AgriChrono/data/fargo"
base_dst = f"/mnt/{user}/fargo"
log_path = os.path.expanduser("~/AgriChrono/transfer_log.txt")
sites = ["site1-1", "site1-2", "site2", "site3"]
date_list = [
    today_str,
    (today - datetime.timedelta(days=1)).strftime("%Y%m%d")
]

# === Logging Function ===
def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

# === Email Sending Function ===
def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_emails, msg.as_string())
        return True
    except Exception as e:
        log(f"Email error: {e}")
        return False

# === Attempt to mount /mnt/USER ===
def try_mount():
    result = subprocess.run(["mountpoint", "-q", f"/mnt/{user}"])
    if result.returncode != 0:
        log(f"🔄 Trying to mount /mnt/{user} manually.")
        try:
            subprocess.run(["mount", f"/mnt/{user}"], check=True)
            log(f"✅ Mounted /mnt/{user} successfully.")
        except subprocess.CalledProcessError as e:
            log(f"❌ Failed to mount /mnt/{user}: {e}")
            return False
    return True

# === Attempt to unmount /mnt/USER ===
def try_unmount():
    time.sleep(2)
    if subprocess.run(["mountpoint", "-q", f"/mnt/{user}"]).returncode != 0:
        log(f"ℹ️ /mnt/{user} is already unmounted.")
        return
    try:
        subprocess.run(["sudo", "umount", f"/mnt/{user}"], check=True)
        log(f"✅ Unmounted /mnt/{user}.")
    except subprocess.CalledProcessError as e:
        log(f"⚠️ Failed to unmount /mnt/{user}: {e}")

# === Main Logic ===
def main():
    if not try_mount():
        send_email("❌ Transfer Aborted", f"Failed to mount /mnt/{user}.")
        return

    send_email("🚚 Transfer Started", f"Date: {date_human}\nHarddisk has been mounted.\nStarting data transfer of {date_human} folders...")

    transfer_summary = []
    total_success = True

    for site in sites:
        src_dir = os.path.join(base_src, site)
        dst_dir = os.path.join(base_dst, site)
        os.makedirs(dst_dir, exist_ok=True)

        matched = []
        for date_code in date_list:
            matched.extend(glob(os.path.join(src_dir, f"{date_code}_*")))

        if not matched:
            log(f"[{site}] No {date_list[0]}_* or {date_list[1]}_* folders found.")
            continue

        folder_names = [os.path.basename(f) for f in matched]
        transfer_summary.append(f"[{site}] {len(folder_names)} folder(s): {', '.join(folder_names)}")
        log(f"Started transfer for {site}: {folder_names}")

        for folder in matched:
            folder_name = os.path.basename(folder)
            dst_path = os.path.join(dst_dir, folder_name)

            if os.path.exists(dst_path):
                log(f"[{site}] Skipped {folder_name} (already exists in destination).")
                continue

            try:
                shutil.copytree(folder, dst_path)
                shutil.rmtree(folder)
                log(f"[{site}] Copied and deleted {folder_name}")
            except Exception as e:
                log(f"[{site}] Failed to copy/delete {folder_name}: {e}")
                total_success = False

    # Email result
    if transfer_summary:
        summary = "\n".join(transfer_summary)
        if total_success:
            send_email("✅ Data Transfer Complete", f"Date: {date_human}\n\nSuccessfully transferred:\n{summary}")
        else:
            send_email("❌ Data Transfer Failed", f"Date: {date_human}\n\nSome folders failed:\n{summary}\nCheck log: {log_path}")
    else:
        log("No data found in any site.")
        send_email("ℹ️ No Data Found", f"Date: {date_human}\nNo {today_str}_* folders found in site1, site2, or site3.\nNothing transferred.")

    try_unmount()

if __name__ == "__main__":
    main()
