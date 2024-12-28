from telethon import events
from telethon import functions
from xtrabot import client
import asyncio
import datetime

class TCoinMod(object):
    def __init__(self):
        self.farmChecked = False
        self.rateLimit = 0
        self.rateLimited = False
        self.nextWaterTime = datetime.datetime.now()

    # Watch for mining updates
    async def mine_watcher(self, event):
        name = event.client.me.first_name[:15]
        if event.chat_id != -1001394158904 or \
           event.sender_id != 79316791:
            return
        lines = event.text.splitlines()
        if len(lines) < 3:
            return
        if not lines[1] == "> exhausted miners:":
            return
        if not name in lines[2]:
            await asyncio.sleep(6)
            await event.respond("!mine")

    # Watch for farming updates
    async def farm_watcher(self, event):
        name = event.client.me.first_name[:15]
        if event.chat_id != -1001394158904:
            return
        lines = event.text.splitlines()
        if not self.farmChecked:
            self.farmChecked = True
            async with event.client.conversation(event.chat_id) as conv:
                await asyncio.sleep(5)
                await conv.send_message("!farm")
                message = await conv.wait_event(
                    events.NewMessage(
                        -1001394158904,
                        from_users=[79316791],
                        func=lambda e: e.text.startswith(
                            f"> {name}'s farm:"
                        )
                    )
                )
                messagelines = message.text.splitlines()
                if "> water: dry" == messagelines[-3]:
                    await asyncio.sleep(1.5)
                    await event.respond("!farm water")
                elif "> water: crop died" in messagelines[-1]:
                    await asyncio.sleep(1.5)
                    await event.respond("!farm reset")
                    await asyncio.sleep(1.5)
                    await event.respond("!farm random")
                    await asyncio.sleep(1.5)
                    await event.respond("!farm plant")
                elif (averageM := messagelines[-2][-20:-18]).isdigit():
                    averageM = int(averageM)
                    if averageM > 97:
                        await asyncio.sleep(1.5)
                        await event.respond("!farm harvest")
                        await asyncio.sleep(1.5)
                        await event.respond("!farm reset")
                        await asyncio.sleep(1.5)
                        await event.respond("!farm random")
                        await asyncio.sleep(1.5)
                        await event.respond("!farm plant")

    # Watch for roulette messages
    async def roulette_watcher(self, event):
        name = event.client.me.first_name[:15]
        if event.chat_id != -1001394158904:  # Adjust chat_id as needed
            return
        lines = event.text.splitlines()
        if len(lines) < 3:
            return
        if "roulette" in lines[0].lower():
            await asyncio.sleep(1.5)
            await event.respond("!roulette play")

    # Periodic task to water crops every 5 days
    async def periodic_farm_watering(self):
        while True:
            now = datetime.datetime.now()
            if now >= self.nextWaterTime:
                self.nextWaterTime = now + datetime.timedelta(days=5)
                await client.send_message(-1001394158904, "!farm water")
            await asyncio.sleep(3600)  # Check every hour

# Instantiate the class
tcoin = TCoinMod()

# Register event handlers
client.add_event_handler(tcoin.farm_watcher, events.NewMessage())
client.add_event_handler(tcoin.mine_watcher, events.NewMessage())
client.add_event_handler(tcoin.roulette_watcher, events.NewMessage())

# Start the periodic watering task
client.loop.create_task(tcoin.periodic_farm_watering())
