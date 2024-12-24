from telethon import events
from xtrabot import client
import asyncio
import secrets
import datetime

class TCoinMod(object):
    def __init__(self):
        self.farmChecked = False
        self.rateLimit = 0
        self.rateLimited = False
        self.lastWatered = None  # Track the last watering time

    async def periodic_farm_check(self):
        """Background task to periodically check and water the farm."""
        while True:
            if self.lastWatered and (datetime.datetime.now() - self.lastWatered).days < 5:
                await asyncio.sleep(3600)  # Sleep for an hour if watering isn't due
                continue

            try:
                async with client.conversation(-1001394158904) as conv:  # Replace with your chat ID
                    await conv.send_message("!farm")
                    message = await conv.get_response()

                    name = client.me.first_name[:15]
                    messagelines = message.text.splitlines()

                    if f"> {name}'s farm:" not in message.text:
                        continue

                    if "> water: dry" in messagelines[-3]:
                        await asyncio.sleep(1.5)
                        await conv.send_message("!farm water")
                        self.lastWatered = datetime.datetime.now()
                    elif "> water: crop died" in messagelines[-1]:
                        await asyncio.sleep(1.5)
                        await conv.send_message("!farm reset")
                        await asyncio.sleep(1.5)
                        await conv.send_message("!farm random")
                        await asyncio.sleep(1.5)
                        await conv.send_message("!farm plant")
                    elif (averageM := messagelines[-2][-20:-18]).isdigit():
                        averageM = int(averageM)
                        if averageM > 97:
                            await asyncio.sleep(1.5)
                            await conv.send_message("!farm harvest")
                            await asyncio.sleep(1.5)
                            await conv.send_message("!farm reset")
                            await asyncio.sleep(1.5)
                            await conv.send_message("!farm random")
                            await asyncio.sleep(1.5)
                            await conv.send_message("!farm plant")

            except Exception as e:
                print(f"Error in periodic farm check: {e}")

            await asyncio.sleep(86400)  # Sleep for a day before checking again

    async def farm_watcher(self, event):
        """Watcher triggered by new messages."""
        name = event.client.me.first_name[:15]
        if event.chat_id != -1001394158904:
            return
        lines = event.text.splitlines()
        if not self.farmChecked:
            self.farmChecked = True
            async with event.client.conversation(event.chat_id) as conv:
                await asyncio.sleep(5)
                await conv.send_message("!farm")
                message = await conv.get_response()

                messagelines = message.text.splitlines()
                if "> water: dry" in messagelines[-3]:
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

tcoin = TCoinMod()
client.add_event_handler(tcoin.farm_watcher, events.NewMessage())
client.loop.create_task(tcoin.periodic_farm_check())  # Start the periodic check task
client.add_event_handler(tcoin.mine_watcher, events.NewMessage())
client.add_event_handler(tcoin.roulette_watcher, events.NewMessage())
