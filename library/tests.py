from django.test import TestCase
from library.models import Item, LibraryTag

class LibraryModelTests(TestCase):
    def setUp(self):
        Item.objects.create(
            name='Test Item',
            slug='test-item',
            image=None,
        )
        for char in 'ABCDEFG':
            LibraryTag.objects.create(name=char)

        for char1, char2 in zip('ABCDEFG','BCDEFGA'):
            LibraryTag.objects.get(name=char1).parents.add(LibraryTag.objects.get(name=char2))


    def test_tagging(self):
        all_tags = set(LibraryTag.objects.all())

        test_item = Item.objects.get(name="Test Item")
        test_item.base_tags.add(LibraryTag.objects.get(name='A'))
        test_item.save()
        test_item.compute_tags(recursion=False)
        self.assertEquals(set(test_item.all_tags), all_tags)