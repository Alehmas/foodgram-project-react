import csv

from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = "Loads data from tags.csv"

    def handle(self, *args, **options):
        with open('./data/tags.csv', 'r', encoding='UTF-8') as f:
            csv_reader = csv.reader(f, delimiter=',')
            for row in csv_reader:
                Tag.objects.create(name=row[0], color=row[1], slug=row[2])
