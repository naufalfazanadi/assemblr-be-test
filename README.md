# Assemblr Backend Technical Test

An Order Checkout & Payment system built with Django REST Framework and Midtrans Sandbox payment integration.

## Tech Stack

- Python 3.10+
- Django 4.2 + Django REST Framework 3.14
- PostgreSQL
- JWT via `djangorestframework-simplejwt` (access token only)
- Midtrans Sandbox via `midtransclient`
- Gunicorn (production server)

## Prerequisites

- Python 3.10+
- PostgreSQL running locally

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/naufalfazanadi/assemblr-be-test
cd assemblr-be-test

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements/local.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

- `DJANGO_SECRET_KEY` — any random string (e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — your PostgreSQL credentials
- `MIDTRANS_SERVER_KEY` / `MIDTRANS_CLIENT_KEY` — from [Midtrans Sandbox Dashboard](https://sandbox.midtrans.com) → Settings → Access Keys

### 3. Create database

```bash
createdb assemblr_db   # or use pgAdmin
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create superuser (for Django admin panel)

```bash
python manage.py createsuperuser
```

### 6. Seed products (optional)

Use Django admin at `http://localhost:8000/admin/`, or run:

```bash
python manage.py shell -c "
from apps.products.models import Product
Product.objects.create(name='Mouse', description='Productivity mouse', price=150000, stock=25)
Product.objects.create(name='Keyboard', description='Mechanical keyboard', price=350000, stock=5)
Product.objects.create(name='Monitor', description='24 inch monitor', price=1000000, stock=5)
"
```

### 7. Run development server

```bash
python manage.py runserver
```

API is available at `http://localhost:8000/`. Health check: `GET /`.

## Webhook Setup (for local testing)

Midtrans needs a public URL to POST webhook notifications. Use [ngrok](https://ngrok.com/):

```bash
ngrok http 8000
```

Then in [Midtrans Sandbox Dashboard](https://sandbox.midtrans.com):

- Go to **Settings → Payment → Notification URL**
- Set **Payment Notification URL** to: `https://<your-ngrok-id>.ngrok-free.app/api/v1/payments/webhook/`

## API Testing Flow

Here's the basic flow to test the API (you can use Postman, curl, etc.):

1. **Register/Login** (`POST /api/v1/users/register/` or `/login/`)
   - Create a user with your email, name, and a strong password (e.g., `!Password123`).
   - Grab the `accessToken` from the response and set it as your Bearer token.

2. **Get a Product** (`GET /api/v1/products/`)
   - Grab a `product_id` from the list.

3. **Create Order** (`POST /api/v1/orders/`)
   - Send the `product_id` and `quantity` inside the `items` array. This automatically reserves and deducts the stock.
   - Grab the order ID from the response.

4. **Update or Cancel Order (Optional)** (`PUT /api/v1/orders/{id}/` or `PATCH /api/v1/orders/{id}/`)
   - If you want to change the items, hit `PUT` with the new payload. Stock will manually adjust!
   - If you want to cancel the order before paying, hit `PATCH`. The stock will be returned to the inventory.

5. **Pay** (`POST /api/v1/orders/{id}/pay/`)
   - This returns a `midtrans_redirect_url`. If you hit this endpoint multiple times, it safely returns the same token to prevent duplicates.

6. **Simulate Payment**
   - Open the `midtrans_redirect_url` in your browser.
   - Pay using the [Midtrans Mock Card](https://docs.midtrans.com/docs/testing-payments) (or intentionally use a failing card/status).
   - Once completed, Midtrans will hit your ngrok webhook in the background.

7. **Check Order & Stock** (`GET /api/v1/orders/{id}/` and `GET /api/v1/products/`)
   - If successful, the order status should now automatically be updated to `paid`.
   - If the payment failed or expired, the order status will be `failed`/`expired` AND the reserved stock will be automatically restored to the products!

## Running in Production

```bash
pip install -r requirements/prod.txt
gunicorn config.wsgi:application --workers 4
```
