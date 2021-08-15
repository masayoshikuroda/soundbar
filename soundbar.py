#!/usr/bin/env python3
#coding=utf-8
import asyncio
import json
from argparse import ArgumentParser
from bleak import BleakClient

BT_ADDRESS            = "62BC9137-F6CC-42EF-ABF3-F3D8AA2E6DC8"

UUID_MODEL_NUMBER     = "00002a24-0000-1000-8000-00805f9b34fb"
UUID_DEVICE_NAME      = "00002a00-0000-1000-8000-00805f9b34fb"
UUID_MANUFACTURE_NAME = "00002a29-0000-1000-8000-00805f9b34fb"

UUID_NOTIFY           = "5cafe9de-e7b0-4e0b-8fb9-2da91a7ae3ed"
UUID_WRITE            = "0c50e7fa-594c-408b-ae0d-b53b884b7c08"

WRITE_BASE = 'ccaa '

WRITE_REQUEST_NOTIFY = WRITE_BASE + '0901 4854 5320 436f 6e74 53'

WRITE_CMD_BASE                  = WRITE_BASE + '0340 '

WRITE_CMD_INPUT_HDMI            = WRITE_CMD_BASE + '784a fb'
WRITE_CMD_INPUT_BLUETOOTH       = WRITE_CMD_BASE + '7829 1c'
WRITE_CMD_INPUT_TV              = WRITE_CMD_BASE + '78df 66'
WRITE_CMD_INPUT_ANALOG          = WRITE_CMD_BASE + '78d1 74'

WRITE_CMD_SURROUND_MOVIE        = WRITE_CMD_BASE + '78d9 6c'
WRITE_CMD_SURROUND_STEREO       = WRITE_CMD_BASE + '7850 f5'
WRITE_CMD_SURROUND_TV           = WRITE_CMD_BASE + '7ef1 4e'
WRITE_CMD_SURROUND_SPORTS       = WRITE_CMD_BASE + '78db 6a'
WRITE_CMD_SURROUND_GAME         = WRITE_CMD_BASE + '78dc 69'
WRITE_CMD_SURROUND_MUSIC        = WRITE_CMD_BASE + '78da 6b'

WRITE_CMD_SOUND_3D_ON           = WRITE_CMD_BASE + '78c9 7c'
WRITE_CMD_SOUND_3D_OFF          = WRITE_CMD_BASE + '78b4 91'
WRITE_CMD_SOUND_CLEAR_VOICE_ON  = WRITE_CMD_BASE + '7e80 bf'
WRITE_CMD_SOUND_CLEAR_VOICE_OFF = WRITE_CMD_BASE + '7e82 bd'
WRITE_CMD_SOUND_BASS_EXT_ON     = WRITE_CMD_BASE + '786e d7'
WRITE_CMD_SOUND_BASS_EXT_OFF    = WRITE_CMD_BASE + '786f d6'

WRITE_CMD_SOUND_SUBWOOFER_UP    = WRITE_CMD_BASE + '784c f9'
WRITE_CMD_SOUND_SUBWOOFER_DOWN  = WRITE_CMD_BASE + '784d f8'

WRITE_CMD_VOLUME_UP             = WRITE_CMD_BASE + '781e 27'
WRITE_CMD_VOLUME_DOWN           = WRITE_CMD_BASE + '781f 26'

WRITE_CMD_MUTE_OFF              = WRITE_CMD_BASE + '7ea3 9c'
WRITE_CMD_MUTE_ON               = WRITE_CMD_BASE + '7ea2 9d'

argparser =  ArgumentParser(description='Connect Sound Bar via bluetooth and send commad.')
argparser.add_argument('address', help='Bluetooth device address')
argparser.add_argument('--input',       choices=['hdmi', 'bt', 'tv', 'analog'])
argparser.add_argument('--surround',    choices=['tv', 'stereo', 'movie', 'music', 'sports', 'game'])
argparser.add_argument('--sound_3d',    choices=['on', 'off'])
argparser.add_argument('--clear_voice', choices=['on', 'off'])
argparser.add_argument('--bass_ext',    choices=['on', 'off'])
argparser.add_argument('--volume',      choices=['up', 'down'])
argparser.add_argument('--subwoofer',   choices=['up', 'down'])
argparser.add_argument('--mute',        choices=['on', 'off'])

args = argparser.parse_args()

def get_surround(code):
    if code == 0x000a:
        return 'TV'
    elif code == 0x0100:
        return 'STEREO'
    elif code == 0x0003:
        return 'MOVIE'
    elif code == 0x0008:
        return 'MUSIC'
    elif code == 0x0009:
        return 'SPORTS'
    elif code == 0x000c:
        return 'GAME'

