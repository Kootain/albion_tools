# Albion Sniffer

A standalone network sniffer for Albion Online, written in Go. It captures game traffic and forwards it to local or remote consumers.

## Features

- **Efficient Packet Capture**: Uses `gopacket/pcap` (Npcap) for high-performance sniffing.
- **Auto-Device Locking**: Automatically detects the network interface carrying game traffic and locks onto it.
- **UDP Forwarding**: Forwards captured payloads to configured targets (e.g., Python analyzer).
- **System Tray Integration**: Minimized UI with status icons and device info.
- **Embedded Resources**: Config and icons are embedded in the binary for single-file deployment.

## Build

To build the application without a console window (background mode):

```powershell
go build -ldflags "-H=windowsgui" -o sniffer.exe main.go
```

To build with a console window (for debugging):

```powershell
go build -o sniffer.exe main.go
```

## Usage

1.  Run `sniffer.exe`.
2.  The application will appear in the system tray.
3.  It will automatically scan interfaces and lock onto the one with game traffic.
4.  Captured packets are forwarded to `127.0.0.1:44444` (default).

## Requirements

- **Npcap**: Must be installed on the Windows machine (install with "WinPcap API-compatible Mode" if needed, though usually not required for modern gopacket).
