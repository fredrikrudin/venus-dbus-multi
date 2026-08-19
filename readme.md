# venus-dbus-multi (GUI Edition)

A universal Bluetooth LE multi-device driver tailored for **Venus OS** (Cerbo GX / Raspberry Pi). This driver continuously scans for encrypted *Instant Readout* BLE advertisement frames broadcast by Victron hardware, decodes the payloads asynchronously, and registers them directly onto the Venus OS D-Bus.

### Supported Devices Simultaneously:
- **Victron Phoenix Smart Inverter** (`com.victronenergy.inverter`)
- **Victron SmartShunt / BMV-Smart** (`com.victronenergy.battery`)
- **Victron SmartSolar MPPT (Up to 3 units)** (`com.victronenergy.solarcharger`)
- **Victron Orion-Tr Smart DC-DC** (`com.victronenergy.dcdc`)

---

## 🧠 Optimized for Raspberry Pi Zero 2 W
Victron hardware broadcasts Bluetooth beacons frequently (~3 times per second). Processing every packet and writing to the D-Bus continuously causes high CPU load, which can bottleneck a **Raspberry Pi Zero 2 W**. 

This driver implements a **Global Performance Throttling** feature. It continuously listens for radio waves but restricts D-Bus commits to a user-defined interval (e.g., once every 15 seconds). This slashes CPU cycle usage, keeping your system cool and highly responsive.

---

## 📡 Prerequisites
Before installing, you must fetch the unique Bluetooth MAC address and AES encryption key for each of your devices:
1. Open the **VictronConnect app** and connect to your device.
2. Go to **Settings (Gear icon)** -> **Product Info**.
3. Enable **Instant Readout via Bluetooth**.
4. Copy the **MAC Address** and the **Encryption Key** (Click *SHOW* next to the key).

---

## 🛠 Installation

Log into your Venus OS device via SSH as `root` and execute the following commands to download and deploy the driver package:

```bash
mkdir -p /data/apps
cd /data/apps
git clone https://github.com
cd venus-dbus-multi
chmod +x install.sh
./install.sh
```

### What the installer does:
1. Installs core OS packet extensions via `opkg`.
2. Downloads python dependencies (`bleak` and `victron-ble`) using `pip3`.
3. Sets up background management wrappers under `daemontools`.
4. Inject custom settings menus into the native Venus OS local display framework (`PageSettings.qml`).
5. Appends restore scripts into `/data/rc.local` so the driver **automatically re-installs and survives Venus OS firmware updates**.

---

## 📺 How to Configure (Zero Config Files!)
This version is fully GUI-driven. You never need to edit configuration files or `config.ini` templates over SSH.

1. Open your **Remote Console** (either locally, via HDMI, or over VRM Portal).
2. Navigate to **Settings** -> **BLE Devices**.
3. Select any hardware slot (e.g., *SmartSolar MPPT - Unit 1*), flip the **Enable Device** switch, and type in your **MAC Address** and **Encryption Key** using the virtual pop-up keyboard.
4. Go to **Global Polling & Performance** and set your target timing window (e.g., *15-30 seconds* is highly recommended for Pi Zero 2W).

Changes are processed immediately on the fly without needing to reboot your Venus OS environment. Your trådlösa units will pop up as native, separate appliances in the main Device List and start reporting metrics directly to the VRM Portal!

---

## 🤝 Contributing & Troubleshooting
If you encounter data collisions or missing frames, you can inspect the application runtime tracker frames using the following command inside your terminal session:
```bash
cat /var/log/victron-dbus-multidevice/current | tai64nlocal
```

Feel free to open an issue or submit a pull request if you want to expand support for more devices!
