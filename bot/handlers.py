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
        "✨ Hi there!\n\n"
        "I'm your AI assistant, ready to help with questions, ideas, problem-solving, and much more.\n\n"
        "💬 Send me a message to get started.\n"
        "❓ Use /help to discover what I can do."
    )


@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):
    lines = [
        "/start - welcome message",
        "/help - show this message",
        "/reset - clear conversation history",
        "/about - about this bot",
        "/weather - weather",
        "/time - current time",
        "/quiz - quiz",
        "/fact - random fact",
        "/quotes - advice",
        "/reminder - reminders",
        "/todo - to do list",
        "/news - news",
    ]
    if HF_SPACE_ID:
        lines.append("/model - switch AI provider")

    bot.send_message(message.chat.id, "\n".join(lines))


@bot.message_handler(commands=["reset"], func=is_allowed)
def cmd_reset(message):
    clear_history(message.from_user.id)
    bot.send_message(message.chat.id, "Conversation cleared. Starting fresh!")


@bot.message_handler(commands=["about"], func=is_allowed)
def cmd_about(message):
    if HF_SPACE_ID:
        provider = get_provider(message.from_user.id)
        model_line = f"{MODEL} (main)" if provider == "main" else f"{HF_SPACE_ID} (hf)"
    else:
        model_line = MODEL
    storage_line = "SQLite" if store is not None else "stateless (no memory)"
    lines = [
        f"Model  : {model_line}",
        f"Storage: {storage_line}",
        f"Hosting: {HOSTING_LABEL}",
    ]
    if COMMIT_SHA:
        lines.append(f"Version: {COMMIT_SHA}")
    bot.send_message(message.chat.id, "\n".join(lines))


if HF_SPACE_ID:

    @bot.message_handler(commands=["model"], func=is_allowed)
    def cmd_model(message):
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) == 1:
            current = get_provider(message.from_user.id)
            bot.send_message(
                message.chat.id,
                f"Current provider: {current}\n\n"
                "Options:\n"
                "/model main — Cerebras (fast, multilingual, with memory)\n"
                "/model hf — ArmGPT (Armenian only, slow, no memory)",
            )
            return
        choice = parts[1].strip().lower()
        if choice not in ("main", "hf"):
            bot.send_message(
                message.chat.id, "Invalid choice. Use: /model main or /model hf"
            )
            return
        if not set_provider(message.from_user.id, choice):
            bot.send_message(
                message.chat.id, "Could not save preference. Try again later."
            )
            return
        if choice == "hf":
            bot.send_message(
                message.chat.id,
                "Switched to hf (ArmGPT).\n\n"
                "Note: this is a tiny base completion model trained only on Armenian text. "
                "It will continue whatever you write rather than answer questions, "
                "and it does not understand English. Replies take ~30-60s and there is no memory.",
            )
        else:
            bot.send_message(message.chat.id, "Switched to Main Provider.")


import random

# ---------------- WEATHER ----------------

@bot.message_handler(commands=["weather"], func=is_allowed)
def cmd_weather(message):
    bot.send_message(
        message.chat.id,
        "🌤️ Weather service example\n\n"
        "To get real weather data connect OpenWeather API."
    )


# ---------------- TIME ----------------

@bot.message_handler(commands=["time"], func=is_allowed)
def cmd_time(message):
    now = datetime.now().strftime("%H:%M:%S")
    bot.send_message(
        message.chat.id,
        f"🕒 Current time\n\n{now}"
    )


# ---------------- QUIZ ----------------

@bot.message_handler(commands=["quiz"], func=is_allowed)
def cmd_quiz(message):
    questions = [
        "❓ What is the capital of Armenia?\n\nA) Gyumri\nB) Yerevan\nC) Vanadzor",
        "❓ 2 + 2 = ?\n\nA) 3\nB) 4\nC) 5",
        "❓ Which planet is called the Red Planet?\n\nA) Mars\nB) Venus\nC) Jupiter",
        "❓ Which language is mostly used for AI?\n\nA) Python\nB) HTML\nC) CSS"
    ]
    bot.send_message(
        message.chat.id,
        random.choice(questions)
    )


# ---------------- FACT ----------------

@bot.message_handler(commands=["fact"], func=is_allowed)
def cmd_fact(message):
    facts = [
        "🧠 Your brain uses around 20% of your body's energy.",
        "🐙 Octopuses have 3 hearts.",
        "🍯 Honey never spoils.",
        "🦒 Giraffes sleep about 30 minutes per day.",
        "🌍 Earth rotates at about 1670 km/h."
    ]
    bot.send_message(
        message.chat.id,
        random.choice(facts)
    )


# ---------------- QUOTES ----------------

@bot.message_handler(commands=["quotes"], func=is_allowed)
def cmd_quotes(message):
    quotes = [
        "✨ Don't wait for opportunity. Create it.",
        "🚀 Small progress is still progress.",
        "🎯 Discipline beats motivation.",
        "🔥 Start before you're ready.",
        "💡 Success is built one day at a time."
    ]
    bot.send_message(
        message.chat.id,
        random.choice(quotes)
    )


# ---------------- REMINDER ----------------

@bot.message_handler(commands=["reminder"], func=is_allowed)
def cmd_reminder(message):
    bot.send_message(
        message.chat.id,
        "⏰ Reminder ideas:\n\n"
        "• Drink water 💧\n"
        "• Read 10 pages 📖\n"
        "• Exercise 20 minutes 🏃\n"
        "• Finish homework 📝\n"
        "• Sleep early 😴"
    )


# ---------------- TODO ----------------

@bot.message_handler(commands=["todo"], func=is_allowed)
def cmd_todo(message):
    bot.send_message(
        message.chat.id,
        "📝 Today's To-Do List\n\n"
        "☐ Study\n"
        "☑ Drink water\n"
        "☐ Exercise\n"
        "☐ Read a book\n"
        "☐ Finish assignments"
    )


# ---------------- NEWS ----------------

@bot.message_handler(commands=["news"], func=is_allowed)
def cmd_news(message):
    bot.send_message(
        message.chat.id,
        "📰 News service example\n\n"
        "To get real news connect NewsAPI."
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
