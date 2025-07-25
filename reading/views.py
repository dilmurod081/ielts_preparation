from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.forms import modelformset_factory

# Local app imports
from .models import ReadingTest, QuestionBlock, Question, UserAnswer
from .forms import ReadingTestForm, QuestionBlockForm, QuestionFormSet

# Import from other apps
from core.models import Profile


def reading_list(request):
    """
    Displays a list of all available reading tests.
    """
    tests = ReadingTest.objects.all().order_by('-created_at')
    context = {'reading_tests': tests}
    return render(request, 'reading/reading.html', context)


def reading_rules(request, test_id):
    """
    Displays the rules and instructions before a user starts a test.
    """
    test = get_object_or_404(ReadingTest, pk=test_id)
    context = {'test': test}
    return render(request, 'reading/rules_page.html', context)


def reading_test_detail(request, test_id):
    """
    Prepares and displays a single, complex reading test in a two-column layout.
    """
    test = get_object_or_404(ReadingTest, pk=test_id)

    passage_1_blocks, passage_2_blocks, passage_3_blocks = [], [], []
    blocks = test.question_blocks.prefetch_related('questions').order_by('passage_number')

    for block in blocks:
        block_data = {
            'instructions': block.instructions,
            'question_type': block.question_type,
            'options_list': [opt.strip() for opt in block.options_list.split(';')] if block.options_list else [],
            'questions': [],
            'prose_with_inputs': '',
        }

        block_questions = []
        for question in block.questions.all():
            question_data = {
                'id': question.id,
                'question_number': question.question_number,
                'question_text': question.question_text,
                'choices': [choice.strip() for choice in question.choices.split(';')] if question.choices else [],
            }
            block_questions.append(question_data)

        block_data['questions'] = block_questions

        if block.prose_content:
            prose_with_inputs = block.prose_content
            for q_data in block_questions:
                placeholder = f"{{{{{q_data['question_number']}}}}}"
                input_html = f'<input type="text" name="question_{q_data["id"]}" class="form-control-sm d-inline-block" style="width: 150px;">'
                prose_with_inputs = prose_with_inputs.replace(placeholder, input_html)
            block_data['prose_with_inputs'] = prose_with_inputs

        if block.passage_number == 1:
            passage_1_blocks.append(block_data)
        elif block.passage_number == 2:
            passage_2_blocks.append(block_data)
        elif block.passage_number == 3:
            passage_3_blocks.append(block_data)

    context = {
        'test': test,
        'passage_1_blocks': passage_1_blocks,
        'passage_2_blocks': passage_2_blocks,
        'passage_3_blocks': passage_3_blocks,
    }
    return render(request, 'reading/reading_test_detail.html', context)


@user_passes_test(lambda u: u.is_staff)
def add_reading_test(request):
    """
    Handles the dynamic form for creating a new test with its blocks and questions.
    """
    QuestionBlockFormSet = modelformset_factory(QuestionBlock, form=QuestionBlockForm, extra=1, can_delete=True)

    if request.method == 'POST':
        test_form = ReadingTestForm(request.POST)
        block_formset = QuestionBlockFormSet(request.POST, queryset=QuestionBlock.objects.none())

        if test_form.is_valid() and block_formset.is_valid():
            test_instance = test_form.save()
            blocks = block_formset.save(commit=False)
            for block in blocks:
                block.test = test_instance
                block.save()

            for block_form in block_formset.cleaned_data:
                if not block_form.get('DELETE', False):
                    block_instance = block_form['id']
                    question_formset = QuestionFormSet(request.POST, instance=block_instance,
                                                       prefix=f'questions-{block_instance.id}')
                    if question_formset.is_valid():
                        question_formset.save()
            return redirect('reading_list')
    else:
        test_form = ReadingTestForm()
        block_formset = QuestionBlockFormSet(queryset=QuestionBlock.objects.none())

    context = {
        'test_form': test_form,
        'block_formset': block_formset,
    }
    return render(request, 'reading/add_test_page.html', context)


@login_required
def submit_reading_test(request, test_id):
    """
    Processes all submitted answers for a reading test and shows the results page.
    """
    if request.method == 'POST':
        test = get_object_or_404(ReadingTest, pk=test_id)
        score, total_questions = 0, 0
        detailed_results = []

        for block in test.question_blocks.all():
            for question in block.questions.all():
                total_questions += 1
                submitted_answer = request.POST.get(f'question_{question.id}', '').strip()
                is_correct = submitted_answer.lower() == question.correct_answer.lower()
                if is_correct: score += 1

                UserAnswer.objects.create(
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

    return redirect('reading_test_detail', test_id=test_id)


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
