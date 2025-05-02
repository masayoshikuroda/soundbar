import sys
import asyncio
from bleak import BleakScanner, BleakClient
import soundbar

async def find_device(uuid):
    stop_event = asyncio.Event()

    def callback(device, advertising_data):
        stop_event.set()

    async with BleakScanner(detection_callback=callback, service_uuids=[uuid]) as scanner:
        await stop_event.wait()
        return scanner.discovered_devices[0].address
    
async def amain():
    address = await find_device(soundbar.UUID_SERVICE)
    async with BleakClient(address) as client:
        await soundbar.print_info(client)

if __name__ == "__main__":
    asyncio.run(amain())
