import smtplib, ssl
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials
sender_email = " "
receiver_emails = [" "]
password = " "  # Gmail app password

# Function to get active IPv4 addresses per interface
def get_ip_addresses():
    try:
        result = subprocess.check_output("ip -o -4 addr show | awk '{print $2 \": \" $4}'", shell=True)
        lines = result.decode().strip().split('\n')
        filtered = [line for line in lines if not line.startswith(("lo:", "tailscale", "enx"))]
        return "\n".join(filtered)
    except Exception as e:
        return f"Error getting IP: {e}"

# Function to get connected Wi-Fi SSID
def get_wifi_ssid():
    try:
        result = subprocess.check_output("iwgetid -r", shell=True)
        ssid = result.decode().strip()
        if ssid == "":
            return "Not connected to any Wi-Fi"
        else:
            return ssid
    except Exception as e:
        return f"Error getting Wi-Fi SSID: {e}"

# Function to get Wi-Fi link speed using iw dev
def get_wifi_speed():
    try:
        result = subprocess.check_output("iw dev wlP1p1s0 link", shell=True)
        lines = result.decode().strip().split('\n')
        bitrate_info = ""
        for line in lines:
            if "tx bitrate" in line or "bitrate" in line:
                # Replace "MBit/s" with "Mbps" for cleaner output
                bitrate_info += line.replace("MBit/s", "Mbps").strip() + "\n"
        if bitrate_info == "":
            return "No bitrate info available."
        else:
            return bitrate_info.strip()
    except Exception as e:
        return f"Error getting Wi-Fi speed: {e}"

# Collect network information
ip_info = get_ip_addresses()
wifi_ssid = get_wifi_ssid()
wifi_speed = get_wifi_speed()

# Prepare email content
subject = "📡 Jetson Network Info"
body = (
    "Jetson has connected to the network.\n\n"
    f"Current Wi-Fi SSID: {wifi_ssid}\n\n"
    f"Active IP Addresses:\n{ip_info}\n\n"
    f"Wi-Fi Link Speed:\n{wifi_speed}"
)

# Compose and send email
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
    print("✅ Email sent successfully.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
