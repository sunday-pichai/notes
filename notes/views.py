from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Note, Profile
from .forms import ProfileForm
from django.db.models import Q


@login_required
def notes_list(request):
    if request.method == 'POST':
        Note.objects.create(
            user=request.user,
            title=request.POST.get('title', ''),
            content=request.POST.get('content'),
        )
        return redirect('/')

    notes = Note.objects.filter(
        user=request.user,
        archived=False,
        trashed=False
    )

    q = request.GET.get('q', '').strip()
    if q:
        notes = notes.filter(
            Q(title__icontains=q) | Q(content__icontains=q)
        )

    notes = notes.order_by('-updated_at')

    return render(request, 'notes/list.html', {'notes': notes})


@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)

    if request.method == 'POST':
        note.title = request.POST.get('title', '')
        note.content = request.POST.get('content')
        note.save()
        return redirect('/')

    return render(request, 'notes/edit.html', {'note': note})


@login_required
def archive_notes(request):
    notes = Note.objects.filter(
        user=request.user,
        archived=True,
        trashed=False
    ).order_by('-updated_at')
    return render(request, 'notes/list.html', {'notes': notes})


@login_required
def trash_notes(request):
    notes = Note.objects.filter(
        user=request.user,
        trashed=True
    ).order_by('-updated_at')
    return render(request, 'notes/trash.html', {'notes': notes})


@login_required
def archive_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.archived = True
    note.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def unarchive_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.archived = False
    note.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def trash_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.trashed = True
    note.archived = False
    note.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def restore_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.trashed = False
    note.save()
    return redirect('/trash/')


@login_required
def delete_forever(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    return redirect('/trash/')


@login_required
def empty_trash(request):
    if request.method == 'POST':
        Note.objects.filter(user=request.user, trashed=True).delete()
        messages.success(request, 'Trash emptied.')
    return redirect('/trash/')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('/')
    return render(request, 'notes/login.html')


def signup_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not username or not password:
            error = 'Username and password are required.'
        elif password != password2:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already taken.'
        else:
            user = User.objects.create_user(username=username, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            # create profile
            Profile.objects.get_or_create(user=user)
            # auto-login
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Account created and signed in.')
                return redirect('/')
            else:
                error = 'Unable to authenticate new user.'

    return render(request, 'notes/signup.html', {'error': error})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/') if request.GET.get('next') == '/' else redirect('login')
    # For safety, only allow POST logout. Redirect to profile page if accessed by GET.
    return redirect('/')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'notes/profile.html', {
        'form': form,
        'profile': profile,
    })