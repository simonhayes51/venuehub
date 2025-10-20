import stripe
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from directory.models import Listing

def subscribe_index(request):
    listing_id=request.GET.get("listing","")
    return render(request,"billing/subscribe.html",{"listing_id":listing_id,"price_id":settings.STRIPE_PRICE_ID})

def create_checkout_session(request):
    if request.method!="POST":
        return HttpResponseBadRequest("Invalid method")
    listing_id=request.POST.get("listing_id")
    email=request.POST.get("email")
    if not (listing_id and email):
        return HttpResponseBadRequest("Missing fields")
    listing=get_object_or_404(Listing, pk=listing_id)
    stripe.api_key=settings.STRIPE_SECRET_KEY
    session=stripe.checkout.Session.create(
        mode="subscription",
        customer_email=email,
        line_items=[{"price":settings.STRIPE_PRICE_ID,"quantity":1}],
        metadata={"listing_id":str(listing.pk)},
        success_url=f"{settings.SITE_URL}/billing/success/?session_id={{CHECKOUT_SESSION_ID}}&listing={listing.pk}",
        cancel_url=f"{settings.SITE_URL}/billing/cancel/",
    )
    return redirect(session.url)

def subscribe_success(request):
    listing_id=request.GET.get("listing")
    if settings.DEBUG and listing_id:
        messages.info(request,"DEBUG: Use the manual button if webhooks aren’t set up.")
    return render(request,"billing/success.html",{"listing_id":listing_id})

def subscribe_cancel(request):
    messages.warning(request,"Subscription canceled or not completed.")
    return redirect("billing:subscribe_index")

@csrf_exempt
def webhook(request):
    payload=request.body
    sig=request.META.get("HTTP_STRIPE_SIGNATURE","")
    secret=settings.STRIPE_WEBHOOK_SECRET
    try:
        event=stripe.Webhook.construct_event(payload, sig, secret)
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    if event["type"]=="checkout.session.completed":
        data=event["data"]["object"]
        listing_id=data.get("metadata",{}).get("listing_id")
        customer=data.get("customer")
        subscription=data.get("subscription")
        if listing_id:
            try:
                l=Listing.objects.get(pk=int(listing_id))
                l.is_premium=True
                l.stripe_customer_id=customer or ""
                l.stripe_subscription_id=subscription or ""
                try:
                    sub=stripe.Subscription.retrieve(subscription) if subscription else None
                    if sub and sub.get("current_period_end"):
                        l.featured_until=datetime.utcfromtimestamp(sub["current_period_end"]).date()
                except Exception:
                    pass
                l.save(update_fields=["is_premium","stripe_customer_id","stripe_subscription_id","featured_until"])
            except Listing.DoesNotExist:
                pass

    elif event["type"] in ("invoice.paid","customer.subscription.updated"):
        obj=event["data"]["object"]
        sub_id=obj.get("subscription") if event["type"]=="invoice.paid" else obj.get("id")
        try:
            l=Listing.objects.get(stripe_subscription_id=sub_id)
            l.is_premium=True
            if event["type"]=="invoice.paid":
                period_end=obj.get("lines",{}).get("data",[{}])[0].get("period",{}).get("end")
                if period_end:
                    l.featured_until=datetime.utcfromtimestamp(period_end).date()
            else:
                current_end=obj.get("current_period_end")
                if current_end:
                    l.featured_until=datetime.utcfromtimestamp(current_end).date()
            l.save(update_fields=["is_premium","featured_until"])
        except Listing.DoesNotExist:
            pass

    elif event["type"] in ("customer.subscription.deleted","customer.subscription.canceled"):
        sub=event["data"]["object"]
        sub_id=sub.get("id")
        try:
            l=Listing.objects.get(stripe_subscription_id=sub_id)
            l.is_premium=False
            l.save(update_fields=["is_premium"])
        except Listing.DoesNotExist:
            pass

    return HttpResponse(status=200)

def billing_portal(request):
    listing_id=request.GET.get("listing")
    if not listing_id:
        messages.info(request,"Pass ?listing=<id> to open the portal for a specific listing.")
        return redirect("directory:listings")
    listing=get_object_or_404(Listing, pk=listing_id)
    if not listing.stripe_customer_id:
        messages.error(request,"No Stripe customer linked to this listing yet.")
        return redirect("directory:listing_detail", pk=listing.pk)
    stripe.api_key=settings.STRIPE_SECRET_KEY
    portal=stripe.billing_portal.Session.create(
        customer=listing.stripe_customer_id,
        return_url=settings.STRIPE_PORTAL_RETURN_URL or settings.SITE_URL + "/",
    )
    return redirect(portal.url)

def manual_mark_premium(request):
    if not settings.DEBUG:
        return HttpResponseBadRequest("Not available")
    listing_id=request.GET.get("listing")
    l=get_object_or_404(Listing, pk=listing_id)
    l.is_premium=True
    from datetime import date, timedelta
    l.featured_until=date.today()+timedelta(days=30)
    l.save(update_fields=["is_premium","featured_until"])
    messages.success(request,f"{l.title} marked as Premium (manual).")
    return redirect("directory:listing_detail", pk=l.pk)
