from django.contrib import admin

from olymphistory_bot.models import TelegramChat, TelegramUser, Epoch, Topic, Question, QuestionType, Note


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'type', 'epoch', 'topic')
    list_filter = ('type', 'epoch', 'topic')

    search_fields = ('text', 'answer')


@admin.register(QuestionType)
class QuestionTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass


@admin.register(Epoch)
class EpochAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramChat, TelegramUser)
class BaseAdmin(admin.ModelAdmin):
    pass

