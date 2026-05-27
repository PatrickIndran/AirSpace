import json
import subprocess
import os
import socket
import logging


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("airspaced")


socket_path = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "airspace.sock")



if os.path.exists(socket_path):
    os.remove(socket_path)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(socket_path)
server.listen(1)

log.info(f"daemon started on {socket_path}")


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
            conn.sendall(b"error: unknown action.")

    except Exception as e:
        log.exception(f"error: {e}")
    finally:
        conn.close()
