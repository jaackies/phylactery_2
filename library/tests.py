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

        eligible.average_play_time = 59
        eligible.compute_play_time()
        self.assertEquals(eligible.average_play_time, 59)

    def test_tagging(self):
        # child -> parent
        # Edge of the Empire -> Star Wars
        # Edge of the Empire -> RPG
        # Star Wars -> Aliens
        # Star Wars -> Droids
        # Droids -> Robots
        # Robots -> Droids
        # Robots -> Sci-Fi
        edge_e = LibraryTagFactory(name="Edge of the Empire")
        star_wars = LibraryTagFactory(name="Star Wars")
        rpg = LibraryTagFactory(name="RPG")
        aliens = LibraryTagFactory(name="Aliens")
        droids = LibraryTagFactory(name="Droids")
        robots = LibraryTagFactory(name="Robots")
        sci_fi = LibraryTagFactory(name="Sci-Fi")

        edge_e.parents.set([star_wars, rpg])
        star_wars.parents.set([aliens, droids])
        droids.parents.add(robots)
        robots.parents.add(droids)
        robots.parents.add(sci_fi)

        edge_e.save()
        star_wars.save()
        rpg.save()
        aliens.save()
        droids.save()
        robots.save()
        sci_fi.save()

        new_item = ItemFactory(name="Star Wars RPG")
        new_item.base_tags.add(star_wars)
        new_item.base_tags.add(rpg)
        new_item.save()

        # This item should now have the tags "Star Wars", "RPG", "Aliens", "Droids", "Robots", "Sci-Fi"
        self.assertEquals(set(new_item.all_tags), {star_wars, rpg, aliens, robots, droids, sci_fi})
