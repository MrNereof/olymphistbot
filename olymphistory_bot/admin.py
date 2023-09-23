from django.contrib import admin

from olymphistory_bot.models import TelegramChat, TelegramUser, TelegramState


@admin.register(TelegramChat, TelegramUser, TelegramState)
class BaseAdmin(admin.ModelAdmin):
    pass

