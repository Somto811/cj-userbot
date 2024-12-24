import openai
from telethon import events
from time import time
import asyncio
import json

# Replace with your OpenAI API key
openai.api_key = "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"

# Dictionary to manage users with enabled GPT auto-response
enabled_users = {}

# Function to interact with OpenAI Chat
async def chat_with_gpt(message):
    try:
        response = openai.Chat.create(
            model="gpt-3.5-turbo",  # Use the appropriate model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ],
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error: {str(e)}"


# Enable auto-response for a user
@borg.on(events.NewMessage(pattern=r"\.enacf", outgoing=True))
async def enable_chat(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.from_id
        chat_id = event.chat_id
        enabled_users[user_id] = {"chat_id": chat_id, "enabled_at": time()}
        await event.edit(f"GPT auto-response enabled for [user](tg://user?id={user_id}).")
    else:
        await event.edit("Reply to a user's message to enable GPT auto-response for them.")


# Disable auto-response for a user
@borg.on(events.NewMessage(pattern=r"\.delcf", outgoing=True))
async def disable_chat(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.from_id
        if user_id in enabled_users:
            del enabled_users[user_id]
            await event.edit(f"GPT auto-response disabled for [user](tg://user?id={user_id}).")
        else:
            await event.edit("This user does not have GPT auto-response enabled.")
    else:
        await event.edit("Reply to a user's message to disable GPT auto-response for them.")


# List all users with GPT auto-response enabled
@borg.on(events.NewMessage(pattern=r"\.listcf", outgoing=True))
async def list_users(event):
    if enabled_users:
        user_list = "\n".join(
            [f"[user](tg://user?id={user_id}) in chat `{data['chat_id']}`" for user_id, data in enabled_users.items()]
        )
        await event.edit(f"GPT auto-response enabled for:\n\n{user_list}")
    else:
        await event.edit("No users have GPT auto-response enabled.")


# Handle incoming messages and respond automatically
@borg.on(events.NewMessage(incoming=True))
async def auto_response(event):
    user_id = event.from_id
    chat_id = event.chat_id

    # Auto-enable for any DM (private chat) unless explicitly disabled
    if event.is_private and user_id not in enabled_users:
        enabled_users[user_id] = {"chat_id": chat_id, "enabled_at": time()}

    # Respond if the user is in the enabled list
    if user_id in enabled_users:
        if not event.media:  # Avoid processing media messages
            query = event.text
            async with event.client.action(chat_id, "typing"):
                await asyncio.sleep(1)  # Simulate typing
                response = await chat_with_gpt(query)
                await event.reply(response)
