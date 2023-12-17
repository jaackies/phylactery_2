from django.db import models
from taggit.managers import TaggableManager, _TaggableManager
from taggit.models import TagBase, TaggedItemBase


class TaggedLibraryItem(TaggedItemBase):
    """
    A custom model to store the Tags for the library system.
    """
    tag = models.ForeignKey(
        LibraryTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items"
    )
    content_object = models.ForeignKey("Item", on_delete=models.CASCADE)
    computed = models.BooleanField(default=False)


class ItemTaggableManager(_TaggableManager):
    """
    A custom TaggableManager to help with Library tagging.
    """
    def add_base(self, *tags):
        """
        Adds base tags to the Item.
        """
        self.add(*tags, through_defaults={"computed": False})

    def add_computed(self, *tags):
        """
        Adds computed tags to the Item.
        """
        self.add(*tags, through_defaults={"computed": True})

    def set_base(self, tags, clear=False):
        """
        Sets base tags for the Item
        """
        pass


class LibraryTag(TagBase):
    """
    A custom tag to implement Tag hierarchies.
    """
    parents = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="children")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class Item(models.Model):
    """
    Stores all the data related to a single library item.
    """

    # The name and slug of the Item
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100)

    # These fields are for the description, condition, and other notes.
    description = models.TextField(blank=True)
    condition = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    tags = TaggableManager(manager=ItemTaggableManager, through=)

    min_players = models.PositiveIntegerField(blank=True, null=True)
    max_players = models.PositiveIntegerField(blank=True, null=True)

    min_play_time = models.PositiveIntegerField(blank=True, null=True, help_text="in minutes")
    max_play_time = models.PositiveIntegerField(blank=True, null=True, help_text="in minutes")
    average_play_time = models.PositiveIntegerField(blank=True, null=True, help_text="in minutes")

    # These govern the Item's borrowing behaviour
    is_borrowable = models.BooleanField(default=True)
    is_high_demand = models.BooleanField(default=False)

    def get_image_filename(self, filename: str) -> str:
        filename, _, extension = filename.rpartition('.')
        return f"library/item_images/{self.slug}.{extension}"

    image = models.ImageField(upload_to=get_image_filename, null=True)

    class Meta:
        ordering = ['name']
