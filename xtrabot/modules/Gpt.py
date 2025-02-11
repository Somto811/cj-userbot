import os
import openai
from telethon import events
from xtrabot import loader, client
from time import time

# Load OpenAI API key securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not set.")
openai.api_key = OPENAI_API_KEY

# Set to track users who have disabled AI
disabled_users = set()

@client.on(events.NewMessage(incoming=True))
async def chatgpt_auto_response(event):
    """Automatically respond in DMs unless disabled by user."""
    
    # Ignore groups and channels
    if event.is_group or event.is_channel:
        return

    user_id = event.sender_id

    # If user has disabled AI, don't respond
    if user_id in disabled_users:
        return

    if not event.text:
        return  # Ignore non-text messages

    query = event.text.strip()

    try:
        async with event.client.action(event.chat_id, "typing"):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use the GPT model you prefer
                messages=[{"role": "user", "content": query}]
            )
            reply = response["choices"][0]["message"]["content"].strip()
            await event.reply(reply)
    except Exception as e:
        await event.reply(f"Error: {str(e)}")

@loader.command(outgoing=True, pattern=r"^\.delcf$")
async def disable_ai(event):
    """Disable AI for a specific user."""
    reply_msg = await event.get_reply_message()
    if reply_msg and reply_msg.sender_id:
        user_id = reply_msg.sender_id
        disabled_users.add(user_id)
        await event.edit(f"AI disabled for [user](tg://user?id={user_id}).")
    else:
        await event.edit("Reply to a user’s message to disable AI.")

@loader.command(outgoing=True, pattern=r"^\.enacf$")
async def enable_ai(event):
    """Re-enable AI for a specific user."""
    reply_msg = await event.get_reply_message()
    if reply_msg and reply_msg.sender_id:
        user_id = reply_msg.sender_id
        if user_id in disabled_users:
            disabled_users.remove(user_id)
            await event.edit(f"AI re-enabled for [user](tg://user?id={user_id}).")
        else:
            await event.edit("AI was not disabled for this user.")
    else:
        await event.edit("Reply to a user’s message to enable AI.")

@loader.command(outgoing=True, pattern=r"^\.listcf$")
async def list_disabled_users(event):
    """List all users who have disabled AI."""
    if disabled_users:
        users = "\n".join([f"[user](tg://user?id={user_id})" for user_id in disabled_users])
        await event.edit(f"The following users have AI disabled:\n{users}")
    else:
        await event.edit("No users have disabled AI.")
