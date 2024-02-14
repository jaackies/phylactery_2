from django.utils.text import slugify
import factory
from .models import Item, LibraryTag, BorrowerDetails, BorrowRecord, Reservation


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


class BorrowerDetailsFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = BorrowerDetails
	
	is_external = True
	internal_member = None
	borrower_name = factory.Faker("name")
	
	borrower_address = factory.Faker("address")
	borrower_phone = factory.Faker("phone_number")
	
	borrow_authorised_by = factory.Faker("name")


class BorrowRecordFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = BorrowRecord
	
	item = factory.SubFactory(ItemFactory)
	borrower = factory.SubFactory(BorrowerDetailsFactory)
	
	borrow_authorised_by = factory.Faker("name")
	

class ReservationFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Reservation
	
	is_external = False
	internal_member = None
	requestor_name = factory.Faker("name")
	requestor_email = factory.Faker("email")
	requestor_phone = factory.Faker("phone_number")
	
	@factory.post_generation
	def reserved_items(self, create, extracted, **kwargs):
		if not create or not extracted:
			# Simple Build, or nothing to add, do nothing
			return
		
		# Add the items to the reservation using bulk addition
		self.reserved_items.add(*extracted)
	
