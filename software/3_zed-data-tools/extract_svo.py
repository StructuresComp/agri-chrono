import os
import time
import numpy as np
import pyzed.sl as sl
import cv2
import csv
import bisect
from tqdm import tqdm

# Load sensor data from CSV file
def load_timestamps_csv(path):
    data = {}
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            frame_id = int(row["frame_id"])
            data[frame_id] = {k: float(v) for k, v in row.items() if k != "frame_id"}
    return data

# Match frame IDs from L and R cameras based on timestamp tolerance
def generate_frame_id_pairs(csv_L, csv_R, tolerance=0.001):
    data_L = load_timestamps_csv(csv_L)  # dict: frame_id -> data dict
    data_R = load_timestamps_csv(csv_R)

    # Build sorted lists of (frame_id, timestamp) for L and R
    sorted_L = sorted((fid, data["timestamp"]) for fid, data in data_L.items())
    sorted_R = sorted((fid, data["timestamp"]) for fid, data in data_R.items())

    timestamps_R = [ts for _, ts in sorted_R]
    frame_ids_R = [fid for fid, _ in sorted_R]

    pair_dict = {"L": set(), "R": set()}
    matched_pairs = []

    for l_fid, l_ts in sorted_L:
        idx = bisect.bisect_left(timestamps_R, l_ts)
        candidates = []
        if idx > 0:
            candidates.append(idx-1)
        if idx < len(timestamps_R):
            candidates.append(idx)

        for c in candidates:
            r_fid = frame_ids_R[c]
            r_ts = timestamps_R[c]
            if abs(l_ts - r_ts) <= tolerance:
                pair_dict["L"].add(l_fid)
                pair_dict["R"].add(r_fid)
                matched_pairs.append((l_fid, r_fid))
                break

    print(f"[🔗] Fuzzy matched pairs (±{tolerance}s): {len(matched_pairs)}")
    return pair_dict, matched_pairs

# Point Cloud to PLY
def save_point_cloud_ply(filename, point_cloud):
    h, w, _ = point_cloud.shape
    # Reshape point cloud to a list of points: [x, y, z, rgba]
    valid_points = point_cloud.reshape(-1, 4)

    # Create a mask to filter out invalid points (NaN or infinite Z values)
    mask = np.isfinite(valid_points[:, 2])
    points = valid_points[mask]

    # Count of valid points
    num_points = points.shape[0]

    with open(filename, 'w') as ply_file:
        # Write PLY header
        ply_file.write('ply\n')
        ply_file.write('format ascii 1.0\n')
        ply_file.write(f'element vertex {num_points}\n')
        ply_file.write('property float x\n')
        ply_file.write('property float y\n')
        ply_file.write('property float z\n')
        ply_file.write('property uchar red\n')
        ply_file.write('property uchar green\n')
        ply_file.write('property uchar blue\n')
        ply_file.write('end_header\n')

        # Write point data: x, y, z, r, g, b
        for p in points:
            x, y, z, color = p
            if np.isnan(x) or np.isnan(y) or np.isnan(z):
                continue

            # Convert RGBA float32 to uint32 and extract RGB values
            color = np.uint32(np.float32(color).view(np.uint32))
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = (color) & 0xFF

            # Write point in ASCII PLY format
            ply_file.write(f"{x} {y} {z} {r} {g} {b}\n")

