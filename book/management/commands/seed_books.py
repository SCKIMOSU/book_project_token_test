# book/management/commands/seed_books.py

from django.core.management.base import BaseCommand
from faker import Faker
from book.models import Book
import random

class Command(BaseCommand):
    help = 'Generate fake Book data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        total = 10

        for _ in range(total):
            Book.objects.create(
                title=fake.sentence(nb_words=3),
                author=fake.name(),
                published_year=random.randint(1990, 2024)
            )

        self.stdout.write(self.style.SUCCESS(f'✅ {total}개의 Book 데이터를 생성했습니다.'))
