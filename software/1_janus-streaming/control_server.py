import os
import time
import threading
from flask import Flask
from flask_socketio import SocketIO

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import psutil
import shutil

from subprocess import Popen, PIPE
import signal, atexit
from datetime import datetime

# Initialize ROS 2 node
rclpy.init()
node = rclpy.create_node('web_control_node')
pub = node.create_publisher(Twist, '/cmd_vel', 10)

app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins='*',
    ping_interval=5,
    ping_timeout=1
)

record_process = None  # Tuple of (ZED process, Livox process)
down_keys = set()
should_update_twist = True  # Controls update_loop publishing

# PTZ state
pan = 0
tilt = 0
zoom = 0
ptz_lock = threading.Lock()
prev_pan = pan
prev_tilt = tilt
prev_zoom = zoom

pan_min, pan_max = -468000, 468000
tilt_min, tilt_max = -324000, 324000
zoom_min, zoom_max = 0, 100
pan_step = 3600 * 5
tilt_step = 7200 * 2
zoom_step = 10

linear_speed = 0.5
angular_speed = 0.5
MAX_LINEAR_SPEED = 1.5
MIN_LINEAR_SPEED = 0.1
MAX_ANGULAR_SPEED = 1.0
MIN_ANGULAR_SPEED = 0.1

def update_ptz():
    global pan, tilt, zoom, prev_pan, prev_tilt, prev_zoom
    updated = False
    with ptz_lock:
        if 'w' in down_keys:
            tilt = min(tilt + tilt_step, tilt_max)
            updated = True
        if 's' in down_keys:
            tilt = max(tilt - tilt_step, tilt_min)
            updated = True
        if 'a' in down_keys:
            pan = min(pan + pan_step, pan_max)
            updated = True
        if 'd' in down_keys:
            pan = max(pan - pan_step, pan_min)
            updated = True
        if 'x' in down_keys:
            zoom = min(zoom + zoom_step, zoom_max)
            updated = True
        if 'z' in down_keys:
            zoom = max(zoom - zoom_step, zoom_min)
            updated = True
        if updated and (pan != prev_pan or tilt != prev_tilt or zoom != prev_zoom):
            os.system(f"v4l2-ctl --set-ctrl=pan_absolute={pan} --set-ctrl=tilt_absolute={tilt} --set-ctrl=zoom_absolute={zoom}")
            prev_pan, prev_tilt, prev_zoom = pan, tilt, zoom

@socketio.on('keydown')
def handle_keydown(data):
    global linear_speed, angular_speed, should_update_twist
    print(f"⬇️ Key down: {data}")
    down_keys.add(data)
    should_update_twist = True  # re-enable if disabled

    updated = False
    if data == ',':
        linear_speed = max(MIN_LINEAR_SPEED, linear_speed - 0.1)
        updated = True
    elif data == '.':
        linear_speed = min(MAX_LINEAR_SPEED, linear_speed + 0.1)
        updated = True
    elif data == '[':
        angular_speed = max(MIN_ANGULAR_SPEED, angular_speed - 0.1)
        updated = True
    elif data == ']':
        angular_speed = min(MAX_ANGULAR_SPEED, angular_speed + 0.1)
        updated = True

    if updated:
        socketio.emit('speed_update', {'linear': linear_speed, 'angular': angular_speed})
        print(f"Updated speeds: Linear={linear_speed}, Angular={angular_speed}")

@socketio.on('keyup')
def handle_keyup(data):
    print(f"⬆️ Key up: {data}")
    down_keys.discard(data)
    twist = Twist()
    pub.publish(twist)

@socketio.on('connect')
def handle_connect():
    global should_update_twist
    should_update_twist = True
    print("🔄 WebSocket client connected — resuming twist updates")

@socketio.on('disconnect')
def handle_disconnect():
    print("🔌 WebSocket disconnected — forcing key release and robot stop")
    clear_keys_and_stop()

def clear_keys_and_stop():
    global down_keys, should_update_twist
    down_keys.clear()
    should_update_twist = False
    print("🛑 Keys cleared — stopping robot")
    twist = Twist()
    pub.publish(twist)
    print("📤 Published zero Twist")

