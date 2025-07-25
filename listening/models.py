from django.db import models
from django.conf import settings


# The main container for the entire test
class ListeningTest(models.Model):
    title = models.CharField(max_length=200, help_text="e.g., 'IELTS Listening Test 1'")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Represents one of the 4 parts of the test
class ListeningPart(models.Model):
    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE, related_name='parts')
    part_number = models.PositiveIntegerField()
    audio_file = models.FileField(upload_to='listening_parts/')

    class Meta:
        ordering = ['part_number']

    def __str__(self):
        return f"{self.test.title} - Part {self.part_number}"


# Represents a group of questions, e.g., Questions 1-10 or 11-15
class QuestionGroup(models.Model):
    GROUP_TYPES = [
        ('note_completion', 'Note/Form/Sentence Completion'),
        ('multiple_choice', 'Multiple Choice'),
        ('map_labelling', 'Map/Diagram Labelling'),
        ('matching', 'Matching'),
    ]
    part = models.ForeignKey(ListeningPart, on_delete=models.CASCADE, related_name='question_groups')
    question_range = models.CharField(max_length=50, help_text="e.g., 'Questions 1-10'")
    group_type = models.CharField(max_length=50, choices=GROUP_TYPES)
    instructions = models.TextField()
    image = models.ImageField(upload_to='listening_images/', blank=True, null=True,
                              help_text="Upload a map or diagram if needed.")

    # For Note Completion: the text with placeholders like {{1}}, {{2}} for the blanks.
    prose_content = models.TextField(blank=True,
                                     help_text="For note completion, use {{num}} for blanks. e.g., 'Area: {{1}} hectares'")

    # For Matching: the list of options to match from.
    options_list = models.TextField(blank=True, help_text="For matching, list options separated by semicolons (;).")

    def __str__(self):
        return f"{self.part} - {self.question_range}"


# Represents a single question item
class Question(models.Model):
    group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE, related_name='questions')
    question_number = models.PositiveIntegerField(unique=True)
    question_text = models.CharField(max_length=500, blank=True, help_text="For MCQs or Matching items.")
    choices = models.TextField(blank=True, help_text="For Multiple Choice, separate options with a semicolon (;).")
    correct_answer = models.CharField(max_length=200)

    class Meta:
        ordering = ['question_number']

    def __str__(self):
        return f"Q{self.question_number}"


# UserAnswer model needs to be updated to point to the new Question model
class ListeningUserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submitted_answer = models.CharField(max_length=200, blank=True)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)