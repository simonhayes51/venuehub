from django.core.management.base import BaseCommand
from directory.models import Organisation, Listing, Vacancy
import random
from datetime import date, timedelta

ORG=["The King’s Arms","Riverside Social","City Tavern","Harbour Lights","The Foundry","Oak & Iron"]
CITIES=["Newcastle","Manchester","Leeds","Liverpool","Birmingham","London"]
CATS=["quiz","dj","band","comedian","karaoke","other"]

class Command(BaseCommand):
    help="Seed demo data"
    def handle(self,*args,**kwargs):
        if Organisation.objects.exists():
            self.stdout.write("Data exists; skipping.")
            return
        orgs=[Organisation.objects.create(name=n,city=random.choice(CITIES),region="England",website="",contact_email="info@example.com") for n in ORG]
        for i in range(20):
            Listing.objects.create(
                organisation=random.choice(orgs), title=f"Demo Listing {i+1}",
                category=random.choice(CATS), description="A short description of this entertainer/service.",
                location=random.choice(CITIES), price_from=random.choice([None,80,120,200,350]),
                is_premium=random.choice([False,False,True]), featured_until=None, is_approved=random.choice([True, True, False]),
                website="", contact_email="booking@example.com", owner_email="owner@example.com"
            )
        for j in range(6):
            Vacancy.objects.create(
                title=f"Need {random.choice(['DJ','Quiz Host','Band'])}",
                description="Event night entertainment.",
                event_date=date.today()+timedelta(days=random.randint(3,30)),
                budget=random.choice([150,200,300,500]),
                location=random.choice(CITIES),
                contact_email="manager@example.com",
                is_open=True
            )
        self.stdout.write(self.style.SUCCESS("Seeded demo data."))
