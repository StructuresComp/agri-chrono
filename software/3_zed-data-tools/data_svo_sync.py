import os
import time
import threading
import argparse
import signal
import sys
import pyzed.sl as sl

stop_event = threading.Event()

class ZEDSVORecorder(threading.Thread):
    def __init__(self, serial_number, name, base_path, sync_time):
        super().__init__(name=name)
        self.serial = serial_number
        self.name = name
        self.base_path = base_path
        self.sync_time = sync_time
        self.running = True
        self.ready_sent = False

        self.cam = sl.Camera()

        init = sl.InitParameters()
        input_type = sl.InputType()
        input_type.set_from_serial_number(serial_number)
        init.input = input_type
        init.depth_mode = sl.DEPTH_MODE.NEURAL
        init.coordinate_units = sl.UNIT.METER
        init.camera_resolution = sl.RESOLUTION.HD1080
        init.camera_fps = 15

        status = self.cam.open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError(f"Failed to open ZED camera {serial_number}: {status}")

        svo_path = os.path.join(base_path, f"{name}.svo2")
        rec_params = sl.RecordingParameters(svo_path, sl.SVO_COMPRESSION_MODE.LOSSLESS)
        rec_status = self.cam.enable_recording(rec_params)
        if rec_status != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError(f"Failed to enable SVO recording for camera {serial_number}: {rec_status}")

        self.runtime = sl.RuntimeParameters()
        self.info_csv = open(os.path.join(self.base_path, f"{self.name}_info.csv"), "w")
        self.info_csv.write("frame_id,rel_time,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n")
        self.sensors_data = sl.SensorsData()

    def run(self):
        count = 0
        while self.running and not stop_event.is_set():
            if self.cam.grab(self.runtime) == sl.ERROR_CODE.SUCCESS:
                now = time.time()
                rel_time = now - self.sync_time

                if not self.ready_sent:
                    print(f"[READY] {self.name}")
                    self.ready_sent = True

                if self.cam.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS:
                    imu = self.sensors_data.get_imu_data()
                    accel = imu.get_linear_acceleration()
                    gyro = imu.get_angular_velocity()

                    self.info_csv.write(f"{count},{rel_time:.6f},{accel[0]},{accel[1]},{accel[2]},{gyro[0]},{gyro[1]},{gyro[2]}\n")
                    self.info_csv.flush()

                count += 1
            else:
                time.sleep(0.005)
        print(f"[{self.name}] Exiting safely.")

    def stop(self):
        self.running = False
        stop_event.set()
        self.join()
        self.info_csv.close()
        self.cam.disable_recording()
        self.cam.close()
        print(f"[{self.name}] Stopped.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Output directory path")
    parser.add_argument("--sync_time", required=True, type=float, help="Shared sync timestamp (float, seconds)")
    args = parser.parse_args()

    base_path = os.path.expanduser(args.output)
    os.makedirs(base_path, exist_ok=True)

    rec_L = ZEDSVORecorder(serial_number=[Serial_number], name="L", base_path=base_path, sync_time=args.sync_time)
    rec_R = ZEDSVORecorder(serial_number=[Serial_number], name="R", base_path=base_path, sync_time=args.sync_time)

    rec_L.start()
    rec_R.start()

    def signal_handler(sig, frame):
        print("[🛑] Stopping...")
        rec_L.stop()
        rec_R.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
