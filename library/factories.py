from django.utils.text import slugify
import factory
from .models import Item, LibraryTag


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    name = factory.Sequence(lambda n: f"Item {n}")
    slug = factory.Sequence(lambda n: slugify(f"Item {n}"))
    description = ""
    condition = ""
    notes = ""

    min_players = None
    max_players = None
    min_play_time = None
    max_play_time = None

    is_borrowable = True
    is_high_demand = False

    image = None


class LibraryTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LibraryTag

    name = factory.Sequence(lambda n: f"tag{n}")
