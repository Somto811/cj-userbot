from telethon import events
from xtrabot import client
import asyncio
import secrets

class TCoinMod(object):
    def __init__(self):
        self.farmChecked = False
        self.rateLimit = 0
        self.rateLimited = False

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

tcoin = TCoinMod()
client.add_event_handler(tcoin.farm_watcher, events.NewMessage())
client.add_event_handler(tcoin.mine_watcher, events.NewMessage())
client.add_event_handler(tcoin.roulette_watcher, events.NewMessage())
