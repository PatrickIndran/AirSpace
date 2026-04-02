import json
import subprocess
import os
import yaml
import socket
import logging
from passlib.apache import HtpasswdFile

# ---------------- Logging ----------------

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("airspaced")

# ---------------- Config ----------------

socket_path = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "airspace.sock")

config_path = os.path.join(os.path.dirname(__file__), "devices.yaml")
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# ---------------- Actions ----------------

# --- Sync --- #
def airspace_sync(config, conn):
    local_folder = os.path.expanduser("~/Documents/AirSpace/AirSync")
    remote_destination = "~/Documents/AirSpace/"
    for device in config["devices"]:
        target = f"{device['username']}@[{device['ip_address']}]:{remote_destination}"
        subprocess.run(["rsync", "--archive", "--rsh", "ssh", local_folder, target], capture_output=True, text=True)
    conn.sendall(b"Sync complete.")

# --- Transfer --- #
def airspace_transfer(config, conn, task):
    path = os.path.expanduser(task["path"])
    d = next((d for d in config["devices"] if d["name"] == task["device"]), None)
    if not d:
        conn.sendall(b"Error: device not found.")
        return
    target = f"{d['username']}@[{d['ip_address']}]:~/Downloads/"
    subprocess.run(["rsync", "-a", "-e", "ssh", path, target], capture_output=True, text=True)
    conn.sendall(b"Transfer complete.")

# --- List --- #
def airspace_list(config, conn):
    conn.sendall(json.dumps(config.get("devices", [])).encode('utf-8'))

# ---------------- Services --------------

# --- Radicale ---
def airspace_radicale():
    config_dir = os.path.expanduser("~/.config/AirSpace")
    htpasswd_file = os.path.join(config_dir, "users.htpasswd")
    collections_dir = os.path.expanduser("~/Documents/AirSpace/AirSync/.data/radicale/calander")

    # 2. Ensure directories exist
    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(collections_dir, exist_ok=True)

    print("Setting up Radicale credentials...")
    try:
        subprocess.run([
            "htpasswd", "-B", "-b", "-c", htpasswd_file, "airspace", "airspace"
        ], check=True)
        print(f"✅ Credentials set: {htpasswd_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating htpasswd: {e}")
        return

    # 4. Define the command to start the server
    cmd = [
        "python3", "-m", "radicale",
        "--config", "",
        "--server-hosts", "127.0.0.1:5232",
        "--storage-filesystem-folder", collections_dir,
        "--auth-type", "htpasswd",
        "--auth-htpasswd-filename", htpasswd_file,
        "--auth-htpasswd-encryption", "bcrypt",
        "--rights-type", "owner_only",
        "--logging-level", "info"
    ]
    subprocess.run(cmd)

# Call the function
airspace_radicale()
# ---------------- Socket ----------------

if os.path.exists(socket_path):
    os.remove(socket_path)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(socket_path)
server.listen(1)

log.info(f"Daemon started on {socket_path}")

# ---------------- Main Loop ----------------

while True:
    conn, addr = server.accept()
    try:
        raw_data = conn.recv(4096).decode('utf-8')
        if not raw_data:
            continue

        task = json.loads(raw_data)
        action = task.get("action")

        if action == "sync":
            airspace_sync(config, conn)
        elif action == "transfer":
            airspace_transfer(config, conn, task)
        elif action == "list":
            airspace_list(config, conn)
        else:
            conn.sendall(b"Error: unknown action.")

    except Exception as e:
        log.exception(f"Error: {e}")
    finally:
        conn.close()
