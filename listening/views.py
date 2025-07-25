from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

# Local app imports
from .models import ListeningTest, ListeningUserAnswer
from .forms import ListeningTestForm

# Import from other apps
from core.models import Profile


def listening_list(request):
    """
    Displays a list of all available listening tests.
    """
    tests = ListeningTest.objects.all().order_by('-created_at')
    context = {'listening_tests': tests}
    return render(request, 'listening/listening.html', context)


def listening_rules(request, test_id):
    """
    Displays the rules and instructions before a user starts a listening test.
    """
    test = get_object_or_404(ListeningTest, pk=test_id)
    context = {'test': test}
    return render(request, 'listening/rules_page.html', context)


def listening_test_detail(request, test_id):
    """
    Prepares and displays a single, complex listening test for the full-screen view.
    """
    test = get_object_or_404(ListeningTest, pk=test_id)
    processed_parts = []
    parts = test.parts.prefetch_related('question_groups__questions')

    for part in parts:
        processed_groups = []
        for group in part.question_groups.all():
            group_data = {
                'question_range': group.question_range,
                'group_type': group.group_type,
                'instructions': group.instructions,
                'image_url': group.image.url if group.image else None,
                'options_list': [opt.strip() for opt in group.options_list.split(';')] if group.options_list else [],
                'questions': [],
            }
            group_questions = []
            for question in group.questions.all():
                question_data = {
                    'id': question.id,
                    'question_number': question.question_number,
                    'question_text': question.question_text,
                    'choices': [choice.strip() for choice in question.choices.split(';')] if question.choices else [],
                }
                group_questions.append(question_data)
            group_data['questions'] = group_questions

            if group.group_type == 'note_completion' and group.prose_content:
                prose_with_inputs = group.prose_content
                for q_data in group_questions:
                    placeholder = f"{{{{{q_data['question_number']}}}}}"
                    input_html = f'<input type="text" name="question_{q_data["id"]}" class="form-control-sm d-inline-block" style="width: 150px;">'
                    prose_with_inputs = prose_with_inputs.replace(placeholder, input_html)
                group_data['prose_with_inputs'] = prose_with_inputs
            processed_groups.append(group_data)

        processed_parts.append({
            'part_number': part.part_number,
            'audio_file_url': part.audio_file.url,
            'groups': processed_groups,
        })

    context = {'test': test, 'parts_data': processed_parts}
    return render(request, 'listening/listening_test_detail.html', context)


@user_passes_test(lambda u: u.is_staff)
def add_listening_test(request):
    """
    Allows an admin to create the main shell for a new ListeningTest.
    """
    if request.method == 'POST':
        form = ListeningTestForm(request.POST)
        if form.is_valid():
            new_test = form.save()
            return redirect(f'/admin/listening/listeningpart/add/?test={new_test.id}')
    else:
        form = ListeningTestForm()
    return render(request, 'listening/add_test.html', {'form': form})


@login_required
def submit_listening_test(request, test_id):
    """
    Processes all submitted answers for a listening test and shows the results page.
    """
    if request.method == 'POST':
        test = get_object_or_404(ListeningTest, pk=test_id)
        score, total_questions = 0, 0
        detailed_results = []

        for part in test.parts.all():
            for group in part.question_groups.all():
                for question in group.questions.all():
                    total_questions += 1
                    submitted_answer = request.POST.get(f'question_{question.id}', '').strip()
                    is_correct = submitted_answer.lower() == question.correct_answer.lower()
                    if is_correct: score += 1

                    ListeningUserAnswer.objects.create(
                        user=request.user, question=question,
                        submitted_answer=submitted_answer, is_correct=is_correct
                    )
                    detailed_results.append({
                        'question_number': question.question_number,
                        'question_text': question.question_text,
                        'submitted_answer': submitted_answer,
                        'correct_answer': question.correct_answer,
                        'is_correct': is_correct,
                    })
        context = {
            'test': test, 'score': score,
            'total_questions': total_questions, 'detailed_results': detailed_results,
        }
        return render(request, 'results.html', context)
    return redirect('listening_test_detail', test_id=test_id)


@login_required
def block_user_view(request):
    """
    This view is called by JavaScript to block a user.
    """
    if request.method == 'POST':
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.is_blocked = True
        profile.save()
        return JsonResponse({'status': 'success', 'message': 'User has been blocked.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)
