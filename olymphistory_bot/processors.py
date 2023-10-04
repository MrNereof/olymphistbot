import random

from django_tgbot.decorators import processor
from django_tgbot.state_manager import message_types, update_types, state_types
from django_tgbot.types.inlinekeyboardbutton import InlineKeyboardButton
from django_tgbot.types.inlinekeyboardmarkup import InlineKeyboardMarkup
from django_tgbot.types.keyboardbutton import KeyboardButton
from django_tgbot.types.replykeyboardmarkup import ReplyKeyboardMarkup
from django_tgbot.types.replykeyboardremove import ReplyKeyboardRemove
from django_tgbot.types.update import Update

from olymphistory_bot import messages
from .bot import TelegramBot
from .bot import state_manager
from .models import TelegramState, Epoch, Topic, Question, Attempt, UserAnswer
from .utils import get_callback_message, send_with_image, get_questions


@processor(state_manager, update_types=update_types.Message,
           message_types=message_types.Text, from_states=state_types.All)
def message_processor(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id = update.get_chat().get_id()
    text = str(update.get_message().get_text())

    match text:
        case "/start":
            send_start(bot, chat_id, state)


@processor(state_manager, update_types=[update_types.CallbackQuery], from_states=state_types.All)
def restart(bot: TelegramBot, update: Update, state: TelegramState):
    callback_data = update.get_callback_query().get_data()
    if callback_data == "restart":
        chat_id, _ = get_callback_message(update)

        send_start(bot, chat_id, state)


def send_start(bot: TelegramBot, chat_id, state: TelegramState):
    bot.sendMessage(chat_id, text=messages.START_MESSAGE,
                    reply_markup=InlineKeyboardMarkup.a(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton.a(messages.TRAINING_BUTTON, callback_data='training')
                            ]
                        ]
                    ), parse_mode="HTML")
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
                        ), parse_mode="HTML"
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
            ids = Epoch.objects.filter(question__topic_id=topic_id).values_list("id", flat=True).distinct()
            queryset = Epoch.objects.filter(id__in=ids)

    keyboard = [[InlineKeyboardButton.a(text="Все", callback_data="epoch_all")]] + [
        [InlineKeyboardButton.a(text=str(epoch), callback_data=f"epoch_{epoch.id}")] for epoch in queryset
    ]

    if topic_id:
        bot.sendMessage(chat_id, messages.SELECT_EPOCH,
                        reply_markup=InlineKeyboardMarkup.a(inline_keyboard=keyboard), parse_mode="HTML")
    else:
        bot.editMessageText(messages.SELECT_EPOCH, chat_id=chat_id, message_id=message_id,
                            reply_markup=InlineKeyboardMarkup.a(
                                inline_keyboard=keyboard
                            ), parse_mode="HTML"
                            )
    state.set_name("theme_selected")


