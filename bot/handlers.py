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
Write a warm, exciting welcome message for a student opening an AI learning assistant for the first time.

Requirements:
- Sound human, upbeat, and genuinely curious about helping them learn
- Use 2-3 emojis, not more
- Mention that you explain things step by step, at their pace
- Invite them to ask literally anything, even "dumb" questions
- Mention /help briefly, once
- 4-6 lines, no filler
   """


   response = ask_ai(message.from_user.id, prompt + "\n\nUse /help command")


   bot.send_message(message.chat.id, response)
  
@bot.message_handler(commands=["reset"], func=is_allowed)
def cmd_reset(message):


   clear_history(message.from_user.id)


   prompt = """
Write a short message confirming a fresh start for an AI learning assistant.

Requirements:
- Friendly, light, a little playful — like wiping a whiteboard clean
- Confirm the previous conversation was cleared
- Frame this as a blank page, not a loss
- Encourage a new question or topic
- Mention /help once
- 4-6 lines
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
Write a help message for an AI learning assistant bot, formatted for Telegram.

Requirements:
- Catchy title with an emoji
- Group the commands below into 2-3 short categories (e.g. "Learning", "Fun & Games", "Utilities") instead of one long list
- One short, punchy line per command — no repeated phrasing across lines
- Friendly, energetic tone, not corporate
- End with a one-line motivational nudge to ask a question right now


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
Write one original motivational quote — not a paraphrase of a famous one.

Requirements:
- Specific and vivid, not generic ("believe in yourself" energy is banned)
- Maximum 2 sentences
- 1 emoji, placed naturally, not just tacked on the end
"""


   response = ask_ai(message.from_user.id, prompt)


   bot.send_message(message.chat.id, response)


   _log(message, "out", response)


   @bot.message_handler(commands=["fact"], func=is_allowed)
   def cmd_fact(message):


       prompt = """
Share one genuinely surprising fact most people don't know.

Requirements:
- Pick something counterintuitive, not the most overused trivia
- 2-4 sentences, written like you're excited to tell a friend
- 1-2 emojis
- End with a tiny "why this matters" or fun twist
"""


   response = ask_ai(message.from_user.id, prompt)


   bot.send_message(message.chat.id, response)


   _log(message, "out", response)


   @bot.message_handler(commands=["compliment"], func=is_allowed)
   def cmd_compliment(message):


    prompt = """
Write one original, specific-feeling compliment.

Requirements:
- Avoid generic praise ("you're amazing") — make it feel earned and particular
- 1-3 sentences
- 1 emoji
- Should make someone smile without sounding like a fortune cookie
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
    reply = ask_ai(message.from_user.id, f"Write a short, clever, PG-rated roast of {name} — playful and witty, never mean-spirited, max 3 lines.")
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

@bot.message_handler(commands=["joke"], func=is_allowed)
def cmd_joke(message):
    _ai_reply(
        message,
        JOKE_PROMPT,
        fallback="😅 Couldn't think of a joke right now, try again!"
    )

@bot.message_handler(commands=["about"], func=is_allowed)
def cmd_about(message):
    prompt = """
Write a short "about me" message for an AI learning assistant bot.

Requirements:
- Friendly, a little personality-forward (not robotic)
- Explain what you help with: explaining things, answering questions, learning together
- 4-6 lines
- 2-3 emojis
  """
    response = ask_ai(message.from_user.id,prompt)

    bot.send_message(message.chat.id,response)
