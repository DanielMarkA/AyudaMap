"""
Seed script to populate Supabase PostgreSQL database with initial AyudaMap data:
- Superuser / Demo accounts & Profiles with volunteer/org flags
- UserSettings
- Verified Community Aid Resources with coordinates, operating status & volunteer ownership
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
        admin_user.set_password('AdminAyuda2026!')
        admin_user.save()
        print("Superuser 'admin' updated.")

    admin_profile, _ = Profile.objects.get_or_create(user=admin_user)
    admin_profile.full_name = 'AyudaMap National Coordinator'
    admin_profile.bio = 'National disaster relief & community aid operations manager.'
    admin_profile.phone_number = '+63 917 888 0001'
    admin_profile.city = 'Manila City'
    admin_profile.organization = 'AyudaMap National Relief Ops'
    admin_profile.is_volunteer = True
    admin_profile.save()

    admin_settings, _ = UserSettings.objects.get_or_create(user=admin_user)
    admin_settings.dark_mode = False
    admin_settings.email_notifications = True
    admin_settings.preferred_category = 'ALL'
    admin_settings.save()

    # 2. Create Regular Demo Volunteer User
    demo_user, created = User.objects.get_or_create(
        username='juan_delacruz',
        defaults={'email': 'juan.delacruz@gmail.com'}
    )
    if created:
        demo_user.set_password('AyudaPass123!')
        demo_user.save()
        print("Created demo user 'juan_delacruz' with password 'AyudaPass123!'")
    else:
        demo_user.set_password('AyudaPass123!')
        demo_user.save()
        print("Demo user 'juan_delacruz' updated.")

    demo_profile, _ = Profile.objects.get_or_create(user=demo_user)
    demo_profile.full_name = 'Juan Dela Cruz'
    demo_profile.bio = 'Community volunteer and relief goods coordinator in Quezon City.'
    demo_profile.phone_number = '+63 928 555 4321'
    demo_profile.city = 'Quezon City'
    demo_profile.organization = 'QC Community Relief Network'
    demo_profile.is_volunteer = True
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
            'status': 'OPERATIONAL',
            'description': 'Emergency first aid, blood donation dispatch, and ambulance services available 24/7.',
            'location': '37 EDSA corner Boni Ave, Mandaluyong, Metro Manila',
            'latitude': 14.5772,
            'longitude': 121.0478,
            'operating_hours': '24/7 Open',
            'contact_info': '(02) 8790 2300 / 143',
            'is_verified': True,
            'created_by': admin_user,
        },
        {
            'name': 'QC Food Relief & Community Pantry Hub',
            'category': 'FOOD',
            'status': 'OPERATIONAL',
            'description': 'Daily hot meals, food ration distribution, and grocery packs for families in need.',
            'location': 'Maginhawa St, Teachers Village East, Quezon City',
            'latitude': 14.6465,
            'longitude': 121.0594,
            'operating_hours': '7:00 AM - 6:00 PM',
            'contact_info': '+63 919 123 4567',
            'is_verified': True,
            'created_by': demo_user,
        },
        {
            'name': 'Marikina Sports Center Evacuation & Relief Shelter',
            'category': 'SHELTER',
            'status': 'FULL_CAPACITY',
            'description': 'Designated high-capacity flood evacuation center with clean sleeping mats, portalets, and medical tent.',
            'location': 'Sumulong Hwy, Marikina, Metro Manila',
            'latitude': 14.6367,
            'longitude': 121.0978,
            'operating_hours': '24/7 During Calamities',
            'contact_info': '(02) 8646 0424',
            'is_verified': True,
            'created_by': admin_user,
        },
        {
            'name': 'DSWD National Operations & Ayuda Desk',
            'category': 'GOV',
            'status': 'OPERATIONAL',
            'description': 'Assistance to Individuals in Crisis Situations (AICS), financial aid, and emergency voucher processing.',
            'location': 'Batasan Complex, Constitution Hills, Quezon City',
            'latitude': 14.6937,
            'longitude': 121.0945,
            'operating_hours': '8:00 AM - 5:00 PM (Mon-Fri)',
            'contact_info': '(02) 8931 8101',
            'is_verified': True,
            'created_by': admin_user,
        },
        {
            'name': 'Tondo Community Donation Drop-off Center',
            'category': 'DONATION',
            'status': 'OPERATIONAL',
            'description': 'Accepts canned goods, bottled water, hygiene kits, blankets, and children clothing for distribution.',
            'location': 'Rizal Ave near Tayuman, Tondo, Manila',
            'latitude': 14.6198,
            'longitude': 120.9825,
            'operating_hours': '9:00 AM - 5:00 PM',
            'contact_info': '+63 915 789 0123',
            'is_verified': True,
            'created_by': demo_user,
        },
        {
            'name': 'St. Jude Community Clinic & Medical Aid',
            'category': 'MEDICAL',
            'status': 'OPERATIONAL',
            'description': 'Free outpatient medical checkups, essential medicines, and maternal healthcare assistance.',
            'location': 'Sampaloc, Manila',
            'latitude': 14.6056,
            'longitude': 120.9922,
            'operating_hours': '8:00 AM - 4:00 PM (Mon-Sat)',
            'contact_info': '(02) 8735 6281',
            'is_verified': True,
            'created_by': admin_user,
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
            for k, v in item.items():
                setattr(res, k, v)
            res.save()
            print(f"Updated resource: '{res.name}'")

    print("\nDatabase seeding completed successfully!")

if __name__ == '__main__':
    run()
