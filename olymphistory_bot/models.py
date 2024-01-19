from django.db import models
from django.db.models import CASCADE

from django_tgbot.models import AbstractTelegramUser, AbstractTelegramChat, AbstractTelegramState


class TelegramUser(AbstractTelegramUser):
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class TelegramChat(AbstractTelegramChat):
    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"


class TelegramState(AbstractTelegramState):
    telegram_user = models.ForeignKey(TelegramUser, related_name='telegram_states', on_delete=CASCADE, blank=True,
                                      null=True)
    telegram_chat = models.ForeignKey(TelegramChat, related_name='telegram_states', on_delete=CASCADE, blank=True,
                                      null=True)

    class Meta:
        unique_together = ('telegram_user', 'telegram_chat')


class Epoch(models.Model):
    class Meta:
        verbose_name = "Эпоха"
        verbose_name_plural = "Эпохи"

    start_year = models.CharField(max_length=25, blank=True, null=True, verbose_name="Начало")
    end_year = models.CharField(max_length=25, blank=True, null=True, verbose_name="Конец")

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="epochs", blank=True, null=True, verbose_name="Картинка")

    position = models.IntegerField(null=True, blank=True, verbose_name="Позиция")

    def __str__(self):
        start = self.start_year if self.start_year is not None else "..."
        end = self.end_year if self.end_year is not None else "..."

        if start == end:
            return self.name
        return f"{self.name} ({start} — {end})"


class Topic(models.Model):
    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="topics", blank=True, null=True, verbose_name="Картинка")

    def __str__(self):
        return self.name


class Leader(models.Model):
    class Meta:
        verbose_name = "Правитель"
        verbose_name_plural = "Правители"

    start_year = models.CharField(max_length=25, blank=True, null=True, verbose_name="Начало")
    end_year = models.CharField(max_length=25, blank=True, null=True, verbose_name="Конец")

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="epochs", blank=True, null=True, verbose_name="Картинка")

    position = models.IntegerField(null=True, blank=True, verbose_name="Позиция")

    def __str__(self):
        start = self.start_year if self.start_year is not None else "..."
        end = self.end_year if self.end_year is not None else "..."

        if start == end:
            return self.name
        return f"{self.name} ({start} — {end})"


class QuestionType(models.Model):
    class Meta:
        verbose_name = "Тип вопроса"
        verbose_name_plural = "Типы вопроса"

    name = models.CharField(max_length=200, verbose_name="Название")

    def __str__(self):
        return self.name


class Note(models.Model):
    class Meta:
        verbose_name = "Шпаргалка"
        verbose_name_plural = "Шпаргалки"

    image = models.ImageField(upload_to="notes", blank=True, null=True, verbose_name="Картинка")
    text = models.TextField(verbose_name="Текст")

    def __str__(self):
        return self.text.splitlines()[0]


class Question(models.Model):
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, verbose_name="Тип")
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Тема")
    epoch = models.ForeignKey(Epoch, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Эпоха")
    leader = models.ForeignKey(Leader, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Эпоха")

    image = models.ImageField(upload_to="questions", blank=True, null=True, verbose_name="Картинка")
    text = models.TextField(verbose_name="Текст вопроса")

    answer = models.CharField(max_length=250, verbose_name="Ответ")
    note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Заметка")

    def __str__(self):
        return f"{self.text} - {self.epoch} | {self.topic}"


class Attempt(models.Model):
    class Meta:
        verbose_name = "Попытка"
        verbose_name_plural = "Попытка"

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    questions = models.ManyToManyField(Question, through="UserAnswer", verbose_name="Вопросы")

    def __str__(self):
        return f"{self.user} (№{self.id})"


class UserAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    answer = models.CharField(max_length=250, verbose_name="Ответ")
    right = models.BooleanField(default=False, blank=True)
