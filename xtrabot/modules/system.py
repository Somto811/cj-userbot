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
import inspect
import traceback
import sys
import subprocess
from telethon.errors import MessageEmptyError, MessageTooLongError, MessageNotModifiedError
import io
import asyncio
import time

class System(loader.Module):
    def __init__(self):
        self.name = "eval"
        super().__init__([self.exc, self.bash])
        self.addxconfig("exec", "Processing...", "This is the Processing message when the script is being run")

    async def exc(self, event):
        await utils.answer(event, self.xconfig["exec"][0])
        cmd = event.text.split(" ", maxsplit=1)[1]
        reply_to_id = event.message.id
        if event.reply_to_msg_id:
            reply_to_id = event.reply_to_msg_id

        old_stderr = sys.stderr
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        redirected_error = sys.stderr = io.StringIO()
        stdout, stderr, exc = None, None, None

        try:
            await self.aexec(cmd, event)
        except Exception:
            exc = traceback.format_exc()

        stdout = redirected_output.getvalue()
        stderr = redirected_error.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        evaluation = ""
        if exc:
            evaluation = exc
        elif stderr:
            evaluation = stderr
        elif stdout:
            evaluation = stdout
        else:
            evaluation = "Success"

        final_output = "**EXC**: `{}` \n\n **OUTPUT**: \n`{}` \n".format(cmd, evaluation)
        await utils.answer(event, final_output)

    async def bash(self, event):
        DELAY_BETWEEN_EDITS = 0.3
        PROCESS_RUN_TIME = 100
        cmd = event.text.split(" ", maxsplit=1)[1]
        reply_to_id = event.message.id
        if event.reply_to_msg_id:
            reply_to_id = event.reply_to_msg_id
        start_time = time.time() + PROCESS_RUN_TIME
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        OUTPUT = f"**QUERY:**\n__Command:__\n`{cmd}` \n__PID:__\n`{process.pid}`\n\n**Output:**\n"
        stdout, stderr = await process.communicate()
        if stderr.decode():
            await utils.answer(event, f"{OUTPUT}`{stderr.decode()}`")
            return
        await utils.answer(event, f"{OUTPUT}`{stdout.decode()}`")

    async def aexec(self, code, event):
        exec(
            f'async def __aexec(event): ' +
            ''.join(f'\n {l}' for l in code.split('\n'))
        )
        return await locals()['__aexec'](event)

Module(System)