# Extract synchronized RGB, Depth data from L/R SVO files and save them along with a combined video and timestamp CSV
def extract_and_combine(svo_path_L, svo_path_R, output_dir, matched_pairs, saved_fps):
    # Initialize ZED cameras
    input_L = sl.InitParameters()
    input_L.set_from_svo_file(svo_path_L)
    input_L.svo_real_time_mode = False
    input_L.coordinate_units = sl.UNIT.MILLIMETER
    cam_L = sl.Camera()

    input_R = sl.InitParameters()
    input_R.set_from_svo_file(svo_path_R)
    input_R.svo_real_time_mode = False
    input_R.coordinate_units = sl.UNIT.MILLIMETER
    cam_R = sl.Camera()

    if cam_L.open(input_L) != sl.ERROR_CODE.SUCCESS:
        raise RuntimeError(f"❌ Failed to open {svo_path_L}")
    if cam_R.open(input_R) != sl.ERROR_CODE.SUCCESS:
        raise RuntimeError(f"❌ Failed to open {svo_path_R}")

    runtime = sl.RuntimeParameters()

    # Define output directory structure
    frame_dir = os.path.join(output_dir, "frames")
    depth_npy_dir = os.path.join(output_dir, "depth_npy")
    depth_png_dir = os.path.join(output_dir, "depth_png")
    pc_ply_dir = os.path.join(output_dir, "pointclooud_ply")
    # avi_path = os.path.join(output_dir, "combined.avi")
    avi_path = os.path.join(output_dir, "combined.mp4")

    frame_dir_L = os.path.join(frame_dir, "L")
    frame_dir_R = os.path.join(frame_dir, "R")
    depth_npy_dir_L = os.path.join(depth_npy_dir, "L")
    depth_npy_dir_R = os.path.join(depth_npy_dir, "R")
    depth_png_dir_L = os.path.join(depth_png_dir, "L")
    depth_png_dir_R = os.path.join(depth_png_dir, "R")
    pc_ply_dir_L = os.path.join(pc_ply_dir, "L")
    pc_ply_dir_R = os.path.join(pc_ply_dir, "R")

    # Create output folders
    for d in [frame_dir_L, frame_dir_R, depth_npy_dir_L, depth_npy_dir_R, depth_png_dir_L, depth_png_dir_R, pc_ply_dir_L, pc_ply_dir_R]:
        os.makedirs(d, exist_ok=True)

    cam_L.set_svo_position(0)
    cam_R.set_svo_position(0)

    # Get camera resolution for combined video layout
    info = cam_L.get_camera_information().camera_configuration.resolution
    width = info.width
    height = info.height
    combined_width = width * 2
    combined_height = height * 2

    # Setup video writer for 2x2 combined video
    video_writer = cv2.VideoWriter(avi_path,
                                    # cv2.VideoWriter_fourcc('M', '4', 'S', '2'),
                                    cv2.VideoWriter_fourcc(*'mp4v'),
                                    saved_fps,
                                    (combined_width, combined_height))

    # Pre-allocate sl.Mat objects for efficiency (reused every frame)
    img_L = sl.Mat()
    img_R = sl.Mat()
    depth_L = sl.Mat()
    depth_R = sl.Mat()
    depth_L_png = sl.Mat()
    depth_R_png = sl.Mat()
    point_cloud_L = sl.Mat()
    point_cloud_R = sl.Mat()

    # Load timestamps for matched frames
    L_info = dict(load_timestamps_csv(os.path.join(os.path.dirname(svo_path_L), "L_info.csv")))
    R_info = dict(load_timestamps_csv(os.path.join(os.path.dirname(svo_path_R), "R_info.csv")))

    # Open CSV file to log matched timestamps
    timestamp_csv_path = os.path.join(output_dir, "info.csv")
    with open(timestamp_csv_path, "w", newline="") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["L_frame_id", "R_frame_id", "L_timestamp", "R_timestamp", "relative_time", "L_accel_x", "L_accel_y", "L_accel_z", "L_gyro_x", "L_gyro_y", "L_gyro_z", "R_accel_x", "R_accel_y", "R_accel_z", "R_gyro_x", "R_gyro_y", "R_gyro_z"])

        # Determine first timestamp as reference (0s)
        if matched_pairs:
            t0 = min(L_info[l]['timestamp'] for l, r in matched_pairs)

            # Process each matched frame pair
            for l_fid, r_fid in tqdm(matched_pairs, desc="Extracting frames"):
                cam_L.set_svo_position(l_fid)
                cam_R.set_svo_position(r_fid)

                if cam_L.grab(runtime) != sl.ERROR_CODE.SUCCESS or cam_R.grab(runtime) != sl.ERROR_CODE.SUCCESS:
                    continue

                # Retrieve RGB frames (LEFT view)
                cam_L.retrieve_image(img_L, sl.VIEW.LEFT)
                cam_R.retrieve_image(img_R, sl.VIEW.LEFT)
                rgba_L = img_L.get_data()
                rgba_R = img_R.get_data()
                rgb_L = cv2.cvtColor(rgba_L, cv2.COLOR_RGBA2RGB)
                rgb_R = cv2.cvtColor(rgba_R, cv2.COLOR_RGBA2RGB)

                # Save RGB frames as PNG
                rgb_L_png_path = os.path.join(frame_dir_L, f"{l_fid:05}.png")
                rgb_R_png_path = os.path.join(frame_dir_R, f"{r_fid:05}.png")
                cv2.imwrite(rgb_L_png_path, rgb_L)
                cv2.imwrite(rgb_R_png_path, rgb_R)

                # Retrieve depth data as float32 (meters) and save as .npy
                cam_L.retrieve_measure(depth_L, sl.MEASURE.DEPTH)
                cam_R.retrieve_measure(depth_R, sl.MEASURE.DEPTH)
                dep_L = depth_L.get_data()
                dep_R = depth_R.get_data()
                dep_L_npy_path = os.path.join(depth_npy_dir_L, f"{l_fid:05}.npy")
                dep_R_npy_path = os.path.join(depth_npy_dir_R, f"{r_fid:05}.npy")
                np.save(dep_L_npy_path, dep_L)
                np.save(dep_R_npy_path, dep_R)

                # Retrieve depth visualization as 8-bit RGB (for display)
                cam_L.retrieve_image(depth_L_png, sl.VIEW.DEPTH)
                cam_R.retrieve_image(depth_R_png, sl.VIEW.DEPTH)
                dep_L_rgba = depth_L_png.get_data()
                dep_R_rgba = depth_R_png.get_data()
                dep_L_png = cv2.cvtColor(dep_L_rgba, cv2.COLOR_RGBA2RGB)
                dep_R_png = cv2.cvtColor(dep_R_rgba, cv2.COLOR_RGBA2RGB)

                # Save depth PNG images
                dep_L_png_path = os.path.join(depth_png_dir_L, f"{l_fid:05}.png")
                dep_R_png_path = os.path.join(depth_png_dir_R, f"{r_fid:05}.png")
                cv2.imwrite(dep_L_png_path, dep_L_png)
                cv2.imwrite(dep_R_png_path, dep_R_png)

                # Create 2x2 combined frame (RGB top, depth bottom)
                top = np.hstack((rgb_L, rgb_R))
                bottom = np.hstack((dep_L_png, dep_R_png))
                combined = np.vstack((top, bottom))
                video_writer.write(combined)

                # Log timestamps and sensor data to CSV
                L_data = L_info.get(l_fid, {})
                R_data = R_info.get(r_fid, {})
                ts_L = L_data.get("timestamp", 0)
                ts_R = R_data.get("timestamp", 0)
                rel_time = ts_L - t0

                row = [
                    l_fid, r_fid, f"{ts_L:.6f}", f"{ts_R:.6f}", f"{rel_time:.6f}",
                    L_data.get("accel_x", 0), L_data.get("accel_y", 0), L_data.get("accel_z", 0),
                    L_data.get("gyro_x", 0), L_data.get("gyro_y", 0), L_data.get("gyro_z", 0),
                    R_data.get("accel_x", 0), R_data.get("accel_y", 0), R_data.get("accel_z", 0),
                    R_data.get("gyro_x", 0), R_data.get("gyro_y", 0), R_data.get("gyro_z", 0)
                ]
                writer.writerow(row)

                # Save pointcloud ply files
                cam_L.retrieve_measure(point_cloud_L, sl.MEASURE.XYZRGBA)
                cam_R.retrieve_measure(point_cloud_R, sl.MEASURE.XYZRGBA)
                pc_L_npy = point_cloud_L.get_data()
                pc_R_npy = point_cloud_R.get_data()
                pc_L_ply_path = os.path.join(pc_ply_dir_L, f"{l_fid:05}.ply")
                pc_R_ply_path = os.path.join(pc_ply_dir_R, f"{r_fid:05}.ply")
                save_point_cloud_ply(pc_L_ply_path, pc_L_npy)
                save_point_cloud_ply(pc_R_ply_path, pc_R_npy)



    cam_L.close()
    cam_R.close()
    video_writer.release()
    print(f"[✅] Done: {output_dir}")
    print(f"[📋] Saved matched timestamps CSV: {timestamp_csv_path}")

