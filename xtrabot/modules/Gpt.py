import openai
from telethon import events
from time import time

# Set your OpenAI API key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# Dictionary to store enabled users and session expiration time
enabled_users = {}

@borg.on(events.NewMessage(incoming=True))
async def chatgpt_auto_response(event):
    """Automatically respond to users if AI is enabled for them."""
    # Ignore group chats and channels
    if event.is_group or event.is_channel:
        return

    user_id = event.sender_id

    # Automatically enable AI if it's not already enabled for the user
    if user_id not in enabled_users:
        enabled_users[user_id] = {"session_expires": time() + 3600}  # Session expires in 1 hour

    # Check if session expired
    if time() > enabled_users[user_id]["session_expires"]:
        del enabled_users[user_id]
        await event.reply("Your AI session has expired. Please contact the bot owner to enable it again.")
        return

    if not event.text:
        return  # Ignore non-text messages

    query = event.text.strip()  # User's message

    try:
        # Indicate typing action
        async with event.client.action(event.chat_id, "typing"):
            # Generate ChatGPT response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}]
            )
            reply = response["choices"][0]["message"]["content"].strip()
            await event.reply(reply)
    except Exception as e:
        await event.reply(f"Oops, I couldn't process that. Error: {str(e)}")

@borg.on(events.NewMessage(pattern=r"^\.enacf", outgoing=True))
async def enable_ai(event):
    """Enable AI response for a specific user."""
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.from_id
        enabled_users[user_id] = {"session_expires": time() + 3600}  # Set session expiry to 1 hour
        await event.edit(f"AI enabled for [user](tg://user?id={user_id}).")
    else:
        await event.edit("Reply to a user's message to enable AI for them.")

@borg.on(events.NewMessage(pattern=r"^\.delcf", outgoing=True))
async def disable_ai(event):
    """Disable AI response for a specific user."""
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.from_id
        if user_id in enabled_users:
            del enabled_users[user_id]
            await event.edit(f"AI disabled for [user](tg://user?id={user_id}).")
        else:
            await event.edit("This user doesn't have AI enabled.")
    else:
        await event.edit("Reply to a user's message to disable AI for them.")

@borg.on(events.NewMessage(pattern=r"^\.listcf", outgoing=True))
async def list_ai_users(event):
    """List all users with AI enabled."""
    if enabled_users:
        users = "\n".join([f"[user](tg://user?id={user_id})" for user_id in enabled_users])
        await event.edit(f"AI is enabled for the following users:\n{users}")
    else:
        await event.edit("No users have AI enabled.")
