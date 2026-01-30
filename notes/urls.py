from django.urls import path
from .views import (
    notes_list, login_view, edit_note,
    archive_notes, archive_note, unarchive_note,
    trash_note, restore_note, delete_forever, trash_notes,
    profile_view, signup_view, logout_view, empty_trash,
)

urlpatterns = [
    path('', notes_list, name='notes'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('edit/<int:note_id>/', edit_note, name='edit_note'),
    path('archive/', archive_notes, name='archive'),
    path('archive-note/<int:note_id>/', archive_note, name='archive_note'),
    path('unarchive-note/<int:note_id>/', unarchive_note, name='unarchive_note'),
    path('trash-note/<int:note_id>/', trash_note, name='trash_note'),
    path('restore-note/<int:note_id>/', restore_note, name='restore_note'),
    path('delete-forever/<int:note_id>/', delete_forever, name='delete_forever'),
    path('trash/', trash_notes, name='trash'),
    path('empty-trash/', empty_trash, name='empty_trash'),
    path('profile/', profile_view, name='profile'),
]