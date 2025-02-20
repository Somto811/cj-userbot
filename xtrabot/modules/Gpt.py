import os
import requests
from telethon import events
from xtrabot import loader, client
from time import time
import random
import asyncio

# Load DeepSeek API key securely
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DeepSeek API key not set.")

# DeepSeek API endpoint (replace with the actual endpoint)
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Set to track users who have disabled AI
disabled_users = set()

# Simulate human-like typing delay (in seconds)
TYPING_DELAY = random.uniform(7, 12)  # Random delay between 7 and 12 seconds

@client.on(events.NewMessage(incoming=True))
async def deepseek_auto_response(event):
    """Automatically respond in DMs unless disabled by user."""
    
    # Ignore groups, channels, and bots
    if event.is_group or event.is_channel:
        return

    user_id = event.sender_id

    # Ignore bots
    sender = await event.get_sender()
    if getattr(sender, "bot", False):  # Check if the sender is a bot
        return

    # If user has disabled AI, don't respond
    if user_id in disabled_users:
        return

    if not event.text:
        return  # Ignore non-text messages

    query = event.text.strip().lower()  # Normalize input to lowercase

    try:
        # Simulate typing before sending the response
        async with event.client.action(event.chat_id, "typing"):
            # Add a random delay to simulate human-like typing
            await asyncio.sleep(TYPING_DELAY)

            # Handle simple greetings like "hi"
            if query in ["hi", "hello", "hey"]:
                await event.reply("Hello!")
                return  # Exit after sending the response

            # For other messages, use DeepSeek API
            payload = {
                "model": "deepseek-chat",  # Replace with the correct model name
                "messages": [{"role": "user", "content": query}]
            }

            # Make the API request to DeepSeek
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)

            # Handle specific HTTP errors
            if response.status_code == 402:
                await event.reply("Sorry, the bot is currently unavailable due to payment requirements. Please contact the admin.")
                return
            response.raise_for_status()  # Raise an error for other bad responses

            # Parse the response
            reply = response.json()["choices"][0]["message"]["content"].strip()

            # Simulate typing while sending the response
            async with event.client.action(event.chat_id, "typing"):
                await asyncio.sleep(TYPING_DELAY)  # Add a delay before sending
                await event.reply(reply)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 402:
            await event.reply("Sorry, the bot is currently unavailable due to payment requirements. Please contact the admin.")
        else:
            await event.reply(f"Error: {str(e)}")
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
