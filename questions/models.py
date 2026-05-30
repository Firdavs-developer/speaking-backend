from django.db import models


class Question(models.Model):
    """A single IELTS speaking question, stored in the database.

    Mirrors the `Question` type used by the Next.js frontend.
    """

    PART_1 = "Part 1"
    PART_2 = "Part 2"
    PART_3 = "Part 3"
    PART_CHOICES = [
        (PART_1, "Part 1"),
        (PART_2, "Part 2"),
        (PART_3, "Part 3"),
    ]

    # Public string id used by the frontend (e.g. "p1-q1").
    qid = models.CharField(max_length=120, unique=True)
    part = models.CharField(max_length=10, choices=PART_CHOICES)
    part_label = models.CharField(max_length=120, default="Question")
    question = models.TextField()
    prep_seconds = models.PositiveIntegerField(default=5)
    speak_seconds = models.PositiveIntegerField(default=30)

    # Optional question image.
    image_src = models.CharField(max_length=500, blank=True)
    image_alt = models.CharField(max_length=255, blank=True)

    # Optional list of cue-card bullet points (Part 2).
    cue_points = models.JSONField(default=list, blank=True)

    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Keeps the test order predictable: Part 1, then 2, then 3.
    _PART_ORDER = {PART_1: 0, PART_2: 1, PART_3: 2}

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"[{self.part}] {self.question[:50]}"

    @property
    def part_rank(self):
        return self._PART_ORDER.get(self.part, 99)
