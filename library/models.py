from django.db import models
from taggit.managers import TaggableManager, _TaggableManager
from taggit.models import TagBase, TaggedItemBase


class ItemTaggableManager(_TaggableManager):
    """
    A custom TaggableManager to help with Library tagging.
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


class BaseTaggedLibraryItem(TaggedItemBase):
    """
    A custom model to store the Tags for the library system.
    """
    tag = models.ForeignKey(
        LibraryTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items"
    )
    content_object = models.ForeignKey("Item", on_delete=models.CASCADE)


class ComputedTaggedLibraryItem(TaggedItemBase):
    """
    A custom model to store the Tags for the library system.
    """
    tag = models.ForeignKey(
        LibraryTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items"
    )
    content_object = models.ForeignKey("Item", on_delete=models.CASCADE)


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

    # The tags for the Item. Base tags are the tags manually applied to the item.
    # Computed tags are the ones automatically set due to tag hierarchy.
    base_tags = TaggableManager(manager=ItemTaggableManager, through=BaseTaggedLibraryItem, blank=True, verbose_name="Base Tags", related_name="base_items")
    computed_tags = TaggableManager(manager=ItemTaggableManager, through=ComputedTaggedLibraryItem, blank=True, verbose_name="Computed Tags", related_name="computed_items")

    # Data for display on the Item's page.
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

    # Methods
    def __str__(self):
        # The name for the object in the admin interface.
        return self.name

    def all_tags(self):
        # Helper method to return all the item's tags.
        return self.base_tags.all().union(self.computed_tags.all())

    def players_display(self):
        # Returns a string representation of the player count.
        if not (self.min_players or self.max_players):
            # No player count given.
            return ""
        if self.min_players == self.max_players:
            # Exactly N players.
            return f"{self.min_players} player{'s' if self.min_players > 1 else ''}"
        if not self.min_players:
            # There's a max but no minimum.
            return f"1 - {self.max_players} players"
        if not self.max_players:
            # There's a minimum but no max.
            return f"{self.max_players}+ players"
        # The base case
        return f"{self.min_players} - {self.max_players} players"
