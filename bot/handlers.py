import os
import random
from datetime import datetime


from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


from bot.clients import bot, BOT_INFO, store
from bot.config import COMMIT_SHA, HF_SPACE_ID, HOSTING_LABEL, MODEL, RATE_LIMIT
from bot.ai import ask_ai
from bot.helpers import is_allowed, keep_typing, send_reply, should_respond
from bot.history import clear_history
from bot.preferences import get_provider
from bot.rate_limit import is_rate_limited

# Verbose console logging for local dev and teaching. Enabled by
# BOT_VERBOSE_LOG=1 (run_local.py sets this automatically). Prints one
# line per inbound/outbound message so kids and teachers can see the
# conversation flow in their terminal while the bot is running.
VERBOSE_LOG = os.environ.get("BOT_VERBOSE_LOG", "").strip().lower() in (
   "1",
   "true",
   "yes",
   "on",
)


def _log(message, direction: str, text: str) -> None:
   """Print a one-line trace of a message in verbose mode.


   direction is "in" (user → bot) or "out" (bot → user). Text is
   truncated to 500 characters so long AI replies don't flood the
   terminal. Newlines are collapsed for single-line readability.
   """
   if not VERBOSE_LOG:
       return
   user = message.from_user
   user_name = (
              f"@{user.username}" if user.username else (user.first_name or f"user:{user.id}")

   )
   bot_name = f"@{BOT_INFO.username}"
   snippet = (text or "").replace("\n", " ").replace("\r", " ")
   if len(snippet) > 500:
       snippet = snippet[:500] + "..."
   if direction == "in":
       sender, receiver = user_name, bot_name
   else:
       sender, receiver = bot_name, user_name
   ts = datetime.now().strftime("%H:%M:%S")
   print(f"[{ts}] {sender} → {receiver}: {snippet}", flush=True)




def _ai_reply(message, prompt: str, fallback: str) -> None:
   """Run a canned-command prompt through the AI and send the result.


   Falls back to a static message if the AI call fails, so commands
   stay usable even if the AI backend is down.
   """
   try:
       with keep_typing(message.chat.id):
           reply = ask_ai(message.from_user.id, prompt)
       send_reply(message, reply)
       _log(message, "out", reply)
   except Exception as e:
       print(f"Error generating AI reply: {e}")
       bot.send_message(message.chat.id, fallback)
       _log(message, "out", f"[error] {e}")


@bot.message_handler(commands=["start"], func=is_allowed)
def cmd_start(message):
   prompt = """
Generate a creative welcome message for a student using an AI learning assistant.


Requirements:
- Friendly, warm and natural tone
- Use a few emojis
- Explain that the bot teaches step by step
- Encourage the user to ask any question without hesitation
- Briefly mention that /help shows all available commands
- Make the user feel excited to learn
- Keep it short (4-6 lines)
   """


   response = ask_ai(message.from_user.id, prompt + "\n\nUse /help command")


   bot.send_message(message.chat.id, response)
  
@bot.message_handler(commands=["reset"], func=is_allowed)
def cmd_reset(message):


   clear_history(message.from_user.id)


   prompt = """
Generate a creative reset message for an AI learning assistant.


Requirements:


- Friendly, warm and natural tone
- Use a few emojis
- Explain that the previous conversation history was cleared
- Tell the user that they are starting a brand new conversation
- Encourage them to ask new questions and explore new ideas
- Briefly mention that /help shows all available commands
- Keep it short (4-6 lines)
"""


   response = ask_ai(message.from_user.id, prompt)


   bot.send_message(message.chat.id, response)


@bot.message_handler(commands=["sticker"], func=is_allowed)
def cmd_sticker(message):




   prompt = "Generate an stiker, that i can send in tg"


   response = ask_ai(message.from_user.id, prompt)


   bot.send_message(message.chat.id, response)



@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):


   prompt = """
Generate a creative help message for an AI learning assistant.


Requirements:


- Friendly, warm and natural tone
- Use emojis
- Create a beautiful title


Include these commands:


👋 /start - Welcome and introduction


❓ /help - Explore my features


🎨 /image - Generate image prompts


🔄 /reset - Start a fresh conversation


😂 /joke - Get a funny joke


😄 /sticker - Send a random sticker


🤖 /about - Learn who I am


🌤️ /weather - Check the weather


🕒 /time - See the current time


🧩 /quiz - Challenge yourself


🧠 /fact - Discover something interesting


💬 /quotes - Get inspiration


⏰ /reminder - Useful reminders


📝 /todo - Organize your tasks


🗑️ /delete - Clear the conversation


📰 /news - Read the latest news


🧠 /fact - Discover something interesting


🌟 /compliment - Receive a compliment


🎲 /roll - Roll a dice


- Explain each briefly
- Encourage learning and asking questions
- Keep it short and clear
- End with a motivational sentence


End with:


💡 Ask questions, learn new things, generate ideas, or simply chat. I'm here to make every conversation useful and enjoyable.
"""


   response = ask_ai(message.from_user.id, prompt)


   bot.send_message(message.chat.id, response)
  
