#!/bin/bash
set -e

APP_DIR="/data/apps/victron-dbus-multidevice"
SERVICE_DIR="/service/victron-dbus-multidevice"

echo "=== Starting installation of victron-dbus-multidevice ==="

# 1. Clean up legacy folder symlinks if they exist from older script variants
if [ -L "/service/dbus-ble-inverter" ]; then
    echo "Cleaning up older service references..."
    rm -f "/service/dbus-ble-inverter"
fi

# 2. Install standard system dependencies and python extensions
echo "Updating packet mirrors and fetching python frameworks..."
opkg update
opkg install python3-pip python3-misc
pip3 install async-timeout bleak victron-ble

# 3. Establish targeted deployment directory layouts
mkdir -p "$APP_DIR/qml"
mkdir -p "$APP_DIR/service"

# 4. Copy working runtime codebase into persistent memory directories
echo "Deploying application tree..."
cp victron-dbus-multidevice.py "$APP_DIR/"
cp qml/page-settings-polling.qml "$APP_DIR/qml/"
cp service/run "$APP_DIR/service/"

# Apply execution bit permissions onto core runtime targets
chmod +x "$APP_DIR/victron-dbus-multidevice.py"
chmod +x "$APP_DIR/service/run"

# 5. Inject custom settings submenu view frames directly into Venus OS core QML
GUI_PAGE_SETTINGS="/opt/victronenergy/gui/qml/PageSettings.qml"
if [ -f "$GUI_PAGE_SETTINGS" ]; then
    if ! grep -q "page-settings-polling.qml" "$GUI_PAGE_SETTINGS"; then
        echo "Injecting BLE Devices interface section into Venus OS System Settings..."
        sed -i '/^}/i \    MbSubMenu {\n        description: qsTr("BLE Devices")\n        subpage: Component { Page { title: qsTr("BLE Config"); source: "'"$APP_DIR"'/qml/page-settings-polling.qml" } }\n    }' "$GUI_PAGE_SETTINGS"
    fi
fi

# 6. Bind runtime configuration paths under active daemontools monitoring loops
echo "Binding active system background process link..."
if [ ! -L "$SERVICE_DIR" ]; then
    ln -s "$APP_DIR/service" "$SERVICE_DIR"
fi

# 7. Secure boot persistence across future system firmware updates via rc.local
touch /data/rc.local
chmod +x /data/rc.local
if ! grep -q "$APP_DIR/install.sh" /data/rc.local; then
    echo -e "\n# Re-install and patch BLE driver following an OS firmware upgrade\ncd $APP_DIR && ./install.sh" >> /data/rc.local
fi

# 8. Force restart GUI core to load and render the new QML views instantly
echo "Re-indexing Venus OS GUI engine..."
svc -t /service/gui
svc -t "$SERVICE_DIR" || echo "Background engine spin-up initialized."

echo "=== INSTALLATION COMPLETE! ==="
echo "Navigate to: Remote Console -> Settings -> 'BLE Devices' to set up your hardware."
