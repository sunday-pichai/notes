from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Note


class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass123'
    
    def test_signup_creates_user(self):
        self.client.post(reverse('signup'), {
            'username': self.username,
            'password': self.password,
            'password2': self.password,
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertTrue(User.objects.filter(username=self.username).exists())
    
    def test_signup_password_mismatch(self):
        self.client.post(reverse('signup'), {
            'username': self.username,
            'password': self.password,
            'password2': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertFalse(User.objects.filter(username=self.username).exists())
    
    def test_signup_duplicate_username(self):
        User.objects.create_user(username=self.username, password=self.password)
        self.client.post(reverse('signup'), {
            'username': self.username,
            'password': self.password,
            'password2': self.password,
            'first_name': 'Test2',
            'last_name': 'User2'
        })
        self.assertEqual(User.objects.filter(username=self.username).count(), 1)
    
    def test_login_with_valid_credentials(self):
        User.objects.create_user(username=self.username, password=self.password)
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_with_invalid_credentials(self):
        User.objects.create_user(username=self.username, password=self.password)
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpass'
        })
        self.assertIn(response.status_code, [200, 302])
    
    def test_logout(self):
        user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)


class NotesCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_create_note(self):
        self.client.post(reverse('notes'), {
            'title': 'Test Note',
            'content': 'This is a test note'
        })
        note = Note.objects.get(title='Test Note')
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.content, 'This is a test note')
    
    def test_create_note_blank_title(self):
        self.client.post(reverse('notes'), {
            'title': '',
            'content': 'Note without title'
        })
        note = Note.objects.get(content='Note without title')
        self.assertEqual(note.title, '')
    
    def test_notes_list_shows_only_user_notes(self):
        Note.objects.create(user=self.user, title='My Note', content='My content')
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        Note.objects.create(user=other_user, title='Other Note', content='Other content')
        
        response = self.client.get(reverse('notes'))
        notes = response.context['notes']
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0].title, 'My Note')
    
    def test_edit_note(self):
        note = Note.objects.create(user=self.user, title='Original', content='Original content')
        self.client.post(reverse('edit_note', args=[note.id]), {
            'title': 'Updated',
            'content': 'Updated content'
        })
        note.refresh_from_db()
        self.assertEqual(note.title, 'Updated')
        self.assertEqual(note.content, 'Updated content')
    
    def test_cannot_edit_other_users_note(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        note = Note.objects.create(user=other_user, title='Other Note', content='Other content')
        
        self.client.post(reverse('edit_note', args=[note.id]), {
            'title': 'Hacked',
            'content': 'Hacked content'
        })
        note.refresh_from_db()
        self.assertEqual(note.title, 'Other Note')
        self.assertEqual(note.content, 'Other content')
    
    def test_delete_note_permanently(self):
        note = Note.objects.create(user=self.user, title='To Delete', content='Content', trashed=True)
        note_id = note.id
        self.client.get(reverse('delete_forever', args=[note.id]))
        self.assertFalse(Note.objects.filter(id=note_id).exists())


class ArchiveTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_archive_note(self):
        note = Note.objects.create(user=self.user, title='To Archive', content='Content')
        self.client.get(reverse('archive_note', args=[note.id]))
        note.refresh_from_db()
        self.assertTrue(note.archived)
    
    def test_unarchive_note(self):
        note = Note.objects.create(user=self.user, title='Archived', content='Content', archived=True)
        self.client.get(reverse('unarchive_note', args=[note.id]))
        note.refresh_from_db()
        self.assertFalse(note.archived)
    
    def test_archived_notes_not_in_list(self):
        Note.objects.create(user=self.user, title='Active', content='Active')
        Note.objects.create(user=self.user, title='Archived', content='Archived', archived=True)
        
        response = self.client.get(reverse('notes'))
        notes = response.context['notes']
        
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0].title, 'Active')
    
    def test_view_archived_notes(self):
        Note.objects.create(user=self.user, title='Archived 1', content='Content', archived=True)
        Note.objects.create(user=self.user, title='Archived 2', content='Content', archived=True)
        Note.objects.create(user=self.user, title='Active', content='Content', archived=False)
        
        response = self.client.get(reverse('archive'))
        notes = response.context['notes']
        
        self.assertEqual(notes.count(), 2)
        for note in notes:
            self.assertTrue(note.archived)


class TrashTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_trash_note(self):
        note = Note.objects.create(user=self.user, title='To Trash', content='Content')
        self.client.get(reverse('trash_note', args=[note.id]))
        note.refresh_from_db()
        self.assertTrue(note.trashed)
    
    def test_trash_unarchives_note(self):
        note = Note.objects.create(user=self.user, title='Archived', content='Content', archived=True)
        self.client.get(reverse('trash_note', args=[note.id]))
        note.refresh_from_db()
        self.assertTrue(note.trashed)
        self.assertFalse(note.archived)
    
    def test_restore_note(self):
        note = Note.objects.create(user=self.user, title='Trashed', content='Content', trashed=True)
        self.client.get(reverse('restore_note', args=[note.id]))
        note.refresh_from_db()
        self.assertFalse(note.trashed)
    
    def test_view_trash(self):
        Note.objects.create(user=self.user, title='Trashed', content='Content', trashed=True)
        Note.objects.create(user=self.user, title='Active', content='Content', trashed=False)
        
        response = self.client.get(reverse('trash'))
        notes = response.context['notes']
        
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0].title, 'Trashed')
    
    def test_empty_trash(self):
        Note.objects.create(user=self.user, title='Trashed 1', content='Content', trashed=True)
        Note.objects.create(user=self.user, title='Trashed 2', content='Content', trashed=True)
        
        self.client.post(reverse('empty_trash'))
        self.assertEqual(Note.objects.filter(user=self.user, trashed=True).count(), 0)


class SearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_search_by_title(self):
        Note.objects.create(user=self.user, title='Python Tutorial', content='Content 1')
        Note.objects.create(user=self.user, title='Django Guide', content='Content 2')
        
        response = self.client.get(reverse('notes'), {'q': 'Python'})
        notes = response.context['notes']
        
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0].title, 'Python Tutorial')
    
    def test_search_by_content(self):
        Note.objects.create(user=self.user, title='Note 1', content='Python is great')
        Note.objects.create(user=self.user, title='Note 2', content='JavaScript is cool')
        
        response = self.client.get(reverse('notes'), {'q': 'Python'})
        notes = response.context['notes']
        
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes[0].content, 'Python is great')
    
    def test_search_case_insensitive(self):
        Note.objects.create(user=self.user, title='PYTHON', content='Content')
        response = self.client.get(reverse('notes'), {'q': 'python'})
        notes = response.context['notes']
        self.assertEqual(notes.count(), 1)
    
    def test_search_no_results(self):
        Note.objects.create(user=self.user, title='Test Note', content='Content')
        response = self.client.get(reverse('notes'), {'q': 'nonexistent'})
        notes = response.context['notes']
        self.assertEqual(notes.count(), 0)


class ProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_view_profile(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_update_profile(self):
        self.client.post(reverse('profile'), {
            'first_name': 'John',
            'last_name': 'Doe'
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')


class AuthenticationRequiredTests(TestCase):
    def test_notes_list_requires_login(self):
        response = self.client.get(reverse('notes'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_edit_note_requires_login(self):
        response = self.client.get(reverse('edit_note', args=[1]))
        self.assertEqual(response.status_code, 302)
    
    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
