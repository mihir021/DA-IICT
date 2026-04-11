# BasketIQ (DA-IICT + Wish2Cart)

Merged codebase from Yashvi's Wish2Cart and Mihir's DA-IICT repositories.

## GroceryPulse Admin Overview

GroceryPulse is a grocery-first pricing, personalization, and operations platform built with Django, MongoDB Atlas, and a vanilla HTML/CSS/JS frontend.

## Current Focus

The implemented feature set includes a grocery admin dashboard with:
- staff login
- revenue, orders, stock, and category KPIs
- interactive 2D analytics
- a 3D inventory-depth chart
- grocery-oriented alerts for low stock and perishables

## Stack

- Django 5 + Django REST Framework
- PyMongo for MongoDB Atlas
- Vanilla HTML, CSS, and JavaScript
- Pytest for backend tests

## Local Setup

1. Copy `.env.example` to `.env`
2. Fill in your MongoDB and Django values
3. Install dependencies with `pip install -r requirements.txt`
4. Optionally seed demo data with `python database/seed.py`
5. Run the API with `python manage.py runserver 8000`
6. Open `frontend/admin.html` for the admin dashboard

## Notes

- Keep secrets in `.env` only
- The repo uses MongoDB directly through `database/connection.py`
- Django SQL ORM stays disabled on purpose
