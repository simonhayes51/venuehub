# VenueHub (Railway Ready)

Directory of entertainment hosts (DJs, bands, quizmasters, etc.) with venue enquiries, vacancies, moderated reviews, Premium placement via Stripe, Billing Portal, photo uploads, and edit links.

## One-time setup
1) Create a new **Postgres** database on Railway (add plugin).
2) Create a new **Service** from this repo.
3) Add environment variables:
   - `SECRET_KEY` (random string)
   - `DEBUG=false`
   - `SITE_URL=https://<your-railway-domain>`
   - `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PORTAL_RETURN_URL`
   - `RECAPTCHA_SITE_KEY`, `RECAPTCHA_SECRET_KEY`
   - (Railway will inject `DATABASE_URL` automatically from Postgres)

## Deploy
Railway will detect Python and run the `Procfile`:
```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn venuehub.wsgi:application --bind 0.0.0.0:$PORT
```

## Local dev
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# set DEBUG=true for local
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

## Webhooks (local)
```
stripe listen --forward-to localhost:8000/billing/webhook/
```

## Notes
- Media uploads are stored on the local filesystem. For production persistence, use S3/Cloudinary later.
