import subprocess
import socket
import json
import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio

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
        return json.loads(response_raw)
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        client.close()

# ---------------- Window and ADW stuff ----------------
Adw.init()

class AirFerWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.selected_file = None
        try:
            self.builder.add_from_file("window.ui")
        except Exception as e:
            print(f"Error loading UI: {e}")
            return

        # FIXED INDENTATION: Everything below is now properly inside __init__
        self.window = self.builder.get_object("main_window")
        self.toast_overlay = self.builder.get_object("toast_overlay")
        self.sync_button = self.builder.get_object("sync_button")
        self.select_button = self.builder.get_object("select_button")
        self.dialog = self.builder.get_object("airfer_dialog")
        self.device_list = self.builder.get_object("device_list")

        self.sync_button.connect("clicked", self.on_sync_button_clicked)
        self.select_button.connect("clicked", self.on_select_file_clicked)
        self.device_list.connect("row-activated", self.on_device_row_activated)

    # --- AirSync ---
    # Tells the daemon to sync the AirSync folder.
    def on_sync_button_clicked(self, button):
        print("Syncing AirSync Folder...")
        send_task({"action": "sync"})
        toast = Adw.Toast.new("Syncing with AirSync folder...")
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

    # ---------------- AirFer ----------------
    # Shares a sellected file to the sellected device.
    def on_select_file_clicked(self, button):
        print("Opening file selector...")

        def on_selected(file_dialog, result):
            try:
                file = file_dialog.open_finish(result)
                self.selected_file = file.get_path()
                print(f"Selected file: {self.selected_file}")
                # Populate the list fresh each time the dialog opens
                self.populate_device_list()
                self.dialog.present(self.window)
            except Exception as e:
                print(f"Cancelled or failed: {e}")

        file_dialog = Gtk.FileDialog()
        file_dialog.open(self.window, None, on_selected)

    def show(self):
        self.window.present()


    # --- Populate device list --- # Hell it self
    # Clears the row and repopulates it with the latest devices from the backend.
    # Or just hell it self, i put a lot of time in this function.
    def populate_device_list(self):

        while True:
            row = self.device_list.get_first_child()
            if row is None:
                break
            self.device_list.remove(row)

        devices = send_task({"action": "list"})
        if not devices:
            row = Adw.ActionRow()
            row.set_title("No devices found :(")
            row.set_sensitive(False)
            self.device_list.append(row)
            return

        for device in devices:
            row = Adw.ActionRow()
            row.set_title(device.get("name", "Unknown"))
            row.set_subtitle(f"{device.get('username', '')}  •  {device.get('ip_address', '')}")
            row.set_activatable(True)

            row.device_data = device

            arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
            row.add_suffix(arrow)
            self.device_list.append(row)

    # --- Row sellected ---
    # Transfer sellected file to the really cool sellected device!
    def on_device_row_activated(self, listbox, row):
        device = getattr(row, "device_data", None)
        if device and self.selected_file:
            print(f"Transferring {self.selected_file} to {device['name']}...")
            send_task({
                "action": "transfer",
                "device": device["name"],
                "path": self.selected_file
            })
            self.dialog.close()

            toast = Adw.Toast.new("Transferring File...")
            toast.set_timeout(3)
            self.toast_overlay.add_toast(toast)


# ---------------- Main ----------------
if __name__ == "__main__":
    app = Adw.Application(application_id="com.externalfoundation.AirFer")

    def on_activate(app):
        win = AirFerWindow()
        app.add_window(win.window)
        win.show()

    app.connect("activate", on_activate)
    app.run(None)

# This was a fun project to make! Also really stressful ngl, but i learned a lot about Blueprint and sockets.
