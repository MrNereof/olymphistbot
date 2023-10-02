from django_tgbot.decorators import processor
from django_tgbot.state_manager import message_types, update_types, state_types
from django_tgbot.types.update import Update

from django_tgbot.types.inlinekeyboardbutton import InlineKeyboardButton
from django_tgbot.types.inlinekeyboardmarkup import InlineKeyboardMarkup
from django_tgbot.types.keyboardbutton import KeyboardButton
from django_tgbot.types.replykeyboardmarkup import ReplyKeyboardMarkup

from .utils import get_callback_message, send_with_image
from .bot import state_manager
from .models import TelegramState, Epoch, Topic
from .bot import TelegramBot

from olymphistory_bot import messages


@processor(state_manager, update_types=update_types.Message,
           message_types=message_types.Text, from_states=state_types.All)
def message_processor(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id = update.get_chat().get_id()
    text = str(update.get_message().get_text())

    match text:
        case "/start":
            send_start(bot, chat_id, state)


def send_start(bot: TelegramBot, chat_id, state: TelegramState):
    bot.sendMessage(chat_id,
                    text=messages.START_MESSAGE,
                    reply_markup=InlineKeyboardMarkup.a(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton.a(messages.TRAINING_BUTTON, callback_data='training')
                            ]
                        ]
                    ))
    state.reset_memory()
    state.set_name("started")


@processor(state_manager, from_states="started", update_types=[update_types.CallbackQuery])
def handle_started(bot: TelegramBot, update: Update, state: TelegramState):
    callback_data = update.get_callback_query().get_data()
    match callback_data:
        case "training":
            handle_training(bot, update, state)


def handle_training(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id, message_id = get_callback_message(update)

    bot.editMessageText(messages.SELECTION_MESSAGE, chat_id=chat_id, message_id=message_id,
                        reply_markup=InlineKeyboardMarkup.a(
                            inline_keyboard=[
                                [InlineKeyboardButton.a(messages.SELECT_EPOCH_BUTTON, callback_data="epoch"),
                                 InlineKeyboardButton.a(messages.SELECT_TOPIC_BUTTON, callback_data="topic")],
                            ]
                        )
                        )
    state.set_name("topic_or_epochs")


@processor(state_manager, from_states="topic_or_epochs", update_types=[update_types.CallbackQuery])
def handle_selection(bot: TelegramBot, update: Update, state: TelegramState):
    callback_data = update.get_callback_query().get_data()
    match callback_data:
        case "epoch":
            send_epoch_selection(bot, update, state)
        case "topic":
            send_topic_selection(bot, update, state)


def send_epoch_selection(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id, message_id = get_callback_message(update)

    topic_id = state.get_memory().get("topic")

    match topic_id:
        case None | "all":
            queryset = Epoch.objects.order_by("position").all()
        case _:
            queryset = Epoch.objects.order_by("position").filter(question__topic_id=topic_id)

    keyboard = [[InlineKeyboardButton.a(text="Все", callback_data="epoch_all")]] + [
        [InlineKeyboardButton.a(text=str(epoch), callback_data=f"epoch_{epoch.id}")] for epoch in queryset
    ]

    if topic_id:
        bot.sendMessage(chat_id, messages.SELECT_EPOCH,
                        reply_markup=InlineKeyboardMarkup.a(inline_keyboard=keyboard))
    else:
        bot.editMessageText(messages.SELECT_EPOCH, chat_id=chat_id, message_id=message_id,
                            reply_markup=InlineKeyboardMarkup.a(
                                inline_keyboard=keyboard
                            )
                            )
    state.set_name("theme_selected")


def send_topic_selection(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id, message_id = get_callback_message(update)

    epoch_id = state.get_memory().get("epoch")

    match epoch_id:
        case None | "all":
            queryset = Topic.objects.all()
        case _:
            queryset = Topic.objects.filter(question__epoch_id=epoch_id)

    keyboard = [
                   [InlineKeyboardButton.a(text="Все", callback_data="topic_all")]
               ] + [[InlineKeyboardButton.a(text=str(topic), callback_data=f"topic_{topic.id}")] for topic in
                    queryset]

    if epoch_id:
        bot.sendMessage(chat_id, messages.SELECT_TOPIC,
                        reply_markup=InlineKeyboardMarkup.a(inline_keyboard=keyboard))
    else:
        bot.editMessageText(messages.SELECT_TOPIC, chat_id=chat_id, message_id=message_id,
                            reply_markup=InlineKeyboardMarkup.a(
                                inline_keyboard=keyboard
                            )
                            )

    state.set_name("theme_selected")


@processor(state_manager, from_states="theme_selected", update_types=[update_types.CallbackQuery])
def handle_theme_selection(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id, message_id = get_callback_message(update)
    callback_data = update.get_callback_query().get_data()

    match callback_data:
        case callback_data if callback_data.startswith("epoch_"):
            epoch = callback_data.replace("epoch_", "")

            bot.editMessageText(messages.YOU_HAVE_EPOCH_SELECTED, chat_id=chat_id, message_id=message_id)

            if epoch != "all":
                epoch_id = int(epoch)
                epoch = Epoch.objects.get(id=epoch_id)
                send_with_image(bot, chat_id,
                                text=messages.SELECTED.format(title=str(epoch), description=epoch.description),
                                image=epoch.image,
                                parse_mode="HTML")

                state.set_memory(dict(epoch=epoch.id, **state.get_memory()))
            else:
                state.set_memory(dict(epoch=epoch, **state.get_memory()))

            if "topic" not in state.get_memory():
                send_topic_selection(bot, update, state)

        case callback_data if callback_data.startswith("topic_"):
            topic = callback_data.replace("topic_", "")

            bot.editMessageText(messages.YOU_HAVE_TOPIC_SELECTED, chat_id=chat_id, message_id=message_id)

            if topic != "all":
                topic_id = int(topic)
                topic = Topic.objects.get(id=topic_id)
                send_with_image(bot, chat_id,
                                text=messages.SELECTED.format(title=str(topic), description=topic.description),
                                image=topic.image,
                                parse_mode="HTML")

                state.set_memory(dict(topic=topic.id, **state.get_memory()))
            else:
                state.set_memory(dict(topic=topic, **state.get_memory()))

            if "epoch" not in state.get_memory():
                send_epoch_selection(bot, update, state)

    data = state.get_memory()
    if "epoch" in data and "topic" in data:
        bot.sendMessage(chat_id, "Лох", parse_mode="HTML")  # todo
