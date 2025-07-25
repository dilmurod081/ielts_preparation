from django.db import models
from django.conf import settings

class ReadingTest(models.Model):
    title = models.CharField(max_length=200)
    passage_1 = models.TextField()
    passage_2 = models.TextField()
    passage_3 = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class QuestionBlock(models.Model):
    QUESTION_TYPES = [
        ('short_answer', 'Short Answer / Completion'),
        ('multiple_choice', 'Multiple Choice'),
        ('true_false_not_given', 'True/False/Not Given'),
        ('matching', 'Matching (e.g., Headings)'),
    ]
    test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE, related_name='question_blocks')
    passage_number = models.IntegerField(choices=[(1, 'Passage 1'), (2, 'Passage 2'), (3, 'Passage 3')], default=1)
    instructions = models.TextField(help_text="Instructions for this group of questions.")
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    options_list = models.TextField(blank=True, help_text="For Matching questions, provide the list of options here, separated by semicolons (;).")
    prose_content = models.TextField(blank=True, help_text="For note completion, use {{num}} for blanks. e.g., 'Area: {{1}} hectares'")


    def __str__(self):
        return f"Block for {self.test.title} ({self.get_question_type_display()})"

class Question(models.Model):
    block = models.ForeignKey(QuestionBlock, on_delete=models.CASCADE, related_name='questions')
    question_number = models.PositiveIntegerField()
    question_text = models.CharField(max_length=500, blank=True, help_text="The question itself, or the item to be matched (e.g., 'Paragraph A').")
    choices = models.TextField(blank=True, help_text="For Multiple Choice questions only, separate choices with a semicolon (;).")
    correct_answer = models.CharField(max_length=200)

    class Meta:
        ordering = ['question_number']

    def __str__(self):
        return f"Q{self.question_number}"

class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submitted_answer = models.CharField(max_length=200, blank=True)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s answer to Q{self.question.question_number}"