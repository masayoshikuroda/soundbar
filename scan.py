import sys
import asyncio
from bleak import BleakScanner

TARGET = 'YAS-108_BLE'
if len(sys.argv) > 1:
  name = sys.argv[1]
else:
  name = TARGET

async def run():
    scanner = BleakScanner()
    await scanner.start()
    await asyncio.sleep(10.0)
    await scanner.stop()

    results = scanner.discovered_devices_and_advertisement_data
    for id in results:
        device = results[id][0]
        data   = results[id][1]
 
        if device.name == name:
            print("---", id, '---')
            print("LOCAL_NAME : ", data.local_name)
            print("RSSI       : ", data.rssi)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(run())