# Process all subfolders in a given relative directory (e.g., vegas/28-29)
def process_vegas(relative_input):
    input_root = "/mnt/ssd"
    full_input_folder = os.path.abspath(os.path.join(input_root, relative_input))
    desktop_out_base = os.path.expanduser("~/Desktop/ZEDX")
    print(f"[INFO] Scanning {full_input_folder}")

    for subfolder in sorted(os.listdir(full_input_folder)):
        subfolder_path = os.path.join(full_input_folder, subfolder)
        if not os.path.isdir(subfolder_path):
            continue

        # Check for required files
        csv_L = os.path.join(subfolder_path, "L_info.csv")
        csv_R = os.path.join(subfolder_path, "R_info.csv")
        svo_L = os.path.join(subfolder_path, "L.svo2")
        svo_R = os.path.join(subfolder_path, "R.svo2")

        if os.path.exists(csv_L) and os.path.exists(csv_R) and os.path.exists(svo_L) and os.path.exists(svo_R):
            pair_dict, matched_pairs = generate_frame_id_pairs(csv_L, csv_R, tolerance=0.001)
            output_dir = os.path.join(desktop_out_base, relative_input, subfolder)
            os.makedirs(output_dir, exist_ok=True)

            if len(matched_pairs) >= 2:
                timestamps_L = load_timestamps_csv(csv_L)
                first_ts = min(timestamps_L[l]['timestamp'] for l, r in matched_pairs)
                last_ts = max(timestamps_L[l]['timestamp'] for l, r in matched_pairs)
                duration = last_ts - first_ts
                saved_fps = (len(matched_pairs) - 1) / duration if duration > 0 else 0
                print(f"{saved_fps:.2f}")
            else:
                print("0.00")

            extract_and_combine(svo_L, svo_R, output_dir, matched_pairs, saved_fps)
        else:
            print(f"[⚠️] Skipping {subfolder_path}: Missing required files")

# Entry point for script
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python extract_svo2_avi.py vegas/28-29")
        exit(1)
    process_vegas(sys.argv[1])