def send_topic_selection(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id, message_id = get_callback_message(update)

    epoch_id = state.get_memory().get("epoch")

    match epoch_id:
        case None | "all":
            queryset = Topic.objects.all()
        case _:
            ids = Topic.objects.filter(question__epoch_id=epoch_id).values_list("id", flat=True).distinct()
            queryset = Topic.objects.filter(id__in=ids)

    keyboard = [
                   [InlineKeyboardButton.a(text="Все", callback_data="topic_all")]
               ] + [[InlineKeyboardButton.a(text=str(topic), callback_data=f"topic_{topic.id}")] for topic in
                    queryset]

    if epoch_id:
        bot.sendMessage(chat_id, messages.SELECT_TOPIC,
                        reply_markup=InlineKeyboardMarkup.a(inline_keyboard=keyboard), parse_mode="HTML")
    else:
        bot.editMessageText(messages.SELECT_TOPIC, chat_id=chat_id, message_id=message_id,
                            reply_markup=InlineKeyboardMarkup.a(
                                inline_keyboard=keyboard
                            ), parse_mode="HTML"
                            )

    state.set_name("theme_selected")


@processor(state_manager, from_states="theme_selected", update_types=[update_types.CallbackQuery])
def handle_theme_selection(bot: TelegramBot, update: Update, state: TelegramState):
    callback_data = update.get_callback_query().get_data()

    match callback_data:
        case callback_data if callback_data.startswith("epoch_"):
            epoch = callback_data.replace("epoch_", "")

            send_selected(bot, update, state, epoch, messages.YOU_HAVE_EPOCH_SELECTED, Epoch, "epoch")

            if "topic" not in state.get_memory():
                send_topic_selection(bot, update, state)

        case callback_data if callback_data.startswith("topic_"):
            topic = callback_data.replace("topic_", "")

            send_selected(bot, update, state, topic, messages.YOU_HAVE_TOPIC_SELECTED, Topic, "topic")

            if "epoch" not in state.get_memory():
                send_epoch_selection(bot, update, state)

    data = state.get_memory()
    if "epoch" in data and "topic" in data:
        send_level_selection(bot, update, state)


def send_selected(bot: TelegramBot, update: Update, state: TelegramState, callback_data, message, model, name):
    chat_id, message_id = get_callback_message(update)

    bot.editMessageText(message, chat_id=chat_id, message_id=message_id, parse_mode="HTML")

    if callback_data != "all":
        obj_id = int(callback_data)
        obj = model.objects.get(id=obj_id)
        send_with_image(bot, chat_id,
                        text=messages.SELECTED.format(title=str(obj), description=obj.description),
                        image=obj.image,
                        parse_mode="HTML")

        state.update_memory({name: obj_id})
    else:
        bot.sendMessage(chat_id, messages.SELECTED_ALL, parse_mode="HTML")

        state.update_memory({name: callback_data})


def send_level_selection(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id, _ = get_callback_message(update)
    bot.sendMessage(chat_id, messages.LEVEL_SELECT,
                    reply_markup=ReplyKeyboardMarkup.a(
                        keyboard=[[KeyboardButton.a(messages.LEVEL_EASY), KeyboardButton.a(messages.LEVEL_HARD)]],
                        one_time_keyboard=True), parse_mode="HTML")

    state.set_name("level_selection")


@processor(state_manager, update_types=update_types.Message,
           message_types=message_types.Text, from_states="level_selection")
def level_selection(bot: TelegramBot, update: Update, state: TelegramState):
    text = update.get_message().get_text()

    if text == "/start":
        return

    tips = text != messages.LEVEL_HARD

    count = get_questions(state).count()
    bot.sendMessage(update.get_chat().get_id(), messages.NUMBER_OF_QUESTION.format(count=count),
                    reply_markup=ReplyKeyboardRemove.a(remove_keyboard=True), parse_mode="HTML")

    state.update_memory({"tips": tips})
    state.set_name("num_of_question")


@processor(state_manager, update_types=update_types.Message,
           message_types=message_types.Text, from_states="num_of_question")
def num_of_question(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id = update.get_chat().get_id()
    text = update.get_message().get_text()

    if text == "/start":
        return

    if not text.isdigit():
        bot.sendMessage(chat_id, messages.INVALID_NUMBER, parse_mode="HTML")
        level_selection(bot, update, state)
        return

    count = get_questions(state).count()
    if int(text) > count:
        bot.sendMessage(chat_id, messages.MAX_NUMBER.format(count=count), parse_mode="HTML")
        level_selection(bot, update, state)
        return

    attempt = Attempt.objects.create(user=state.telegram_user)
    state.update_memory({"num": int(text), "already": 0, "attempt": attempt.id, "questions": []})

    send_question(bot, update, state)


def send_question(bot: TelegramBot, update: Update, state: TelegramState):
    data = state.get_memory()

    attempt = Attempt.objects.get(id=data["attempt"])
    question = get_questions(state).exclude(attempt=attempt).order_by("?").first()

    keyboard = []
    if data['tips']:
        keyboard = [[KeyboardButton.a(question.answer)]]
        for q in get_questions(state).order_by('?').filter(type=question.type).exclude(id=question.id, answer=question.answer)[:2]:
            keyboard.append([KeyboardButton.a(q.answer)])
        random.shuffle(keyboard)

    send_with_image(bot, update.get_chat().get_id(),
                    text=messages.QUESTION.format(pos=data["already"] + 1, count=data["num"], text=question.text),
                    image=question.image,
                    reply_markup=ReplyKeyboardMarkup.a(keyboard=keyboard, resize_keyboard=True),
                    parse_mode="HTML")

    state.update_memory({"question": question.id})
    state.set_name("question")


@processor(state_manager, update_types=update_types.Message,
           message_types=message_types.Text, from_states="question")
def handle_question(bot: TelegramBot, update: Update, state: TelegramState):
    chat_id = update.get_chat().get_id()
    text = update.get_message().get_text()

    if text == "/start":
        return

    state.update_memory({"already": state.get_memory()["already"] + 1})
    data = state.get_memory()

    attempt = Attempt.objects.get(id=data["attempt"])
    question = Question.objects.get(id=data["question"])

    answer = UserAnswer(question=question, attempt=attempt, answer=text)

    remove = dict(reply_markup=ReplyKeyboardRemove.a(remove_keyboard=True)) if data["already"] >= data["num"] else {}

    if text.lower() == question.answer.lower():
        answer.right = True
        bot.sendMessage(chat_id, messages.ANSWER_RIGHT, parse_mode="HTML", **remove)
    else:
        bot.sendMessage(chat_id, messages.ANSWER_FALSE.format(answer=question.answer), parse_mode="HTML", **remove)

    answer.save()

    if data["num"] > data["already"]:
        send_question(bot, update, state)
    else:
        right = UserAnswer.objects.filter(attempt=attempt, right=True).count()
        count = UserAnswer.objects.filter(attempt=attempt).count()

        bot.sendMessage(chat_id, messages.RESULT_ATTEMPT.format(right=right, count=count),
                        reply_markup=InlineKeyboardMarkup.a(inline_keyboard=[
                            [InlineKeyboardButton.a(text=messages.RESTART_BUTTON, callback_data="training")]]),
                        parse_mode="HTML")
        state.reset_memory()
        state.set_name("started")
