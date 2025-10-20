from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Listing, Organisation, Vacancy, ListingImage
from .forms import HostSignupForm, ReviewForm, VacancyForm, VacancyApplicationForm, ContactRequestForm, ListingEditForm, ListingImageForm
from .recaptcha import verify_recaptcha

def home(request):
    featured=Listing.objects.filter(is_approved=True).order_by("-is_premium","-created_at")[:6]
    vacancies=Vacancy.objects.filter(is_open=True).order_by("-created_at")[:5]
    return render(request,"home.html",{"featured":featured,"vacancies":vacancies})

def listings(request):
    q=request.GET.get("q","").strip()
    category=request.GET.get("category","")
    qs=Listing.objects.filter(is_approved=True)
    if q:
        qs=qs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(location__icontains=q)|Q(organisation__name__icontains=q))
    if category:
        qs=qs.filter(category=category)
    return render(request,"directory/listings.html",{"listings":qs,"q":q,"category":category})

def listing_detail(request, pk):
    item=get_object_or_404(Listing, pk=pk, is_approved=True)
    reviews=item.reviews.filter(is_published=True)
    avg_rating=reviews.aggregate(avg=Avg("rating"))["avg"]
    if request.method=="POST" and request.POST.get("form_type")=="contact":
        form=ContactRequestForm(request.POST)
        token=request.POST.get("g-recaptcha-response","")
        if not verify_recaptcha(token):
            messages.error(request,"Please complete the reCAPTCHA.")
        elif form.is_valid():
            lead=form.save(commit=False); lead.listing=item; lead.save()
            if item.contact_email:
                send_mail(f"New enquiry for {item.title}",
                          f"From: {lead.venue_name} <{lead.venue_email}>\n\n{lead.message}",
                          settings.DEFAULT_FROM_EMAIL,[item.contact_email],fail_silently=True)
            send_mail("Thanks — enquiry sent",
                      f"Your enquiry has been sent to {item.title}. They may contact you directly.",
                      settings.DEFAULT_FROM_EMAIL,[lead.venue_email],fail_silently=True)
            messages.success(request,"Enquiry sent to host.")
            return redirect("directory:listing_detail", pk=item.pk)
    else:
        form=ContactRequestForm()
    review_form=ReviewForm()
    return render(request,"directory/listing_detail.html",{"item":item,"reviews":reviews,"avg_rating":avg_rating,"form":form,"review_form":review_form})

def submit_review(request, pk):
    item=get_object_or_404(Listing, pk=pk, is_approved=True)
    if request.method=="POST":
        form=ReviewForm(request.POST)
        token=request.POST.get("g-recaptcha-response","")
        if not verify_recaptcha(token):
            messages.error(request,"Please complete the reCAPTCHA.")
        elif form.is_valid():
            r=form.save(commit=False); r.listing=item; r.is_published=False; r.save()
            send_mail("New review submitted",
                      f"A new review for {item.title} is awaiting moderation.",
                      settings.DEFAULT_FROM_EMAIL,[settings.DEFAULT_FROM_EMAIL],fail_silently=True)
            messages.success(request,"Review submitted for moderation.")
    return redirect("directory:listing_detail", pk=item.pk)

def organisations(request):
    q=request.GET.get("q","").strip()
    qs=Organisation.objects.all()
    if q:
        qs=qs.filter(Q(name__icontains=q)|Q(city__icontains=q)|Q(region__icontains=q))
    return render(request,"directory/organisations.html",{"organisations":qs,"q":q})

def organisation_detail(request, pk):
    org=get_object_or_404(Organisation, pk=pk)
    items=org.listings.filter(is_approved=True)
    return render(request,"directory/organisation_detail.html",{"org":org,"items":items})

