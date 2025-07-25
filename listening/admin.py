from django.contrib import admin
from .models import ListeningTest, ListeningPart, QuestionGroup, Question

# Allows adding Questions when editing a QuestionGroup
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1 # Show 1 empty question form by default
    ordering = ('question_number',)

# Allows adding QuestionGroups when editing a ListeningPart
class QuestionGroupInline(admin.StackedInline):
    model = QuestionGroup
    extra = 1 # Show 1 empty group form by default

class QuestionGroupAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('__str__', 'part', 'group_type')
    list_filter = ('part__test',)

class ListeningPartAdmin(admin.ModelAdmin):
    inlines = [QuestionGroupInline]
    list_display = ('__str__', 'test')
    list_filter = ('test',)

# Register your models with the new admin configurations
admin.site.register(ListeningTest)
admin.site.register(ListeningPart, ListeningPartAdmin)
admin.site.register(QuestionGroup, QuestionGroupAdmin)