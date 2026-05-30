from django.core.management.base import BaseCommand

from questions.models import Question

# Seed questions, mirroring DEFAULT_QUESTIONS in the frontend.
SEED = [
    {"qid": "p1-q1", "part": "Part 1", "part_label": "Question 1",
     "question": "What do you usually do in your free time?", "prep_seconds": 5, "speak_seconds": 30},
    {"qid": "p1-q2", "part": "Part 1", "part_label": "Question 2",
     "question": "Do you prefer studying alone or with other people?", "prep_seconds": 5, "speak_seconds": 30},
    {"qid": "p1-q3", "part": "Part 1", "part_label": "Question 3",
     "question": "How often do you use your phone for learning?", "prep_seconds": 5, "speak_seconds": 30},
    {"qid": "p1-q4", "part": "Part 1", "part_label": "Question 4",
     "question": "Look at the picture. What are the people doing?", "prep_seconds": 5, "speak_seconds": 30,
     "image_src": "/images/market-speaking.svg", "image_alt": "People shopping at a colorful market"},
    {"qid": "p1-q5", "part": "Part 1", "part_label": "Question 5",
     "question": "Look at the picture. What problems can online study create?", "prep_seconds": 5, "speak_seconds": 30,
     "image_src": "/images/remote-study.svg", "image_alt": "Students studying online at a table"},
    {"qid": "p1-q6", "part": "Part 1", "part_label": "Question 6",
     "question": "Look at the picture. How could this public place be improved?", "prep_seconds": 5, "speak_seconds": 30,
     "image_src": "/images/city-park.svg", "image_alt": "A city park with cyclists, trees and buildings"},
    {"qid": "p2-q1", "part": "Part 2", "part_label": "Cue card",
     "question": "Describe a skill you would like to improve.", "prep_seconds": 60, "speak_seconds": 120,
     "cue_points": [
         "what the skill is",
         "why you want to improve it",
         "how you plan to practise",
         "how this skill could help you",
     ]},
    {"qid": "p3-q1", "part": "Part 3", "part_label": "Discussion",
     "question": "Do you think technology is changing the way people learn languages? Why?",
     "prep_seconds": 60, "speak_seconds": 120},
]


class Command(BaseCommand):
    help = "Seed the database with the default IELTS speaking questions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing questions before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = Question.objects.all().delete()
            self.stdout.write(f"Deleted {deleted} existing questions.")

        created = 0
        for index, data in enumerate(SEED):
            _, was_created = Question.objects.update_or_create(
                qid=data["qid"],
                defaults={**data, "order": index},
            )
            created += 1 if was_created else 0

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(SEED)} questions ({created} newly created)."
            )
        )
