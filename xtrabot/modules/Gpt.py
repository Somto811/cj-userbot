from telethon import events
import openai

# Set up OpenAI API
openai.api_key = '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'

# Store the IDs of users who are disabled for auto-response
enabled_users = set()

# Flag to control whether auto-response is enabled for all users by default
all_users_enabled = True

# Your bot client (replace 'client' with your actual bot client instance)
@client.on(events.NewMessage(incoming=True))
async def auto_response(event):
    global all_users_enabled  # Declare this variable as global here

    user_id = event.sender_id  # Correctly get the user ID as an integer

    # Check if auto-response is enabled for all users or the user is not disabled
    if all_users_enabled or user_id not in enabled_users:
        # Handle the auto-response (responding with ChatGPT or custom response)
        response = await generate_chatgpt_response(event.text)
        await event.reply(response)

    # Command to disable auto-response for the user
    elif event.text == "/delcf":
        enabled_users.add(user_id)  # Add user to the disabled list
        await event.reply("Auto-response disabled for you!")

    # Command to enable auto-response for the user
    elif event.text == "/enacf":
        if user_id in enabled_users:
            enabled_users.remove(user_id)  # Remove user from the disabled list
            await event.reply("Auto-response enabled for you!")

    # Command to disable auto-response for everyone
    elif event.text == "/disable_all":
        all_users_enabled = False
        await event.reply("Auto-response disabled for all users!")

    # Command to enable auto-response for everyone
    elif event.text == "/enable_all":
        all_users_enabled = True
        await event.reply("Auto-response enabled for all users!")

# Function to generate ChatGPT response
async def generate_chatgpt_response(prompt):
    try:
        # Use OpenAI's GPT model to generate a response to the user's message
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can change to a different model if you prefer
            prompt=prompt,
            max_tokens=150  # Adjust max tokens as needed
        )
        return response.choices[0].text.strip()  # Return the text response from GPT
    except Exception as e:
        return f"Sorry, I couldn't generate a response. Error: {e}"
