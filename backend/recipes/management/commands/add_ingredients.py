import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Loads data from tags.csv"

    def handle(self, *args, **options):
        with open('../data/ingredients.csv', 'r', encoding='UTF-8') as f:
            csv_reader = csv.reader(f, delimiter=',')
            for row in csv_reader:
                Ingredient.objects.create(name=row[0], measurement_unit=row[1])
