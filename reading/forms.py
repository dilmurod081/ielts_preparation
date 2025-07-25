from django import forms
from .models import ReadingTest, QuestionBlock, Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_number', 'question_text', 'choices', 'correct_answer']
        widgets = {
            'question_number': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Q Number'}),
            'question_text': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Question Text (e.g., Paragraph A)'}),
            'choices': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Choices for MCQs (use ; to separate)'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Correct Answer'}),
        }

class QuestionBlockForm(forms.ModelForm):
    class Meta:
        model = QuestionBlock
        fields = ['passage_number', 'instructions', 'question_type', 'options_list', 'prose_content']
        widgets = {
            'passage_number': forms.Select(attrs={'class': 'form-select mb-2'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control mb-2', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-select mb-2'}),
            'options_list': forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Options for Matching (use ; to separate)'}),
            'prose_content': forms.Textarea(attrs={'class': 'form-control mb-2', 'rows': 4, 'placeholder': 'Prose for Note Completion (use {{num}} for blanks)'}),
        }

# This formset will manage the collection of Questions within a Block
QuestionFormSet = forms.inlineformset_factory(
    QuestionBlock,
    Question,
    form=QuestionForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True,
    # A prefix is needed for the nested formsets
    # prefix='questions'
)

class ReadingTestForm(forms.ModelForm):
    class Meta:
        model = ReadingTest
        fields = ['title', 'passage_1', 'passage_2', 'passage_3']
