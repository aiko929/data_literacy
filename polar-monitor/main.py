import asyncio
import csv
import datetime
import os
from typing import Dict, List, Optional, Tuple, Any
from bleak import BleakClient, BleakScanner

# Standard UUIDs for the Heart Rate Service and Measurement Characteristic
HR_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HR_MEASUREMENT_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"


class HeartRateMonitor:
    def __init__(self):
        self.device_name_filter = "Polar"
        self.client: Optional[BleakClient] = None
        self.device_address: Optional[str] = None
        self.running = False
        self.data: Dict[str, List[Tuple[int, str]]] = {"heart": []}
        self.notification_callback = None
        self.debug_print = print  # Default to regular print

    async def scan_for_device(self) -> bool:
        """Scan for BLE devices matching the filter."""
        self.debug_print(f"Scanning for BLE devices with '{self.device_name_filter}' in name...")
        devices = await BleakScanner.discover()

        for device in devices:
            if device.name and self.device_name_filter in device.name:
                self.device_address = device.address
                self.debug_print(f"Found device: {device.name} [{device.address}]")
                return True

        self.debug_print(f"No {self.device_name_filter} device found. Make sure it's on and in range.")
        return False

    def handle_hr_notification(self, _: int, data: bytearray) -> None:
        """Handle incoming heart rate data."""
        # The first byte is a flag. If bit0==0, heart rate is uint8 at data[1].
        # If bit0==1, heart rate is uint16 at data[1:3].
        flags = data[0]
        if flags & 0x01 == 0:
            hr_value = data[1]
        else:
            hr_value = int.from_bytes(data[1:3], byteorder="little")

        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Store data
        self.data["heart"].append((hr_value, timestamp))

        # Call notification callback if set
        if self.notification_callback:
            self.notification_callback(hr_value, timestamp)

        self.debug_print(f"Heart Rate: {hr_value} at {timestamp}")

    async def connect_and_start(self) -> bool:
        """Connect to the device and start notifications."""
        if not self.device_address:
            return False

        try:
            self.client = BleakClient(self.device_address)
            await self.client.connect()

            if not self.client.is_connected:
                self.debug_print("Failed to connect.")
                return False

            self.debug_print("Connected. Starting notifications...")
            await self.client.start_notify(
                HR_MEASUREMENT_CHAR_UUID,
                self.handle_hr_notification
            )
            self.running = True
            return True

        except Exception as e:
            self.debug_print(f"Connection error: {e}")
            return False

    async def run(self) -> None:
        """Main loop for heart rate monitoring."""
        try:
            found = await self.scan_for_device()
            if not found:
                return

            connected = await self.connect_and_start()
            if not connected:
                return

            self.debug_print("Monitoring heart rate...")
            while self.running:
                await asyncio.sleep(1)

        except Exception as e:
            self.debug_print(f"Error during monitoring: {e}")
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop notifications and disconnect gracefully."""
        self.running = False

        if self.client and self.client.is_connected:
            self.debug_print("Stopping notifications...")
            try:
                await self.client.stop_notify(HR_MEASUREMENT_CHAR_UUID)
                await self.client.disconnect()
                self.debug_print("Disconnected from device.")
            except Exception as e:
                self.debug_print(f"Error during disconnect: {e}")

        # Save collected data
        if self.data["heart"]:
            self.save_to_csv()

    def save_to_csv(self, filename: str) -> None:
        """Save the collected heart rate data to a CSV file."""
        time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(f"csv/{time}", exist_ok=True)

        filename = f"csv/{time}/{filename}.csv"
        with open(filename, "w+") as file:
            writer = csv.writer(file)
            writer.writerow(["heartrate", "time"])

            for hr_value, timestamp in self.data["heart"]:
                writer.writerow([hr_value, timestamp])

        self.debug_print(f"Data saved to {filename}")