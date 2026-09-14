"""
Seed script to populate Supabase PostgreSQL database with initial AyudaMap data:
- Superuser / Demo accounts
- Profiles & UserSettings
- Verified Community Aid Resources with coordinates & contact info
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.profile.models import Profile
from apps.user_settings.models import UserSettings
from apps.home.models import Resource

def run():
    print("Seeding Supabase database...")

    # 1. Create Admin User
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@ayudamap.ph', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        admin_user.set_password('AdminAyuda2026!')
        admin_user.save()
        print("Created superuser 'admin' with password 'AdminAyuda2026!'")
    else:
        print("Superuser 'admin' already exists.")

    admin_profile, _ = Profile.objects.get_or_create(user=admin_user)
    admin_profile.full_name = 'AyudaMap Admin Coordinator'
    admin_profile.bio = 'National disaster relief & community aid operations manager.'
    admin_profile.phone_number = '+63 917 888 0001'
    admin_profile.city = 'Manila City'
    admin_profile.save()

    admin_settings, _ = UserSettings.objects.get_or_create(user=admin_user)
    admin_settings.dark_mode = False
    admin_settings.email_notifications = True
    admin_settings.preferred_category = 'ALL'
    admin_settings.save()

    # 2. Create Regular Demo User
    demo_user, created = User.objects.get_or_create(
        username='juan_delacruz',
        defaults={'email': 'juan.delacruz@gmail.com'}
    )
    if created:
        demo_user.set_password('AyudaPass123!')
        demo_user.save()
        print("Created demo user 'juan_delacruz' with password 'AyudaPass123!'")

    demo_profile, _ = Profile.objects.get_or_create(user=demo_user)
    demo_profile.full_name = 'Juan Dela Cruz'
    demo_profile.bio = 'Community volunteer and relief goods coordinator in Quezon City.'
    demo_profile.phone_number = '+63 928 555 4321'
    demo_profile.city = 'Quezon City'
    demo_profile.save()

    demo_settings, _ = UserSettings.objects.get_or_create(user=demo_user)
    demo_settings.dark_mode = True
    demo_settings.email_notifications = True
    demo_settings.preferred_category = 'FOOD'
    demo_settings.save()

    # 3. Seed Community Resources
    resources_data = [
        {
            'name': 'Philippine Red Cross - National HQ',
            'category': 'MEDICAL',
            'description': 'Emergency first aid, blood donation dispatch, and ambulance services available 24/7.',
            'location': '37 EDSA corner Boni Ave, Mandaluyong, Metro Manila',
            'latitude': 14.5772,
            'longitude': 121.0478,
            'operating_hours': '24/7 Open',
            'contact_info': '(02) 8790 2300 / 143',
            'is_verified': True,
        },
        {
            'name': 'QC Food Relief & Community Pantry Hub',
            'category': 'FOOD',
            'description': 'Daily hot meals, food ration distribution, and grocery packs for families in need.',
            'location': 'Maginhawa St, Teachers Village East, Quezon City',
            'latitude': 14.6465,
            'longitude': 121.0594,
            'operating_hours': '7:00 AM - 6:00 PM',
            'contact_info': '+63 919 123 4567',
            'is_verified': True,
        },
        {
            'name': 'Marikina Sports Center Evacuation & Relief Shelter',
            'category': 'SHELTER',
            'description': 'Designated high-capacity flood evacuation center with clean sleeping mats, portalets, and medical tent.',
            'location': 'Sumulong Hwy, Marikina, Metro Manila',
            'latitude': 14.6367,
            'longitude': 121.0978,
            'operating_hours': '24/7 During Calamities',
            'contact_info': '(02) 8646 0424',
            'is_verified': True,
        },
        {
            'name': 'DSWD National Operations & Ayuda Desk',
            'category': 'GOV',
            'description': 'Assistance to Individuals in Crisis Situations (AICS), financial aid, and emergency voucher processing.',
            'location': 'Batasan Complex, Constitution Hills, Quezon City',
            'latitude': 14.6937,
            'longitude': 121.0945,
            'operating_hours': '8:00 AM - 5:00 PM (Mon-Fri)',
            'contact_info': '(02) 8931 8101',
            'is_verified': True,
        },
        {
            'name': 'Tondo Community Donation Drop-off Center',
            'category': 'DONATION',
            'description': 'Accepts canned goods, bottled water, hygiene kits, blankets, and children clothing for distribution.',
            'location': 'Rizal Ave near Tayuman, Tondo, Manila',
            'latitude': 14.6198,
            'longitude': 120.9825,
            'operating_hours': '9:00 AM - 5:00 PM',
            'contact_info': '+63 915 789 0123',
            'is_verified': True,
        },
        {
            'name': 'St. Jude Community Clinic & Medical Aid',
            'category': 'MEDICAL',
            'description': 'Free outpatient medical checkups, essential medicines, and maternal healthcare assistance.',
            'location': 'Sampaloc, Manila',
            'latitude': 14.6056,
            'longitude': 120.9922,
            'operating_hours': '8:00 AM - 4:00 PM (Mon-Sat)',
            'contact_info': '(02) 8735 6281',
            'is_verified': True,
        },
    ]

    for item in resources_data:
        res, is_new = Resource.objects.get_or_create(
            name=item['name'],
            defaults=item
        )
        if is_new:
            print(f"Created resource: {res.name}")
        else:
            print(f"Resource '{res.name}' already exists.")

    print("\nDatabase seeding completed successfully!")

if __name__ == '__main__':
    run()

