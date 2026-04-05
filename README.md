# AirSpace

> **Work in progress.** Expect breaking changes.

A P2P mesh sync daemon for [SnapperOS](https://github.com/PatrickIndran), built on top of [Yggdrasil](https://yggdrasil-network.github.io/). AirSpace runs as a background daemon (`airspaced`) and i[...]  

<img width="1080" height="1080" alt="ddd" src="https://github.com/user-attachments/assets/f63c4b7f-e78e-4345-af3f-652361c8d172" /> | width=100)


## What it does right now

- Daemon + CLI IPC over Unix sockets
- Device management via `devices.yaml`
- File sync over Yggdrasil using rsync over SSH
- File transfer over Yggdrasil using rsync over SSH
- GUI Client for AirSpace.

## Planned

- Clipboard sync
- Calendar sync

## Transparency  
- I am new to python so some of the code might be "shit".
- This readme has been made by Claude.

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).
