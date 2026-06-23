import os
from datetime import datetime
from bot.clients import bot, BOT_INFO, store
from bot.config import COMMIT_SHA, HF_SPACE_ID, HOSTING_LABEL, MODEL, RATE_LIMIT
from bot.ai import ask_ai
from bot.helpers import is_allowed, keep_typing, send_reply, should_respond
from bot.history import clear_history
from bot.preferences import get_provider, set_provider
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


@bot.message_handler(commands=["start"], func=is_allowed)
def cmd_start(message):
bot.send_message(
message.chat.id,
"👋 Welcome!\n\n"
"I'm your intelligent, friendly, and creative AI assistant.\n\n"
"✨ Ask questions\n"
"💡 Explore ideas\n"
"📚 Learn something new\n"
"📝 Improve your writing\n"
"🚀 Solve problems faster\n\n"
"💬 Send a message to begin.\n"
"❓ Type /help to discover everything I can do."
)

@bot.message_handler(commands=["delete"], func=is_allowed)
def cmd_delete(message):

keyboard = InlineKeyboardMarkup()

btn = InlineKeyboardButton(
    "🗑️ Delete conversation",
    callback_data="delete_chat"
)

keyboard.add(btn)

bot.send_message(
    message.chat.id,
    "🗑️ Want to start over?\n\n"
    "Click the button below to delete the entire conversation and begin with a clean slate.",
    reply_markup=keyboard
)

@bot.callback_query_handler(func=lambda call: call.data == "delete_chat")
def delete_chat(call):

clear_history(call.from_user.id)

bot.answer_callback_query(
    call.id,
    "Deleted ✅"
)

bot.send_message(
    call.message.chat.id,
    "✅ Conversation deleted.\n\n✨ You're ready for a fresh start."
)

@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):

lines = [
    "✨ Here's how I can help you:",
    "",
    "👋 /start - Welcome and introduction",
    "❓ /help - Explore my features",
    "🔄 /reset - Start a fresh conversation",
    "🤖 /about - Learn who I am",
    "🌤️ /weather - Check the weather",
    "🕒 /time - See the current time",
    "🧩 /quiz - Challenge yourself",
    "🧠 /fact - Discover something interesting",
    "💬 /quotes - Get inspiration",
    "⏰ /reminder - Useful reminders",
    "📝 /todo - Organize your tasks",
    "🗑️ /delete - Clear the conversation",
    "📰 /news - Read the latest news",
    "",
    "💡 Ask questions, learn new things, generate ideas, or simply chat. I'm here to make every conversation useful and enjoyable."
]

if HF_SPACE_ID:
    lines.append("🤖 /model - Switch AI provider")

bot.send_message(message.chat.id, "\n".join(lines))


@bot.message_handler(commands=["about"], func=is_allowed)
def cmd_about(message):


if HF_SPACE_ID:
    provider = get_provider(message.from_user.id)

    model_line = (
        f"{MODEL} (main)"
        if provider == "main"
        else f"{HF_SPACE_ID} (hf)"
    )
else:
    model_line = MODEL

storage_line = (
    "SQLite"
    if store is not None
    else "Stateless (no memory)"
)

lines = [
    "👋 Hello! I'm your AI assistant.",
    "",
    "✨ Friendly and easy to talk to.",
    "🧠 Intelligent and practical.",
    "💡 Creative with ideas and solutions.",
    "📚 Able to explain complex topics simply.",
    "📝 Helpful for writing and improving English.",
    "🌍 Ready to share facts, advice, and inspiration.",
    "",
    f"🤖 Model: {model_line}",
    f"💾 Storage: {storage_line}",
    f"🖥️ Hosting: {HOSTING_LABEL}",
]

if COMMIT_SHA:
    lines.append(f"🔖 Version: {COMMIT_SHA}")

lines.append("")
lines.append("💬 Learn • Create • Explore • Enjoy")

bot.send_message(
    message.chat.id,
    "\n".join(lines)
)
@bot.message_handler(commands=["weather"], func=is_allowed)
def cmd_weather(message):

bot.send_message(
    message.chat.id,
    "🌤️ Weather Center\n\n"
    "Connect an OpenWeather API key to get real-time weather forecasts from anywhere in the world."
)


@bot.message_handler(commands=["time"], func=is_allowed)
def cmd_time(message):


now = datetime.now().strftime("%H:%M:%S")

bot.send_message(
    message.chat.id,
    f"🕒 Current time\n\n{now}\n\n⏳ Every second is a new opportunity."
)


@bot.message_handler(commands=["fact"], func=is_allowed)
def cmd_fact(message):

facts = [
    "🧠 Your brain uses around 20% of your body's energy.",
    "🐙 Octopuses have 3 hearts.",
    "🍯 Honey never spoils.",
    "🦒 Giraffes sleep about 30 minutes per day.",
    "🌍 Earth rotates at about 1670 km/h.",
    "⚡ A lightning bolt is five times hotter than the Sun's surface.",
    "🌕 The Moon is slowly moving away from Earth every year."
]

bot.send_message(
    message.chat.id,
    random.choice(facts)
)

@bot.message_handler(commands=["quotes"], func=is_allowed)
def cmd_quotes(message):

quotes = [
    "✨ Don't wait for opportunity. Create it.",
    "🚀 Small progress is still progress.",
    "🎯 Discipline beats motivation.",
    "🔥 Start before you're ready.",
    "💡 Success is built one day at a time.",
    "🌱 Growth begins outside your comfort zone.",
    "⭐ Great things take time."
]

bot.send_message(
    message.chat.id,
    random.choice(quotes)
)

@bot.message_handler(commands=["reminder"], func=is_allowed)
def cmd_reminder(message):

bot.send_message(
    message.chat.id,
    "⏰ Friendly reminders\n\n"
    "💧 Drink water\n"
    "📖 Read 10 pages\n"
    "🏃 Move your body\n"
    "📝 Finish important tasks\n"
    "😴 Get enough sleep"
)

@bot.message_handler(commands=["todo"], func=is_allowed)
def cmd_todo(message):

bot.send_message(
    message.chat.id,
    "📝 Today's checklist\n\n"
    "☐ Study\n"
    "☑ Drink water\n"
    "☑ Take a short break\n"
    "☐ Exercise\n"
    "☑ Learn something new\n"
    "☑ Read a book"
)

@bot.message_handler(commands=["news"], func=is_allowed)
def cmd_news(message):


bot.send_message(
    message.chat.id,
    "📰 News Center\n\n"
    "Connect NewsAPI to receive real-time headlines and stay updated."
)

@bot.message_handler(content_types=["text"], func=is_allowed)
def handle_message(message):
    if not should_respond(message):
        return
    text = (message.text or "").replace(f"@{BOT_INFO.username}", "").strip()
    if not text:
        # Edited messages, forwards, or stickers-with-empty-caption can
        # arrive with no usable text. Don't burn rate-limit / AI calls on them.
        return
    _log(message, "in", text)
    if is_rate_limited(message.from_user.id):
        limit_msg = f"You've reached the daily limit of {RATE_LIMIT} messages. Try again tomorrow."
        bot.send_message(message.chat.id, limit_msg)
        _log(message, "out", f"[rate limited] {limit_msg}")
        return
    try:
        with keep_typing(message.chat.id):
            reply = ask_ai(message.from_user.id, text)
        send_reply(message, reply)
        _log(message, "out", reply)
    except Exception as e:
        print(f"Error in handle_message: {e}")
        bot.send_message(message.chat.id, "Something went wrong. Please try again.")
        _log(message, "out", f"[error] {e}")
