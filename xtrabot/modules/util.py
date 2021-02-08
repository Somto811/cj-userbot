#    X-tra-Telegram (userbot for telegram)
#    Copyright (C) 2019-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from xtrabot import loader, utils
from xtrabot.xtrautil import Module
import time
from datetime import datetime

class Util(loader.Module):
    def __init__(self):
        self.name = "ping"
        super().__init__([self.ping, self.help, self.abtping])
        self.addxconfig("PING", "Pong!\n", "Defines Ping Message")

    async def ping(self, event):
        start = datetime.now()
        await utils.answer(event, self.xconfig["PING"][0])
        end = datetime.now()
        if event.reply_to_msg_id:
            info = await event.get_reply_message()
        else:
            info = event
        DMY = time.strftime("%d.%m.%Y")
        HM = time.strftime("%H:%M:%S")
        TZ = time.strftime("%z")
        ms = (end - start).microseconds / 1000
        textmsg = "`ID = {}\nCHAT ID = {}\nDATE = {}\nTIME = {} GMT{}\nPING = {}ms`".format(info.id, info.chat_id, DMY, HM, TZ, ms)
        await utils.answer(event, textmsg)

    async def help(self, event):
        await utils.answer(event, "No help yet.")

    async def abtping(self, event):
        await utils.answer(event, self.xconfig["PING"][1])

Module(Util)
