import sys
import asyncio
import xml.etree.ElementTree as ET
from bleak import BleakScanner, BleakClient
import soundbar, scan

async def assert_service(node):
    description = node.attrib.get("description")
    print(f"Child element: {node.tag} description: {description}")
    service_uuid = node.attrib.get("uuid")
    print(f"\tuuid: {service_uuid}")

    address = await scan.find_device(service_uuid)
    print(f"\taddress: {address}")

    client = BleakClient(address)
    await client.connect()
    
    service = client.services.get_service(service_uuid)
    for child in node:
        if child.tag == "assert-characteristic":
            assert_characteristic(child, service)
        else:
            raise ValueError(f"Child element: {child.tag}")
    print()

    return client

def assert_characteristic(node, service):
    description = node.attrib.get("description")
    print(f"\tChild element: {node.tag} description: {description}")
    char_uuid = node.attrib.get("uuid")
    print(f"\t\tuuid: {char_uuid}")

    characteristic = service.get_characteristic(char_uuid)
    for child in node:
        if child.tag == "property":
            assert_property(child)
        elif child.tag == "assert-cccd":
            print(f"\t\tChild element: {child.tag}")
        else:
            raise ValueError(f"Child element: {child.tag}")

def assert_property(node):
    name = node.attrib.get("name")
    print(f"\t\tChild element: {node.tag} name: {name}")

def node_base(node):
    description = node.attrib.get("description")
    print(f"Child element: {node.tag}  description: {description}")
    service_uuid = node.attrib.get("service-uuid")
    print(f"\tservice-uuid: {service_uuid}")
    char_uuid = node.attrib.get("characteristic-uuid")
    print(f"\tcharacteristic-uuid: {char_uuid}")
    return service_uuid, char_uuid

async def write_descriptor(node, client):
    s_uuid, c_uuid = node_base(node)
    uuid = node.attrib.get("uuid")
    print(f"\tuuid: {uuid}")
    descriptor = client.services.get_service(s_uuid).get_characteristic(c_uuid).get_descriptor(uuid)
    value = node.attrib.get("value")
    print(f"\tvalue: {value}")
    #await client.write_gatt_descriptor(descriptor.handle, bytes.fromhex(value))
    await client.start_notify(c_uuid, soundbar.on_notify)
    print()

async def write(node, client):
    s_uuid, c_uuid = node_base(node)
    char = client.services.get_service(s_uuid).get_characteristic(c_uuid)
    value = node.attrib.get("value")
    print(f"\tvalue: {value}")
    type = node.attrib.get("type")
    print(f"\ttype: {type}")
    response = True if type == "WRITE_REQUEST" else False
    await client.write_gatt_char(char.handle, bytes.fromhex(value), response)
    print()

async def wait_for_notification(node, client):
    s_uuid, c_uuid = node_base(node)
    timeout = node.attrib.get("timeout")
    print(f"\timeout: {timeout}")
    print()

    await asyncio.sleep(max(1, int(timeout)/1000))

async def amain(macro_path):
    tree = ET.parse(macro_path)

    # XMLのルート要素を取得
    root = tree.getroot()
    if (root.tag != "macro"):
        raise ValueError(f"Invalid root element: {root.tag}")
    print(f"Root element: {root.tag}")
    print(f"\tname: {root.attrib['name']}")
    print(f"\ticon: {root.attrib['icon']}")
    print()

    # 子要素を表示
    for child in root:
        if child.tag == "assert-service":
            client = await assert_service(child)
        elif child.tag == "write-descriptor":
            await write_descriptor(child, client)
        elif child.tag == "write":
            await write(child, client)
        elif child.tag == "wait-for-notification":
            await wait_for_notification(child, client)
        else:
            raise ValueError(f"Child element: {child.tag}")
    await client.disconnect()
    print("Disconnected")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        macro_path = sys.argv[1]
    else:
        macro_path = "macro/surround-movie.xml"

    asyncio.run(amain(macro_path))






