from django.test import TestCase
from .factories import ItemFactory, LibraryTagFactory
from .models import Item, LibraryTag


class LibraryModelTests(TestCase):
    def setUp(self):
        pass

    def test_item_name(self):
        item = ItemFactory()
        self.assertEqual(str(item), item.name)

    def test_all_tags(self):
        item = ItemFactory()
        tags = LibraryTagFactory.create_batch(5)
        item.base_tags.set(tags[0:2])
        item.computed_tags.set(tags[2:])
        self.assertEqual(set(item.all_tags), set(tags))

    def test_players_display(self):
        no_players = ItemFactory()
        self.assertEquals(no_players.players_display, "")

        equal_players = ItemFactory(min_players=1, max_players=1)
        self.assertEquals(equal_players.players_display, "1 player")
        equal_players_plural = ItemFactory(min_players=3, max_players=3)
        self.assertEquals(equal_players_plural.players_display, "3 players")

        no_max = ItemFactory(min_players=1)
        self.assertEquals(no_max.players_display, "1+ players")

        no_min = ItemFactory(max_players=5)
        self.assertEquals(no_min.players_display, "1 - 5 players")

        different = ItemFactory(min_players=2, max_players=6)
        self.assertEquals(different.players_display, "2 - 6 players")

    def test_compute_play_time(self):
        ineligible_1 = ItemFactory(min_play_time=30)
        ineligible_1.compute_play_time()
        self.assertEquals(ineligible_1.average_play_time, None)

        ineligible_2 = ItemFactory(max_play_time=60)
        ineligible_2.compute_play_time()
        self.assertEquals(ineligible_2.average_play_time, None)

        eligible = ItemFactory(min_play_time=30, max_play_time=60)
        eligible.compute_play_time()
        self.assertEquals(eligible.average_play_time, 45)

    def test_tagging(self):
        item = ItemFactory()
        tag = LibraryTagFactory()
        item.base_tags.add(tag)
        self.assertIn(tag, item.base_tags.all())

