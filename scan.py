import asyncio
from bleak import BleakScanner

async def run():
    scanner = BleakScanner()
    await scanner.start()
    await asyncio.sleep(10.0)
    await scanner.stop()

    for d in scanner.discovered_devices:
        if d.name == "YAS-108_BLE":
            print("NAME    : ", d.name)
            print("ADDRESS : ", d.address)
            print("RSSI    : ", d.rssi)
            print("DETAILS : ", d.details)
            print("METADATA: ")
            for k in d.metadata:
                print("    ", k, d.metadata[k])
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
