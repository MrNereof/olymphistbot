from django_tgbot.decorators import processor
from django_tgbot.state_manager import message_types, update_types, state_types
from django_tgbot.types.update import Update

from django_tgbot.types.inlinekeyboardbutton import InlineKeyboardButton
from django_tgbot.types.inlinekeyboardmarkup import InlineKeyboardMarkup
from django_tgbot.types.keyboardbutton import KeyboardButton
from django_tgbot.types.replykeyboardmarkup import ReplyKeyboardMarkup

from .bot import TelegramBot
from .models import TelegramState, Epoch, Topic, Question, Attempt, UserAnswer

import typing
import io


def get_callback_message(update: Update):
    return update.get_callback_query().get_chat().get_id(), update.get_callback_query().get_message().get_message_id()


def send_with_image(bot: TelegramBot, *args, text: str = "", image: typing.Optional[io.BytesIO] = None, **kwargs):
    if image:
        return bot.sendPhoto(*args, caption=text, photo=image, upload=True, **kwargs)
    return bot.sendMessage(*args, text=text, **kwargs)


def get_questions(state: TelegramState):
    data = state.get_memory()

    queryset = Question.objects.all()

    if data["epoch"] != "all":
        queryset = queryset.filter(epoch=data["epoch"])
    if data["topic"] != "all":
        queryset = queryset.filter(topic=data["topic"])

    return queryset


def process_answer(answer: str) -> str:
    return answer.lower().replace("ё", "е")
