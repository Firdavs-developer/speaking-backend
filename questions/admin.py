from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("qid", "part", "part_label", "short_question", "prep_seconds", "speak_seconds", "order")
    list_filter = ("part",)
    search_fields = ("qid", "question", "part_label")
    ordering = ("order", "id")

    @admin.display(description="Question")
    def short_question(self, obj):
        return obj.question[:60]
