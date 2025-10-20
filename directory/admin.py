from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Organisation, Listing, Review, ContactRequest, Vacancy, VacancyApplication, ListingImage

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display=("name","city","region","website","contact_email","created_at")
    search_fields=("name","city","region")

class ListingImageInline(admin.TabularInline):
    model=ListingImage
    extra=0

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display=("title","category","organisation","location","price_from","is_premium","featured_until","is_approved","created_at")
    list_filter=("category","is_premium","is_approved")
    search_fields=("title","description","location","organisation__name")
    autocomplete_fields=("organisation",)
    readonly_fields=("stripe_customer_id","stripe_subscription_id","edit_code")
    inlines=[ListingImageInline]
    actions=["approve_listings","mark_premium"]
    def approve_listings(self, request, queryset):
        updated = queryset.update(is_approved=True)
        for l in queryset:
            l.ensure_edit_code()
            if l.owner_email:
                send_mail("Your listing is approved",
                          f"Your listing '{l.title}' is now live: {getattr(settings,'SITE_URL','')}/listings/{l.pk}/\nManage: {getattr(settings,'SITE_URL','')}/listings/{l.pk}/edit/?code={l.edit_code}",
                          settings.DEFAULT_FROM_EMAIL,[l.owner_email],fail_silently=True)
        self.message_user(request, f"Approved {updated}")
    def mark_premium(self, request, queryset):
        updated = queryset.update(is_premium=True)
        for l in queryset:
            if l.owner_email:
                send_mail("Premium activated",
                          f"Your listing '{l.title}' is now Premium.",
                          settings.DEFAULT_FROM_EMAIL,[l.owner_email],fail_silently=True)
        self.message_user(request, f"Premium {updated}")
    approve_listings.short_description="Approve selected"
    mark_premium.short_description="Mark selected Premium"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=("listing","rating","venue_name","is_published","created_at")
    list_filter=("is_published","rating")
    search_fields=("listing__title","venue_name","comment")

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display=("listing","venue_name","venue_email","status","created_at")
    list_filter=("status",)
    search_fields=("venue_name","venue_email","message")

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display=("title","event_date","budget","location","contact_email","is_open","created_at")
    list_filter=("is_open",)
    search_fields=("title","description","location","contact_email")

@admin.register(VacancyApplication)
class VacancyApplicationAdmin(admin.ModelAdmin):
    list_display=("vacancy","listing","created_at")
    search_fields=("vacancy__title","listing__title")