def is_sound_3d(code):
    return (code & 0x40) != 0

def is_clear_voice(code):
    return (code & 0x04) != 0

def is_bass_ext(code):
    return (code & 0x20) != 0

def get_subwoofer(code):
    return '{:+1,d}'.format(code // 4 - 4)

def on_notify(sender, data: bytearray):
    code = data.hex()
    if (code.startswith('ccaa0d05')):
        surround = int.from_bytes(data[13:15], 'big')
        status = {}
        status['code'] = code
        status['mute'] = (data[7] == True)
        status['volume'] = data[8]
        status['subwoofer'] = get_subwoofer(data[9])
        status['surround'] = get_surround(surround)
        status['3d_sound'] = is_sound_3d(data[15])
        status['clear_voice'] = is_clear_voice(data[15])
        status['bass_ext'] = is_bass_ext(data[15])
        print(json.dumps(status, ensure_ascii=False, indent=4))

async def get_info(client):
    device_name = await client.read_gatt_char(UUID_DEVICE_NAME)
    print("Device Name: {0}".format("".join(map(chr, device_name))))
    
    manu_name = await client.read_gatt_char(UUID_MANUFACTURE_NAME)
    print("Manufacture Name: {0}".format("".join(map(chr, manu_name))))

async def write_command(client, command):
    bytes = bytearray.fromhex(command.replace(' ', ''))
    await client.write_gatt_char(UUID_WRITE, bytes, False)
#    print("Wrote command! command=" + command)

async def write_command_mode(client, on_command, off_command, mode):
    command = on_command if mode else off_command
    await write_command(client, command)

async def write_command_status(client):
    await write_command(client, WRITE_REQUEST_NOTIFY)

async def run(address):
    client = BleakClient(address)
    try:
        await client.connect(tomeout=5)
        await client.start_notify(UUID_NOTIFY, on_notify)

#        await get_info(client)

        if args.input == 'hdmi':
            await write_command(client, WRITE_CMD_INPUT_HDMI)
        elif args.input == 'bluetooth':
            await write_command(client, WRITE_CMD_INPUT_BLUETOOTH)
        elif args.input == 'tv':
            await write_command(client, WRITE_CMD_INPUT_TV)
        elif args.input == 'analog':
            await write_command(client, WRITE_CMD_INPUT_ANALOG)

        if args.surround == 'tv':
            await write_command(client, WRITE_CMD_SURROUND_TV)
        elif args.surround == 'stereo':
            await write_command(client, WRITE_CMD_SURROUND_STEREO)
        elif args.surround == 'movie':
            await write_command(client, WRITE_CMD_SURROUND_MOVIE)
        elif args.surround == 'music':
            await write_command(client, WRITE_CMD_SURROUND_MUSIC)
        elif args.surround == 'sports':
            await write_command(client, WRITE_CMD_SURROUND_SPORTS)
        elif args.surround == 'game':
            await write_command(client, WRITE_CMD_SURROUND_GAME)

        if args.sound_3d is not None:
            await write_command_mode(client, WRITE_CMD_SOUND_3D_ON, \
                                             WRITE_CMD_SOUND_3D_OFF, \
                                             args.sound_3d == 'on')
        if args.clear_voice is not None:
            await write_command_mode(client, WRITE_CMD_SOUND_CLEAR_VOICE_ON, \
                                             WRITE_CMD_SOUND_CLEAR_VOICE_OFF, \
                                             args.clear_voice == 'on')
        if args.bass_ext is not None:
            await write_command_mode(client, WRITE_CMD_SOUND_BASS_EXT_ON, \
                                             WRITE_CMD_SOUND_BASS_EXT_OFF, \
                                             args.bass_ext == 'on')

        if args.subwoofer is not None:
            await write_command_mode(client, WRITE_CMD_SOUND_SUBWOOFER_UP, \
                                             WRITE_CMD_SOUND_SUBWOOFER_DOWN, \
                                             args.subwoofer == 'up')

        if args.volume is not None:
            await write_command_mode(client, WRITE_CMD_VOLUME_UP, \
                                             WRITE_CMD_VOLUME_DOWN, \
                                             args.volume == 'up')

        if args.mute is not None:
            await write_command_mode(client, WRITE_CMD_MUTE_ON, \
                                             WRITE_CMD_MUTE_OFF, \
                                             args.mute == 'on')
        await write_command_status(client)
        await asyncio.sleep(2.0)
    except Exception as e:
        print(e)
    finally:
        if client.is_connected:
            await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(args.address))
