from django.test import TestCase
from .factories import ItemFactory, LibraryTagFactory
from .models import Item, LibraryTag


class LibraryModelTests(TestCase):
    def setUp(self):
        pass

    def test_tagging(self):
        item = ItemFactory()
        tag = LibraryTagFactory()
        item.base_tags.add(tag)
        self.assertIn(tag, item.base_tags.all())

