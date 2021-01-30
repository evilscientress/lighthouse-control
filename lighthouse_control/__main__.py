import asyncio
import logging

from . import Lighthouse

logging.basicConfig(level=logging.INFO)
loop = asyncio.get_event_loop()
loop.run_until_complete(Lighthouse.discover())