def host_signup(request):
    if request.method=="POST":
        form=HostSignupForm(request.POST, request.FILES)
        token=request.POST.get("g-recaptcha-response","")
        if not verify_recaptcha(token):
            messages.error(request,"Please complete the reCAPTCHA.")
        elif form.is_valid():
            org=Organisation.objects.create(
                name=form.cleaned_data["org_name"],
                city=form.cleaned_data.get("city",""),
                region=form.cleaned_data.get("region",""),
                website=form.cleaned_data.get("website",""),
                contact_email=form.cleaned_data.get("contact_email",""),
            )
            listing=Listing.objects.create(
                organisation=org, title=form.cleaned_data["title"], category=form.cleaned_data["category"],
                description=form.cleaned_data.get("description",""), location=form.cleaned_data.get("location",""),
                price_from=form.cleaned_data.get("price_from"), is_premium=False, featured_until=None, is_approved=False,
                website=form.cleaned_data.get("website",""), contact_email=form.cleaned_data.get("contact_email",""),
                owner_email=form.cleaned_data.get("owner_email",""),
            )
            photo=form.cleaned_data.get("photo")
            if photo:
                listing.photo=photo; listing.save(update_fields=["photo"])
            listing.ensure_edit_code()
            send_mail("Thanks — listing submitted",
                      "Thanks! We'll review your listing shortly. We'll email you once approved.",
                      settings.DEFAULT_FROM_EMAIL,[form.cleaned_data.get("owner_email")],fail_silently=True)
            send_mail("New host signup pending review",
                      f"Act: {form.cleaned_data['org_name']}\nTitle: {form.cleaned_data['title']}",
                      settings.DEFAULT_FROM_EMAIL,[settings.DEFAULT_FROM_EMAIL],fail_silently=True)
            if form.cleaned_data.get("wants_premium"):
                send_mail("Premium interest received","Host ticked interested in Premium placement.",
                          settings.DEFAULT_FROM_EMAIL,[settings.DEFAULT_FROM_EMAIL],fail_silently=True)
            messages.success(request,"Submitted for review. We'll approve your listing shortly.")
            return redirect("directory:host_thanks")
    else:
        form=HostSignupForm()
    return render(request,"directory/host_signup.html",{"form":form})

def host_thanks(request):
    return render(request,"directory/host_thanks.html")

def vacancies(request):
    q=request.GET.get("q","").strip()
    qs=Vacancy.objects.filter(is_open=True)
    if q:
        qs=qs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(location__icontains=q))
    return render(request,"directory/vacancies.html",{"vacancies":qs,"q":q})

def vacancy_detail(request, pk):
    v=get_object_or_404(Vacancy, pk=pk)
    return render(request,"directory/vacancy_detail.html",{"vacancy":v})

def post_vacancy(request):
    if request.method=="POST":
        form=VacancyForm(request.POST)
        token=request.POST.get("g-recaptcha-response","")
        if not verify_recaptcha(token):
            messages.error(request,"Please complete the reCAPTCHA.")
        elif form.is_valid():
            v=form.save()
            send_mail("Vacancy posted", f"Your vacancy '{v.title}' is now live.",
                      settings.DEFAULT_FROM_EMAIL,[v.contact_email],fail_silently=True)
            send_mail("New vacancy posted", f"{v.title} — {v.location}",
                      settings.DEFAULT_FROM_EMAIL,[settings.DEFAULT_FROM_EMAIL],fail_silently=True)
            messages.success(request,"Vacancy posted — hosts can apply.")
            return redirect("directory:vacancies")
    else:
        form=VacancyForm()
    return render(request,"directory/post_vacancy.html",{"form":form})

def apply_vacancy(request, pk, listing_id):
    v=get_object_or_404(Vacancy, pk=pk, is_open=True)
    listing=get_object_or_404(Listing, pk=listing_id, is_approved=True)
    if request.method=="POST":
        form=VacancyApplicationForm(request.POST)
        token=request.POST.get("g-recaptcha-response","")
        if not verify_recaptcha(token):
            messages.error(request,"Please complete the reCAPTCHA.")
        elif form.is_valid():
            app=form.save(commit=False); app.vacancy=v; app.listing=listing; app.save()
            send_mail(f"New application for {v.title}",
                      f"{listing.title} has applied.\n\nMessage:\n{app.message}",
                      settings.DEFAULT_FROM_EMAIL,[v.contact_email],fail_silently=True)
            if listing.owner_email:
                send_mail("You applied to a vacancy",
                          f"You applied to '{v.title}'.",
                          settings.DEFAULT_FROM_EMAIL,[listing.owner_email],fail_silently=True)
            messages.success(request,"Applied — the venue has been notified.")
            return redirect("directory:vacancy_detail", pk=v.pk)
    else:
        form=VacancyApplicationForm()
    return render(request,"directory/apply_vacancy.html",{"form":form,"vacancy":v,"listing":listing})

@require_http_methods(["GET","POST"])
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    code = request.GET.get("code") or request.POST.get("code")
    if not code or code != listing.edit_code:
        messages.error(request, "Invalid or missing edit code.")
        return redirect("directory:listing_detail", pk=listing.pk)

    listing.ensure_edit_code()
    form = ListingEditForm(request.POST or None, request.FILES or None, instance=listing)
    img_form = ListingImageForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if "save_listing" in request.POST and form.is_valid():
            form.save()
            messages.success(request, "Listing updated.")
            return redirect(f"{request.path}?code={listing.edit_code}")
        if "add_image" in request.POST and img_form.is_valid():
            obj = img_form.save(commit=False)
            obj.listing = listing
            obj.save()
            messages.success(request, "Image added.")
            return redirect(f"{request.path}?code={listing.edit_code}")

    return render(request, "directory/edit_listing.html", {
        "listing": listing,
        "form": form,
        "img_form": img_form,
    })
