from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'archived', 'updated_at')
    list_filter = ('archived', 'trashed')