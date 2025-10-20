from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

def listing_photo_path(instance, filename):
    return f"listings/{instance.pk or 'new'}/{filename}"

def listing_gallery_path(instance, filename):
    return f"listings/{instance.listing_id}/gallery/{filename}"

class Organisation(models.Model):
    name=models.CharField(max_length=200)
    city=models.CharField(max_length=100,blank=True)
    region=models.CharField(max_length=100,blank=True)
    website=models.URLField(blank=True)
    contact_email=models.EmailField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["name"]
    def __str__(self): return self.name

class Listing(models.Model):
    class Category(models.TextChoices):
        QUIZ_HOST="quiz","Quiz Host"
        DJ="dj","DJ"
        BAND="band","Band"
        COMEDIAN="comedian","Comedian"
        KARAOKE="karaoke","Karaoke Host"
        OTHER="other","Other"
    organisation=models.ForeignKey(Organisation,on_delete=models.CASCADE,related_name="listings")
    title=models.CharField(max_length=200)
    category=models.CharField(max_length=20,choices=Category.choices,default=Category.OTHER)
    description=models.TextField(blank=True)
    location=models.CharField(max_length=120,blank=True)
    price_from=models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True)
    photo=models.ImageField(upload_to=listing_photo_path, blank=True, null=True)
    is_premium=models.BooleanField(default=False)
    featured_until=models.DateField(null=True,blank=True)
    is_approved=models.BooleanField(default=False)
    website=models.URLField(blank=True)
    contact_email=models.EmailField(blank=True)
    owner_email=models.EmailField(blank=True)
    stripe_customer_id=models.CharField(max_length=100, blank=True)
    stripe_subscription_id=models.CharField(max_length=100, blank=True)
    edit_code=models.CharField(max_length=36, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-is_premium","-is_approved","title"]
    def __str__(self): return f"{self.title} ({self.organisation.name})"
    @property
    def is_featured(self):
        return self.is_premium or (self.featured_until and self.featured_until >= timezone.now().date())
    def ensure_edit_code(self):
        if not self.edit_code:
            self.edit_code=str(uuid.uuid4())
            self.save(update_fields=["edit_code"])

class ListingImage(models.Model):
    listing=models.ForeignKey(Listing,on_delete=models.CASCADE,related_name="images")
    image=models.ImageField(upload_to="listings/gallery/")
    caption=models.CharField(max_length=200, blank=True)
    uploaded_at=models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    listing=models.ForeignKey(Listing,on_delete=models.CASCADE,related_name="reviews")
    rating=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.TextField(blank=True)
    venue_name=models.CharField(max_length=200,blank=True)
    venue_email=models.EmailField(blank=True)
    is_published=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]

class ContactRequest(models.Model):
    listing=models.ForeignKey(Listing,on_delete=models.CASCADE,related_name="leads")
    venue_name=models.CharField(max_length=200)
    venue_email=models.EmailField()
    message=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,default="new")

class Vacancy(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    event_date=models.DateField(null=True,blank=True)
    budget=models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True)
    location=models.CharField(max_length=120,blank=True)
    contact_email=models.EmailField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_open=models.BooleanField(default=True)

class VacancyApplication(models.Model):
    vacancy=models.ForeignKey(Vacancy,on_delete=models.CASCADE,related_name="applications")
    listing=models.ForeignKey(Listing,on_delete=models.CASCADE,related_name="applications")
    message=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
