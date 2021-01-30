import argparse
import asyncio
import logging

from bleak import BleakError

from . import Lighthouse

parser = argparse.ArgumentParser(description='Lighthouse Control')
parser.add_argument('-d', '--discover', action='store_true', help='discover lighthouses')
parser.add_argument('-o', '--on', nargs='+', metavar='mac', help='turn lighthouses on')
parser.add_argument('-s', '--sleep', nargs='+', metavar='mac', help='put lighthouses into sleep mode')
parser.add_argument('--standby', nargs='+', metavar='mac', help='put lighthouses into standby mode')
parser.add_argument('--identify', nargs='+', metavar='mac',
                    help='identify a lighthouse by letting it\'s LED blink white')
parser.add_argument('-i', '--info', nargs='*', metavar='mac',
                    help='print information about lighthouses (name, power_state, channel, firmware version, etc.')
args = parser.parse_args()

# configure logging
logging.basicConfig(level=logging.INFO)

# run rest of the code in a async context
async def set_lh_powerstate(device, power_state):
    try:
        logging.info('setting %s to power state %s', device, Lighthouse.POWER_STATES[power_state])
        await Lighthouse(device).set_power_state(power_state)
    except BleakError as e:
        logging.exception('Error communicating with lighthouse: %s', device)

async def cmd_line_handler(args):
    if args.discover or not any((args.on, args.sleep, args.standby, args.identify, args.info)):
        lighthouses = await Lighthouse.discover()
    elif args.on:
        await asyncio.gather(*[set_lh_powerstate(d, Lighthouse.POWER_STATE_ON) for d in args.on])
    elif args.standby:
        await asyncio.gather(*[set_lh_powerstate(d, Lighthouse.POWER_STATE_STANDBY) for d in args.standby])
    elif args.sleep:
        await asyncio.gather(*[set_lh_powerstate(d, Lighthouse.POWER_STATE_SLEEP) for d in args.sleep])
    elif args.identify:
        for device in args.identify:
            try:
                await Lighthouse(device).identify()
            except BleakError as e:
                logging.exception('Error communicating with lighthouse: %s', device)
    elif args.info:
        raise NotImplementedError()

loop = asyncio.get_event_loop()
loop.run_until_complete(cmd_line_handler(args))
