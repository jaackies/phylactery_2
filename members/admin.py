from django.contrib import admin

from blog.models import MailingList
from .models import Member, Membership, Rank


class RankInline(admin.TabularInline):
	model = Rank
	extra = 0


class MailingListInline(admin.TabularInline):
	model = MailingList.members.through
	extra = 0


class MembershipInline(admin.TabularInline):
	model = Membership
	extra = 0
	fk_name = "member"
	fields = ("date_purchased", "guild_member", "amount_paid", "expired", "authorised_by")


class MemberAdmin(admin.ModelAdmin):
	inlines = [RankInline, MembershipInline, MailingListInline]


admin.site.register(Member, MemberAdmin)
admin.site.register(Membership)
