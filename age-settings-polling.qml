import QtQuick 1.1
import com.victron.velib 1.0

Page {
    id: root
    title: qsTr("System - BLE Device Configuration")

    // ==========================================
    // INVERTER
    // ==========================================
    MbSubMenu {
        description: qsTr("Inverter")
        subpage: Component {
            Page {
                title: qsTr("Configure Inverter")
                MbSwitch {
                    bind: "com.victronenergy.settings/Settings/BleDevice/Inverter/Enabled"
                    name: qsTr("Enable Device")
                }
                MbItemText {
                    description: qsTr("MAC Address")
                    bind: "com.victronenergy.settings/Settings/BleDevice/Inverter/MacAddress"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "AA:BB:CC:DD:EE:FF"
                }
                MbItemText {
                    description: qsTr("Encryption Key (AES)")
                    bind: "com.victronenergy.settings/Settings/BleDevice/Inverter/EncryptionKey"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "32-character hex key"
                }
            }
        }
    }

    // ==========================================
    // SMARTSHUNT / BATTERY
    // ==========================================
    MbSubMenu {
        description: qsTr("SmartShunt / Battery")
        subpage: Component {
            Page {
                title: qsTr("Configure SmartShunt")
                MbSwitch {
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartShunt/Enabled"
                    name: qsTr("Enable Device")
                }
                MbItemText {
                    description: qsTr("MAC Address")
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartShunt/MacAddress"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "AA:BB:CC:DD:EE:FF"
                }
                MbItemText {
                    description: qsTr("Encryption Key (AES)")
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartShunt/EncryptionKey"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "32-character hex key"
                }
            }
        }
    }

    // ==========================================
    // SMARTSOLAR MPPT - UNIT 1
    // ==========================================
    MbSubMenu {
        description: qsTr("SmartSolar MPPT - Unit 1")
        subpage: Component {
            Page {
                title: qsTr("Configure SmartSolar 1")
                MbSwitch {
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar1/Enabled"
                    name: qsTr("Enable Device")
                }
                MbItemText {
                    description: qsTr("MAC Address")
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar1/MacAddress"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "AA:BB:CC:DD:EE:FF"
                }
                MbItemText {
                    description: qsTr("Encryption Key (AES)")
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar1/EncryptionKey"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "32-character hex key"
                }
            }
        }
    }

    // ==========================================
    // SMARTSOLAR MPPT - UNIT 2
    // ==========================================
    MbSubMenu {
        description: qsTr("SmartSolar MPPT - Unit 2")
        subpage: Component {
            Page {
                title: qsTr("Configure SmartSolar 2")
                MbSwitch {
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar2/Enabled"
                    name: qsTr("Enable Device")
                }
                MbItemText {
                    description: qsTr("MAC Address")
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar2/MacAddress"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "AA:BB:CC:DD:EE:FF"
                }
                MbItemText {
                    description: qsTr("Encryption Key (AES)")
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar2/EncryptionKey"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "32-character hex key"
                }
            }
        }
    }

    // ==========================================
    // SMARTSOLAR MPPT - UNIT 3
    // ==========================================
    MbSubMenu {
        description: qsTr("SmartSolar MPPT - Unit 3")
        subpage: Component {
            Page {
                title: qsTr("Configure SmartSolar 3")
                MbSwitch {
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar3/Enabled"
                    name: qsTr("Enable Device")
                }
                MbItemText {
                    description: qsTr("MAC Address")
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar3/MacAddress"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "AA:BB:CC:DD:EE:FF"
                }
                MbItemText {
                    description: qsTr("Encryption Key (AES)")
                    bind: "com.victronenergy.settings/Settings/BleDevice/SmartSolar3/EncryptionKey"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "32-character hex key"
                }
            }
        }
    }

    // ==========================================
    // ORION DC-DC
    // ==========================================
    MbSubMenu {
        description: qsTr("Orion-Tr Smart DC-DC")
        subpage: Component {
            Page {
                title: qsTr("Configure Orion DC-DC")
                MbSwitch {
                    bind: "com.victronenergy.settings/Settings/BleDevice/Orion/Enabled"
                    name: qsTr("Enable Device")
                }
                MbItemText {
                    description: qsTr("MAC Address")
                    bind: "com.victronenergy.settings/Settings/BleDevice/Orion/MacAddress"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "AA:BB:CC:DD:EE:FF"
                }
                MbItemText {
                    description: qsTr("Encryption Key (AES)")
                    bind: "com.victronenergy.settings/Settings/BleDevice/Orion/EncryptionKey"
                    writeAccessLevel: User.AccessUser
                    placeholderText: "32-character hex key"
                }
            }
        }
    }

    // ==========================================
    // GLOBAL PERFORMANCE THROTTLING
    // ==========================================
    MbSubMenu {
        description: qsTr("Global Polling & Performance")
        subpage: Component {
            Page {
                title: qsTr("System Performance")
                MbSpinBox {
                    description: qsTr("Global Update Interval")
                    bind: "com.victronenergy.settings/Settings/System/GlobalPollingInterval"
                    numOfDecimals: 0
                    unit: " seconds"
                    min: 1     
                    max: 60    
                    stepSize: 1 
                }
                MbItem {
                    description: "Hardware Note"
                    value: "Optimized for RPi Zero 2W (15s recommended)."
                    writeAccessLevel: User.AccessUser
                }
            }
        }
    }
}
