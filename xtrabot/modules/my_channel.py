from telethon import events

@borg.on(events.NewMessage(incoming=True))
async def transfer(event):
    target_channel = -1001165981906
    my_channel = -1001276100737
    if event.chat_id == target_channel:
        await borg.send_message(my_channel, event.message)
