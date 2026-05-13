# BookGlam — On-Demand Beauty Services Platform

Nigeria's Uber-style beauty services marketplace. Connects clients with verified hair stylists, barbers, makeup artists, and nail technicians for instant or scheduled home/shop visits.

---

## Project Structure

```
bookglam/
│
├── run.py                    # App entry point
├── seed_admin.py             # Create first admin account
├── requirements.txt
│
└── app/
    ├── __init__.py           # App factory & DB seeding
    ├── extensions.py         # SQLAlchemy, LoginManager, Bcrypt
    ├── models.py             # All DB models
    │
    ├── main/                 # Public pages (home, services, about, contact)
    ├── auth/                 # Login & signup
    ├── client/               # Client dashboard, booking, profile
    ├── provider/             # Provider dashboard, jobs, earnings, profile
    ├── admin/                # Admin panel (full CRUD + approvals)
    │
    ├── templates/
    │   ├── base.html         # Master layout with design system
    │   ├── _public_nav.html
    │   ├── _dashboard_nav.html
    │   ├── _footer.html
    │   ├── main/
    │   ├── auth/
    │   ├── client/
    │   ├── provider/
    │   └── admin/
    │
    └── static/
        ├── css/
        ├── js/
        └── images/
```

---

## Setup & Run

### 1. Clone and create virtual environment

```bash
cd bookglam
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python run.py
```

The app will start at **http://localhost:5000**

The database (`bookglam.db`) and all service categories/services are auto-created on first run.

### 4. Create admin account

```bash
python seed_admin.py
```

Admin credentials:
- **Email:** admin@bookglam.ng
- **Password:** Admin@1234

---

## User Roles & Access

| Role | Access | URL Prefix |
|------|--------|-----------|
| Client | Book services, view history, leave reviews | `/client/` |
| Provider | Accept jobs, manage availability, withdraw earnings | `/provider/` |
| Admin | Full platform management | `/admin/` |

---

## Key Features

### For Clients
- Sign up & choose role (client/provider)
- Browse services by category (Hair, Barbing, Makeup, Nails)
- Book instantly or schedule ahead
- Choose home visit or shop visit
- Select service tier (Basic / Standard / Premium)
- Pay by cash, transfer, wallet, or card
- Live tracking indicator
- Rate & review after completion

### For Providers
- Register & await admin verification
- Toggle online/offline availability
- Browse and accept open job requests
- Update job status step-by-step (accepted → on_the_way → in_progress → completed)
- Real-time earnings dashboard
- Request bank withdrawals (admin approves)
- Profile with specialties, location, and tier

### For Admins
- Overview dashboard with platform stats
- Verify/revoke provider accounts
- Manage all users (activate/deactivate)
- Monitor all bookings with status filtering
- Dispute resolution (mark completed or cancel)
- Process/reject provider withdrawal requests
- View full service catalogue

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask 3.x |
| Database ORM | Flask-SQLAlchemy (SQLite → swap to PostgreSQL for production) |
| Auth | Flask-Login + Flask-Bcrypt |
| Migrations | Flask-Migrate (Alembic) |
| Frontend | Jinja2 templates + Tailwind CSS (CDN) |
| Icons | Font Awesome 6 |
| Fonts | Playfair Display + DM Sans (Google Fonts) |

---

## Production Checklist

- [ ] Change `SECRET_KEY` in `app/__init__.py` to a random secure string
- [ ] Switch `SQLALCHEMY_DATABASE_URI` from SQLite to PostgreSQL
- [ ] Set `debug=False` in `run.py`
- [ ] Add `.env` file with secrets (use `python-dotenv`)
- [ ] Configure a proper WSGI server (Gunicorn + Nginx)
- [ ] Add CSRF protection (Flask-WTF)
- [ ] Implement real payment gateway (Paystack / Flutterwave)
- [ ] Add real-time features with Flask-SocketIO for live tracking
- [ ] Set up file upload handling for provider ID/portfolio images
- [ ] Add email notifications (Flask-Mail)

---

## Expanding the Platform

The codebase is structured for easy growth:

1. **Real-time tracking**: Add Flask-SocketIO — providers emit location updates, clients receive them
2. **Push notifications**: Integrate FCM for mobile web notifications on new bookings
3. **Payments**: Paystack is Nigeria's go-to — wrap the API in `app/utils/payments.py`
4. **Two separate apps**: The role-based single app is designed to split into `client_app` and `provider_app` at scale
5. **Multi-city**: The `ProviderProfile.location` field and lat/lng are ready for geospatial filtering

---

*BookGlam — Beauty, At Your Doorstep.*
