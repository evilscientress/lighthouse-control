import asyncio
import functools
import logging
from struct import pack, unpack
from typing import Union

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

logger = logging.getLogger('lighthouse_control')

class Lighthouse:

    MANUFACTURER_ID = 1373
    SERVICE_UUID = '00001523-1212-EFDE-1523-785FEABCD124'
    POWER_CHARACTERISTIC = '00001525-1212-EFDE-1523-785FEABCD124'
    CHANNEL_CHARACTERISTIC = '00001524-1212-EFDE-1523-785FEABCD124'
    IDENTIFY_CHARACTERISTIC = '00008421-1212-EFDE-1523-785FEABCD124'

    POWER_STATE_SLEEP = 0x00
    POWER_STATE_STANDBY = 0x02
    POWER_STATE_ON = 0x0b
    POWER_STATE_BOOTING = 0x01
    POWER_STATE_UNKNOWN = None

    POWER_STATES = {
        POWER_STATE_SLEEP: "sleep",
        POWER_STATE_STANDBY: "standby",
        POWER_STATE_ON: 'on',
        POWER_STATE_BOOTING: 'booting',
        POWER_STATE_UNKNOWN: 'unknown',
    }

    def __init__(self, device: Union[str, BLEDevice]):
        self.device = device

    @classmethod
    def power_state_from_byte(cls, power_state):
        power_state = unpack('B', power_state)[0]
        if power_state == 0x01 or power_state == 0x08 or power_state == 0x09:
            power_state = cls.POWER_STATE_BOOTING
        elif power_state not in cls.POWER_STATES:
            power_state = cls.POWER_STATE_UNKNOWN
        return power_state

    async def get_power_state(self):
        async with BleakClient(self.device) as client:
            power_state = self.power_state_from_byte(await client.read_gatt_char(self.POWER_CHARACTERISTIC))
            self.__dict__['power_state'] = power_state  # store the last known power state in the power_state property
            return power_state

    @functools.cached_property
    async def power_state(self):
        return await self.get_power_state()

    async def get_power_state_verbose(self):
        return self.POWER_STATES[await self.get_power_state()]

    async def set_power_state(self, power_state):
        if power_state not in {self.POWER_STATE_SLEEP, self.POWER_STATE_STANDBY, self.POWER_STATE_ON}:
            raise ValueError('Invalid Power State')
        if power_state == self.POWER_STATE_ON:
            # to turn on a lighthouse you need to write 0x01 to it
            power_state = 0x01
        async with BleakClient(self.device) as client:
            await client.write_gatt_char(self.POWER_CHARACTERISTIC, bytearray(pack('B', power_state)))

    async def get_channel(self):
        async with BleakClient(self.device) as client:
            power_state = unpack('B', await client.read_gatt_char(self.CHANNEL_CHARACTERISTIC))[0]
            self.__dict__['channel'] = power_state  # store the last known channel in the channel property
            return power_state

    @functools.cached_property
    async def channel(self):
        return await self.get_channel()

    async def identify(self):
        async with BleakClient(self.device) as client:
            await client.write_gatt_char(self.IDENTIFY_CHARACTERISTIC, bytearray(pack('B', 0x00)))

    @classmethod
    async def discover(cls):
        devices = await BleakScanner.discover()
        lighthouses = []
        for d in devices:
            if d.name.startswith('LHB') and cls.MANUFACTURER_ID in d.metadata.get('manufacturer_data', dict()):
                logger.debug('found potential lighthouse %s', d)
                async with BleakClient(d.address) as client:
                    svc = (await client.get_services()).get_service(cls.SERVICE_UUID)
                    if svc is not None:
                        power_state = cls.POWER_STATES[
                            cls.power_state_from_byte(await client.read_gatt_char(cls.POWER_CHARACTERISTIC))
                        ]
                        logger.info("Found Lighthouse %s, current power state: %s", d.name, power_state)
                        lighthouses.append(cls(d))
        return lighthouses


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Lighthouse.discover())
