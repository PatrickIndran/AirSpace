import socket
import json
import os
import argparse
from rich.table import Table
from rich import box, print

# ---------------- Config ----------------

socket_path = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "airspace.sock")

# ---------------- Socket ----------------

def send_task(task_dict):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(socket_path)
        message = json.dumps(task_dict).encode('utf-8')
        client.sendall(message)

        response_raw = client.recv(4096).decode('utf-8')

        if not response_raw:
            print("[bold red]No response from daemon.[/bold red]")
            return

        if task_dict.get("action") == "list":
            try:
                devices = json.loads(response_raw)
                table = Table(box=box.SQUARE, title="AirSpace Trusted Devices")
                table.add_column("Device Name", style="cyan")
                table.add_column("User", style="magenta")
                table.add_column("IP Address", style="green")
                for d in devices:
                    table.add_row(d["name"], d["username"], d["ip_address"])
                print(table)
            except json.JSONDecodeError:
                print(f"Raw response: {response_raw}")
        else:
            print(f"[bold green]Daemon:[/bold green] {response_raw}")

    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
    finally:
        client.close()

# ---------------- Args ----------------

parser = argparse.ArgumentParser(description="AirSpaceCTL — control the AirSpace daemon")
parser.add_argument("-s", "--sync", dest="sync", action="store_true", help="Sync the AirSync folder to all devices")
parser.add_argument("-l", "--list", action="store_true", help="List trusted devices")
parser.add_argument("-cp", "--copy", dest="copy_path", help="Path of file to transfer")
parser.add_argument("-d", "--device", dest="target_device", help="Target device name")
args = parser.parse_args()

# ---------------- Actions ----------------

# --- Sync ---
if args.sync:
    send_task({"action": "sync"})

# --- Transfer ---
elif args.copy_path or args.target_device:
    if not args.copy_path:
        print("[bold red]Error:[/bold red] -cp requires a file path. Use -cp <path> -d <device>")
    elif not args.target_device:
        print("[bold red]Error:[/bold red] -d requires a device name. Use -cp <path> -d <device>")
    else:
        send_task({
            "action": "transfer",
            "device": args.target_device,
            "path": args.copy_path
        })

# --- List ---
elif args.list:
    send_task({"action": "list"})
