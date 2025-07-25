import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Case, When, IntegerField
from collections import defaultdict
from django.utils import timezone
from django.db import transaction

# The forms are now imported from the new forms.py file
from .forms import AdminUserCreationForm, ProfileForm, AppealForm
from .models import Page, Profile
from reading.models import UserAnswer as ReadingUserAnswer
from listening.models import ListeningUserAnswer

# --- Your Telegram Bot Configuration ---
BOT_TOKEN = '7068733907:AAGb5ri9rn_w7coRlPLnUfoFIfap1w8L4vg'
ADMIN_ID = '6667155546'


@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def add_user(request):
    if request.method == 'POST':
        user_form = AdminUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = new_user
            profile.save()
            username = user_form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('home')
    else:
        user_form = AdminUserCreationForm()
        profile_form = ProfileForm()
    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'core/add_user.html', context)


def home(request):
    return render(request, 'core/home.html')


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    context = {'page': page}
    return render(request, 'core/page_detail.html', context)


def blocked_page(request):
    """
    This view displays the blocked page and sends the user's appeal to the admin via Telegram.
    If the user is no longer blocked, it redirects them to the homepage.
    """
    # Check if the user is authenticated and has a profile
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        # If the user is NOT blocked, redirect them away from this page.
        if not request.user.profile.is_blocked:
            messages.info(request, "Your account has been unblocked. Welcome back!")
            return redirect('home')

    if request.method == 'POST':
        form = AppealForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            user = request.user

            # Prepare the message to send to the Telegram admin
            message_to_admin = (
                f"Unblock Appeal from User: {user.username} (ID: {user.id})\n\n"
                f"Message: {user_message}\n\n"
                f"Reply with 'yes {user.id}' to unblock or 'no {user.id}' to keep blocked."
            )

            # Send the message using the Telegram Bot API
            send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': ADMIN_ID,
                'text': message_to_admin
            }
            try:
                requests.post(send_url, json=payload)
                messages.success(request, "Your appeal has been sent to the administrator.")
            except requests.exceptions.RequestException as e:
                messages.error(request, "There was an error sending your appeal. Please try again later.")

            return redirect('blocked_page')
    else:
        form = AppealForm()

    return render(request, 'core/blocked_page.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def user_statistics(request):
    users = User.objects.filter(is_staff=False).prefetch_related('profile')
    user_data = []
    for user in users:
        reading_answers = ReadingUserAnswer.objects.filter(user=user)
        reading_tests_taken = reading_answers.values('question__block__test').distinct().count()
        reading_score_avg = reading_answers.aggregate(
            avg_score=Avg(Case(When(is_correct=True, then=1), default=0, output_field=IntegerField())))['avg_score']
        reading_percent = round(reading_score_avg * 100) if reading_score_avg is not None else 0
        listening_answers = ListeningUserAnswer.objects.filter(user=user)
        listening_tests_taken = listening_answers.values('question__group__part__test').distinct().count()
        listening_score_avg = listening_answers.aggregate(
            avg_score=Avg(Case(When(is_correct=True, then=1), default=0, output_field=IntegerField())))['avg_score']
        listening_percent = round(listening_score_avg * 100) if listening_score_avg is not None else 0
        user_data.append({
            'id': user.id, 'username': user.username,
            'is_blocked': user.profile.is_blocked if hasattr(user, 'profile') else False,
            'reading_tests': reading_tests_taken, 'reading_avg': reading_percent,
            'listening_tests': listening_tests_taken, 'listening_avg': listening_percent,
        })
    context = {'user_data': user_data}
    return render(request, 'core/user_statistics.html', context)


@user_passes_test(lambda u: u.is_staff)
def user_detail(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    reading_answers = ReadingUserAnswer.objects.filter(user=target_user).select_related(
        'question__block__test').order_by('question__block__test_id', 'question__question_number')
    reading_tests_data = defaultdict(lambda: {'correct': 0, 'total': 0, 'answers': []})
    for answer in reading_answers:
        test = answer.question.block.test
        reading_tests_data[test]['answers'].append(answer)
        reading_tests_data[test]['total'] += 1
        if answer.is_correct:
            reading_tests_data[test]['correct'] += 1
    listening_answers = ListeningUserAnswer.objects.filter(user=target_user).select_related(
        'question__group__part__test').order_by('question__group__part__test_id', 'question__question_number')
    listening_tests_data = defaultdict(lambda: {'correct': 0, 'total': 0, 'answers': []})
    for answer in listening_answers:
        test = answer.question.group.part.test
        listening_tests_data[test]['answers'].append(answer)
        listening_tests_data[test]['total'] += 1
        if answer.is_correct:
            listening_tests_data[test]['correct'] += 1
    context = {
        'target_user': target_user,
        'reading_tests_data': dict(reading_tests_data),
        'listening_tests_data': dict(listening_tests_data),
    }
    return render(request, 'core/user_detail.html', context)