@bot.message_handler(commands=["quote"], func=is_allowed)
def cmd_quote(message):


   prompt = """
Generate one original motivational quote.


Requirements:


- Positive and inspiring
- Friendly and natural
- Maximum 2 sentences
- Use 1-2 emojis
- Do not copy famous quotes
"""


   response = ask_ai(message.from_user.id, prompt)


   bot.send_message(message.chat.id, response)


   _log(message, "out", response)


   @bot.message_handler(commands=["fact"], func=is_allowed)
   def cmd_fact(message):


       prompt = """
Generate one surprising and interesting fact.


Requirements:


- Educational
- Easy to understand
- 2-4 sentences
- Use emojis
- Make it fun
"""


   response = ask_ai(message.from_user.id, prompt)


   bot.send_message(message.chat.id, response)


   _log(message, "out", response)


   @bot.message_handler(commands=["compliment"], func=is_allowed)
   def cmd_compliment(message):


    prompt = """
Generate one original compliment.


Requirements:


- Warm and encouraging
- 1-3 sentences
- Friendly tone
- Use emojis
- Make the user smile
"""


   response = ask_ai(message.from_user.id, prompt)


   bot.send_message(message.chat.id, response)


   _log(message, "out", response)


@bot.message_handler(commands=["roll"], func=is_allowed)
def cmd_roll(message):


    number = random.randint(1, 6)
    response = f"🎲 You rolled: {number}"


    bot.send_message(message.chat.id,response)

    _log(message, "out", response)


@bot.message_handler(commands=["roast"], func=is_allowed)
def cmd_roast(message):
    name = message.text.split(maxsplit=1)[1] if " " in message.text else "you"
    reply = ask_ai(message.from_user.id, f"Write a short, playful, friendly roast of {name}.")
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["remember"], func=is_allowed)
def cmd_remember(message):

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2 or not parts[1].strip():
        bot.send_message(
            message.chat.id,
            "⚠️ Please write something to remember.\nExample: /remember buy milk"
        )
        return

    note = parts[1].strip()

    store.set(
        f"note:{message.from_user.id}",
        note
    )

    bot.send_message(
        message.chat.id,
        "💾 Saved!"
    )

    _log(message, "out", note)

    @bot.message_handler(commands=["recall"], func=is_allowed)
    def cmd_recall(message):

        note = store.get(
        f"note:{message.from_user.id}"
    )

    if not note:
        bot.send_message(
            message.chat.id,
            "📭 You have nothing saved yet."
        )
        return

    bot.send_message(
        message.chat.id,
        f"🧠 Your saved note:\n{note}"
    )

    _log(message, "out", note)

@bot.message_handler(commands=["note"], func=is_allowed)
def cmd_note(message):
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        bot.send_message(
        message.chat.id,
        "Usage: /note <key> <text>"
        )
        return 


    key = parts[1]
    value = parts[2]

    notes = store.get(f"notes:{message.from_user.id}")

    if notes:
        notes = json.loads(notes)
    else:
        notes = {}

    notes[key] = value

    store.set(
    f"notes:{message.from_user.id}",
    json.dumps(notes)
)

    bot.send_message(
    message.chat.id,
    f"Saved note '{key}'."
    )

@bot.message_handler(commands=["forget"], func=is_allowed)
def cmd_forget(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(
        message.chat.id,
        "🗑️ Which note should I forget?\nUsage: /forget <key>"
    )
        return

    key = parts[1].strip()

    notes = store.get(f"notes:{message.from_user.id}")

    if not notes:
        bot.send_message(
        message.chat.id,
        "📭 Your memory box is empty. No notes to forget."
    )
        return

    notes = json.loads(notes)

    if key not in notes:
        bot.send_message(
        message.chat.id,
        f"🤔 I couldn't find a note called '{key}'."
    )
        return

    del notes[key]

    store.set(
    f"notes:{message.from_user.id}",
    json.dumps(notes)
    )

    bot.send_message(
    message.chat.id,
    f"🧹 Done! I've forgotten '{key}'."
    )


@bot.message_handler(commands=["about"], func=is_allowed)
def cmd_about(message):
    prompt = """
Generate a short about message for an AI learning assistant.

Requirements:

* Friendly tone
* Use emojis
* Explain what the bot can do
* 4-6 lines
  """
    response = ask_ai(message.from_user.id,prompt)

    bot.send_message(message.chat.id,response)
