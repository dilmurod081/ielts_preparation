from django.contrib import admin
from .models import ReadingTest, QuestionBlock, Question

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    ordering = ('question_number',)

class QuestionBlockAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('test', 'question_type', 'instructions')
    list_filter = ('test',)

admin.site.register(ReadingTest)
admin.site.register(QuestionBlock, QuestionBlockAdmin)