def update_loop():
    global should_update_twist
    while True:
        if not should_update_twist:
            time.sleep(0.1)
            continue
        update_ptz()
        twist = Twist()
        if 'ArrowUp' in down_keys:
            twist.linear.x += linear_speed
        if 'ArrowDown' in down_keys:
            twist.linear.x -= linear_speed
        if 'ArrowLeft' in down_keys:
            twist.angular.z += angular_speed
        if 'ArrowRight' in down_keys:
            twist.angular.z -= angular_speed
        pub.publish(twist)
        time.sleep(0.1)

def ros_spin():
    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.1)

def get_wifi_name():
    try:
        result = os.popen("iwgetid -r").read().strip()
        return result if result else "Not connected"
    except Exception:
        return "Unavailable"
    
def system_monitor():
    while True:
        data_dir = os.path.expanduser("~/AgriChrono/data")
        os.makedirs(data_dir, exist_ok=True)
        total, used, free = shutil.disk_usage(data_dir)
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        wifi = get_wifi_name()
        
        socketio.emit('sysmon', {
            'cpu': cpu,
            'mem': mem,
            'used_gb': round(used / (1024**3), 1),
            'total_gb': round(total / (1024**3), 1),
            'used_pct': round((used / total) * 100, 1),
            'linear_mps': round(linear_speed, 2),
            'linear_mph': round(linear_speed * 2.23694, 2),
            'wifi': wifi,
        })
        time.sleep(1)

@socketio.on('start_recording')
def handle_start_recording(filename):
    global record_process
    if record_process is not None:
        print("⚠️ Recording already running")
        return

    print(f"📥 Start recording: {filename}")
    base_path = os.path.expanduser(f"~/AgriChrono/data/fargo/{filename}")
    timestamp_dir = datetime.now().strftime("%Y%m%d_%H%M")
    full_path = os.path.join(base_path, timestamp_dir)
    # full_path = f"{base_path}_{timestamp_dir}"
    rgbd_path = os.path.join(full_path, "RGB-D")
    lidar_path = os.path.join(full_path, "LiDAR")

    for path in [base_path, full_path, rgbd_path, lidar_path]:
    # for path in [full_path, rgbd_path, lidar_path]:
        os.makedirs(path, exist_ok=True)

    sync_time = time.time()
    with open(os.path.join(full_path, "sync_time.txt"), "w") as f:
        f.write(str(sync_time))
    print(f"[SYNC] sync_time.txt written: {sync_time}")

    zed_cmd = f"python3 ~/AgriChrono/3_zed-data-tools/data_svo_sync.py --output '{rgbd_path}' --sync_time {sync_time}"
    config_path = os.path.expanduser("~/AgriChrono/4_livox-data-tools/config/mid360_config.json")
    livox_cmd = f"~/AgriChrono/4_livox-data-tools/Livox-SDK2/record_lidar_sync/build/recorder_sync '{config_path}' '{lidar_path}'"

    zed_process = Popen(["bash", "-c", zed_cmd], stdout=PIPE, stderr=PIPE)
    livox_process = Popen(["bash", "-c", livox_cmd], stdout=PIPE, stderr=PIPE)

    record_process = (zed_process, livox_process)

@socketio.on('stop_recording')
def handle_stop_recording():
    global record_process
    if not record_process:
        print("⚠️ No recording in progress")
        return

    zed_process, livox_process = record_process
    print("🛑 Stopping ZED & Livox recording")
    zed_process.send_signal(signal.SIGINT)
    try:
        stdout, stderr = zed_process.communicate(timeout=10)
        print(f"[ZED] STDOUT:\n{stdout.decode()}\nSTDERR:\n{stderr.decode()}")
    except Exception as e:
        print(f"⚠️ ZED stop error: {e}")

    livox_process.terminate()
    livox_process.wait()
    record_process = None

# Register cleanup hooks
atexit.register(clear_keys_and_stop)
signal.signal(signal.SIGHUP, lambda s, f: clear_keys_and_stop())

# Start background threads
threading.Thread(target=system_monitor, daemon=True).start()
threading.Thread(target=ros_spin, daemon=True).start()
threading.Thread(target=update_loop, daemon=True).start()

if __name__ == '__main__':
    os.makedirs(os.path.expanduser("~/AgriChrono/data"), exist_ok=True)
    print("✅ WebSocket control server running on port 5000...")
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, use_reloader=False)