"""
Seed realistic MVP provider data for BookGlam.
Usage: python seed_dummy_providers.py
"""

from datetime import datetime, timedelta
import random

from app.extensions import db, bcrypt
from app.models import Booking, ProviderPortfolio, ProviderProfile, Review, Service, ServiceCategory, User


PHOTO_URLS = [
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=500&q=80",
    "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7?auto=format&fit=crop&w=500&q=80",
]

PORTFOLIO_URLS = [
    "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1605497788044-5a32c7078486?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1595475884562-073c30d45670?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=700&q=80",
    "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?auto=format&fit=crop&w=700&q=80",
]

PROVIDERS = [
    ("Amara Okafor", "Hair", "Wash & Style, Hair Braiding, Silk Press, Bridal Hair"),
    ("Teni Balogun", "Makeup", "Natural Makeup, Bridal Makeup, Soft Glam, Photoshoot Glam"),
    ("Zainab Bello", "Nails", "Manicure, Pedicure, Nail Art, Gel Extensions"),
    ("Kelechi Nwosu", "Barbing", "Haircut & Fade, Beard Trim & Shape, Line Up, Grooming"),
    ("Maya Johnson", "Hair", "Hair Coloring, Wash & Style, Wig Styling, Treatments"),
    ("Ify Eze", "Makeup", "Bridal Makeup, Natural Makeup, Editorial Glam, Gele Styling"),
    ("Damilola Adeyemi", "Nails", "Nail Art, Manicure, Acrylic Sets, Luxury Pedicure"),
    ("Seyi Martins", "Barbing", "Haircut & Fade, Beard Trim & Shape, Classic Cuts"),
    ("Nora Williams", "Hair", "Hair Braiding, Wash & Style, Protective Styling"),
    ("Chioma Umeh", "Makeup", "Natural Makeup, Bridal Makeup, Skin Prep"),
    ("Aisha Lawal", "Nails", "Manicure, Pedicure, Minimal Nail Art"),
    ("David Mensah", "Barbing", "Haircut & Fade, Beard Trim & Shape, Hot Towel"),
    ("Rita Ojo", "Hair", "Hair Coloring, Wash & Style, Blowouts"),
    ("Ebere Obi", "Makeup", "Soft Glam, Bridal Makeup, Natural Makeup"),
    ("Lara Thompson", "Nails", "Nail Art, Gel Polish, Pedicure"),
    ("Kunle Ajayi", "Barbing", "Haircut & Fade, Beard Trim & Shape, Premium Grooming"),
    ("Blessing Etim", "Hair", "Hair Braiding, Wig Install, Wash & Style"),
    ("Mariam Yusuf", "Makeup", "Bridal Makeup, Natural Makeup, HD Glam"),
    ("Fola Bankole", "Nails", "Manicure, Nail Art, Chrome Nails"),
    ("Andre Cole", "Barbing", "Haircut & Fade, Beard Trim & Shape, Fade Specialist"),
    ("Adaeze Iroha", "Hair", "Wash & Style, Hair Coloring, Luxury Treatments"),
    ("Tara Mohammed", "Makeup", "Natural Makeup, Bridal Makeup, Mature Skin Glam"),
]

REVIEW_COMMENTS = [
    "Arrived on time and the finish was even better than my reference photo.",
    "Very calm, clean setup and premium service from start to finish.",
    "Loved the attention to detail. I booked again immediately.",
    "Professional, warm and fast without rushing the result.",
    "My look lasted all day and photographed beautifully.",
    "The whole appointment felt polished and easy.",
]


def find_services(category_name, specialties):
    specialties_lower = specialties.lower()
    services = (Service.query
                .join(ServiceCategory)
                .filter(ServiceCategory.name == category_name)
                .all())
    matched = [service for service in services if service.name.lower() in specialties_lower]
    return matched or services[:2]


def get_or_create_review_client(index):
    email = f"dummy.client{index}@bookglam.test"
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(
        full_name=random.choice(["Nkechi A.", "Tolu R.", "Muna K.", "Bisi O.", "Sandra E.", "Halima Y."]),
        email=email,
        phone=f"080{random.randint(10000000, 99999999)}",
        password_hash=bcrypt.generate_password_hash("password").decode("utf-8"),
        role="client",
    )
    db.session.add(user)
    db.session.flush()
    return user


def seed_dummy_providers():
    random.seed(42)
    services_by_name = {service.name: service for service in Service.query.all()}
    if not services_by_name:
        raise RuntimeError("No services found. Start the app once so default services are created.")

    for index, (name, category_name, specialties) in enumerate(PROVIDERS, start=1):
        slug = name.lower().replace(" ", ".")
        email = f"{slug}@bookglam.test"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                full_name=name,
                email=email,
                phone=f"081{random.randint(10000000, 99999999)}",
                password_hash=bcrypt.generate_password_hash("password").decode("utf-8"),
                role="provider",
                avatar=PHOTO_URLS[index % len(PHOTO_URLS)],
            )
            db.session.add(user)
            db.session.flush()

        profile = ProviderProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = ProviderProfile(user_id=user.id)
            db.session.add(profile)
            db.session.flush()

        profile.bio = (
            f"{name} is a {category_name.lower()} specialist known for refined finishes, "
            "clean tools and a calm BookGlam appointment experience."
        )
        profile.specialties = specialties
        profile.location = random.choice(["Lekki Phase 1", "Ikeja GRA", "Victoria Island", "Yaba", "Surulere", "Ikoyi"])
        profile.is_online = index % 3 != 0
        profile.is_verified = True
        profile.tier = random.choice(["standard", "premium", "premium", "basic"])
        profile.years_experience = random.randint(3, 12)
        profile.rating = round(random.uniform(4.7, 5.0), 1)
        profile.total_reviews = random.randint(18, 96)

        if ProviderPortfolio.query.filter_by(provider_id=profile.id).count() < 3:
            for offset in range(4):
                db.session.add(ProviderPortfolio(
                    provider_id=profile.id,
                    image_url=PORTFOLIO_URLS[(index + offset) % len(PORTFOLIO_URLS)],
                    caption=random.choice(["Clean finish", "Client favorite", "Soft luxury detail", "BookGlam-ready look"]),
                    service_tag=category_name,
                ))

        provider_services = find_services(category_name, specialties)
        review_count = Review.query.join(Booking).filter(Booking.provider_id == profile.id).count()
        for review_index in range(review_count, 3):
            client_user = get_or_create_review_client(index * 10 + review_index)
            service = random.choice(provider_services)
            booking = Booking(
                client_id=client_user.id,
                provider_id=profile.id,
                service_id=service.id,
                booking_type=random.choice(["home", "shop"]),
                service_tier=random.choice(["standard", "premium"]),
                status="completed",
                scheduled_at=datetime.utcnow() - timedelta(days=random.randint(4, 120)),
                address=random.choice(["Lekki, Lagos", "Ikeja, Lagos", "Victoria Island, Lagos"]),
                price=random.choice([8000, 12000, 15000, 20000, 30000]),
                payment_method=random.choice(["cash", "transfer", "card"]),
                payment_status="paid",
                notes="Seeded MVP booking for provider review.",
            )
            db.session.add(booking)
            db.session.flush()
            db.session.add(Review(
                booking_id=booking.id,
                rating=random.choice([5, 5, 5, 4]),
                comment=random.choice(REVIEW_COMMENTS),
            ))

    db.session.commit()
    print(f"Seeded {len(PROVIDERS)} dummy providers with portfolios and reviews.")


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        seed_dummy_providers()
