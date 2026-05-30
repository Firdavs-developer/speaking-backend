from django.contrib import admin

from .models import Answer, Result


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ("order", "part", "question", "transcript", "duration_seconds")
    readonly_fields = fields


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "overall_band", "estimated_cefr", "created_at")
    list_filter = ("estimated_cefr", "created_at")
    search_fields = ("user__email", "user__name", "summary")
    readonly_fields = ("created_at",)
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "result", "part", "short_question", "duration_seconds")
    list_filter = ("part",)
    search_fields = ("question", "transcript")

    @admin.display(description="Question")
    def short_question(self, obj):
        return obj.question[:50]
