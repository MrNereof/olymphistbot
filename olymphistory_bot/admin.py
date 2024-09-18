from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import admin

from olymphistory_bot.models import TelegramChat, TelegramUser, Epoch, Topic, Question, QuestionType, Note, Attempt, Leader
from olymphistory_bot.bot import bot
from olymphistory_bot.forms import BroadcastForm


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    list_filter = ('user', )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'type', 'epoch', 'topic', 'leader', 'answer')
    list_filter = ('type', 'epoch', 'topic', 'leader', 'note')

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


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    actions = ['broadcast']

    def broadcast(self, request, queryset):
        """ Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        ids = queryset.values_list('id', flat=True).distinct().iterator()
        if 'apply' in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            for user in TelegramUser.objects.filter(id__in=ids):
                bot.sendMessage(user.telegram_id, broadcast_message_text, parse_mode="HTML")
            self.message_user(request, f"Just broadcasted to {len(queryset)} users")

            return HttpResponseRedirect(request.get_full_path())
        else:
            form = BroadcastForm(initial={'_selected_action': ids})
            return render(
                request, "admin/broadcast_message.html", {'form': form, 'title': 'Broadcast message'}
            )


@admin.register(TelegramChat)
class BaseAdmin(admin.ModelAdmin):
    pass

