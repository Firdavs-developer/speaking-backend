from django.conf import settings
from django.db import models


class Result(models.Model):
    """A saved speaking-test result for a user, with the AI evaluation."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="results",
        null=True,
        blank=True,
    )

    overall_band = models.FloatField(null=True, blank=True)
    estimated_cefr = models.CharField(max_length=8, blank=True)
    summary = models.TextField(blank=True)

    # Full AI evaluation payload (criteria, partFeedback, strengths, etc.).
    evaluation = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.user.email if self.user else "anonymous"
        return f"Result({who}, band={self.overall_band})"


class Answer(models.Model):
    """A single spoken answer captured during a test, linked to a Result."""

    result = models.ForeignKey(
        Result, on_delete=models.CASCADE, related_name="answers"
    )
    part = models.CharField(max_length=20)
    question = models.TextField()
    transcript = models.TextField(blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.part}: {self.question[:40]}"
