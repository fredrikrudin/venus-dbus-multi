#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
import time
from bleak import BleakScanner
from victron_ble.devices import detect_device_type, Inverter, BatteryMonitor, SolarCharger, DcDcConverter
from victron_ble.exceptions import DecodingException

# Setup system logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("victron-dbus-multidevice")

# Link into the internal Venus OS libraries
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '/opt/victronenergy/dbus-modbus-client/ext/velib_python'))
try:
    from vedbus import VeDbusService
    from dbusmonitor import DbusMonitor 
except ImportError:
    logger.error("Could not find standard Venus OS velib_python paths. Exiting.")
    sys.exit(1)

class DbusBleMultiDevice:
    def __init__(self):
        self.devices_config = {}
        self.dbus_services = {}
        self.last_updates = {}
        self.dbus_monitor = None
        self.update_interval = 15.0

        # Mapping dictionary connecting the QML slots to standard Victron frameworks
        self.supported_types = {
            'Inverter':    {'type': 'INVERTER',   'instance': 29, 'prod_id': 0xA201, 'name': 'BLE Inverter'},
            'SmartShunt':  {'type': 'SMARTSHUNT', 'instance': 30, 'prod_id': 0xA389, 'name': 'BLE SmartShunt'},
            'SmartSolar1': {'type': 'SMARTSOLAR', 'instance': 31, 'prod_id': 0xA053, 'name': 'BLE SmartSolar 1'},
            'SmartSolar2': {'type': 'SMARTSOLAR', 'instance': 33, 'prod_id': 0xA053, 'name': 'BLE SmartSolar 2'},
            'SmartSolar3': {'type': 'SMARTSOLAR', 'instance': 34, 'prod_id': 0xA053, 'name': 'BLE SmartSolar 3'},
            'Orion':       {'type': 'ORION_DC_DC','instance': 32, 'prod_id': 0xA360, 'name': 'BLE Orion DC-DC'}
        }

    def init_dbus(self):
        settings_device = 'com.victronenergy.settings'
        watch_settings = {'/Settings/System/GlobalPollingInterval': {'code': None, 'whenToLog': 'onChanges'}}
        
        for dev_key in self.supported_types.keys():
            watch_settings[f'/Settings/BleDevice/{dev_key}/Enabled'] = {'code': None, 'whenToLog': 'onChanges'}
            watch_settings[f'/Settings/BleDevice/{dev_key}/MacAddress'] = {'code': None, 'whenToLog': 'onChanges'}
            watch_settings[f'/Settings/BleDevice/{dev_key}/EncryptionKey'] = {'code': None, 'whenToLog': 'onChanges'}

        self.dbus_monitor = DbusMonitor({settings_device: watch_settings}, valueChangedCallback=self._handle_setting_changed)

        try:
            import dbus
            bus = dbus.SystemBus()
            local_settings = bus.get_object(settings_device, '/Settings')
            local_settings.AddSetting('System', 'GlobalPollingInterval', 15.0, 1.0, 60.0, dbus_interface='com.victronenergy.Settings')
            
            for dev_key in self.supported_types.keys():
                local_settings.AddSetting('BleDevice/', f'{dev_key}/Enabled', 0, 0, 1, dbus_interface='com.victronenergy.Settings')
                local_settings.AddSetting('BleDevice/', f'{dev_key}/MacAddress', "", 0, 0, dbus_interface='com.victronenergy.Settings')
                local_settings.AddSetting('BleDevice/', f'{dev_key}/EncryptionKey', "", 0, 0, dbus_interface='com.victronenergy.Settings')
        except Exception as e:
            logger.debug(f"Settings paths initialized: {e}")

        self.reload_configuration_from_gui()

    def reload_configuration_from_gui(self):
        settings_device = 'com.victronenergy.settings'
        val = self.dbus_monitor.get_value(settings_device, '/Settings/System/GlobalPollingInterval')
        if val is not None:
            self.update_interval = float(val)

        new_config = {}
        for dev_key, dev_static in self.supported_types.items():
            enabled = self.dbus_monitor.get_value(settings_device, f'/Settings/BleDevice/{dev_key}/Enabled') == 1
            mac = str(self.dbus_monitor.get_value(settings_device, f'/Settings/BleDevice/{dev_key}/MacAddress')).strip().lower()
            key = str(self.dbus_monitor.get_value(settings_device, f'/Settings/BleDevice/{dev_key}/EncryptionKey')).strip()

            if enabled and len(mac) == 17 and len(key) >= 32:
                new_config[mac] = {
                    'type': dev_static['type'],
                    'key': key,
                    'name': dev_static['name'],
                    'instance': dev_static['instance'],
                    'prod_id': dev_static['prod_id']
                }
                if mac not in self.last_updates:
                    self.last_updates[mac] = 0

        for mac, dev_info in new_config.items():
            if mac not in self.dbus_services:
                self._register_new_dbus_service(mac, dev_info)

        self.devices_config = new_config

    def _register_new_dbus_service(self, mac, dev_info):
        clean_mac = mac.replace(":", "")
        dev_type = dev_info['type']
        
        if dev_type == 'INVERTER':
            service_name = f'com.victronenergy.inverter.ble_{clean_mac}'
            paths = ['/State', '/Ac/Out/L1/V', '/Ac/Out/L1/I', '/Ac/Out/L1/P', '/Dc/0/Voltage']
        elif dev_type == 'SMARTSHUNT':
            service_name = f'com.victronenergy.battery.ble_{clean_mac}'
            paths = ['/Dc/0/Voltage', '/Dc/0/Current', '/Dc/0/Power', '/Soc', '/ConsumedAmphours', '/TimeToGo']
        elif dev_type == 'SMARTSOLAR':
            service_name = f'com.victronenergy.solarcharger.ble_{clean_mac}'
            paths = ['/State', '/Dc/0/Voltage', '/Dc/0/Current', '/Yield/Power', '/Pv/V']
        elif dev_type == 'ORION_DC_DC':
            service_name = f'com.victronenergy.dcdc.ble_{clean_mac}'
            paths = ['/State', '/Dc/0/Voltage', '/Dc/1/Voltage']
        else:
            return

        service = VeDbusService(service_name)
        service.add_path('/Mgmt/ProcessName', __file__)
        service.add_path('/Mgmt/ProcessVersion', '3.5.0')
        service.add_path('/Mgmt/Connection', 'Bluetooth LE Instant Readout')
        service.add_path('/DeviceInstance', dev_info['instance']) 
        service.add_path('/ProductId', dev_info['prod_id'])  
        service.add_path('/ProductName', dev_info['name'])
        service.add_path('/Connected', 1)

        for path in paths:
            service.add_path(path, 0.0 if 'Voltage' in path or 'Current' in path or 'Power' in path or 'Soc' in path else 0)

        self.dbus_services[mac] = service
        logger.info(f"Registered and mapped device: {service_name}")

    def _handle_setting_changed(self, service, path, changes):
        self.reload_configuration_from_gui()

    def update_device_dbus(self, mac, data):
        current_time = time.time()
        if current_time - self.last_updates.get(mac, 0) < self.update_interval:
            return 

        try:
            service = self.dbus_services[mac]
            dev_type = self.devices_config[mac]['type']

            if dev_type == 'INVERTER':
                ac_voltage = data.get_ac_voltage()
                ac_power = data.get_ac_apparent_power()
                service['/Ac/Out/L1/V'] = ac_voltage
                service['/Ac/Out/L1/P'] = ac_power
                service['/Ac/Out/L1/I'] = round(ac_power / ac_voltage, 2) if ac_voltage > 0 else 0.0
                service['/Dc/0/Voltage'] = data.get_battery_voltage()
                service['/State'] = int(data.get_state())
            
            elif dev_type == 'SMARTSHUNT':
                service['/Dc/0/Voltage'] = data.get_voltage()
                service['/Dc/0/Current'] = data.get_current()
                service['/Dc/0/Power'] = round(data.get_voltage() * data.get_current(), 1)
                service['/Soc'] = data.get_soc()
                service['/ConsumedAmphours'] = data.get_consumed_amphours()
                service['/TimeToGo'] = data.get_remaining_time() * 60 if data.get_remaining_time() else 0

            elif dev_type == 'SMARTSOLAR':
                service['/Dc/0/Voltage'] = data.get_battery_voltage()
                service['/Dc/0/Current'] = data.get_charge_current()
                service['/Yield/Power'] = data.get_solar_power()
                service['/Pv/V'] = data.get_pv_voltage()
                service['/State'] = int(data.get_charge_state())

            elif dev_type == 'ORION_DC_DC':
                service['/Dc/0/Voltage'] = data.get_input_voltage()
                service['/Dc/1/Voltage'] = data.get_output_voltage()
                service['/State'] = int(data.get_device_state())

            self.last_updates[mac] = current_time

        except Exception as e:
            logger.error(f"Error transferring data frame for {mac}: {e}")

    def ble_detection_callback(self, device, advertisement_data):
        mac = device.address.lower()
        if mac in self.devices_config:
            try:
                m_data = advertisement_data.manufacturer_data
                if 0x0241 in m_data: 
                    raw_payload = m_data[0x0241]
                    parsed_device = detect_device_type(raw_payload)
                    
                    if parsed_device:
                        dev_info = self.devices_config[mac]
                        decrypted_data = parsed_device.decrypt(raw_payload, dev_info['key'])
                        self.update_device_dbus(mac, decrypted_data)
            except DecodingException:
                pass 
            except Exception as e:
                logger.error(f"Error handling scan callback for {mac}: {e}")

    async def main(self):
        self.init_dbus()
        logger.info("Asynchronous BLE scanner engine activated.")
        scanner = BleakScanner(detection_callback=self.ble_detection_callback)
        await scanner.start()
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    service = DbusBleMultiDevice()
    try:
        asyncio.run(service.main())
    except KeyboardInterrupt:
        sys.exit(0)
