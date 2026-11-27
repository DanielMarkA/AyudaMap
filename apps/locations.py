import re


CITY_GROUPS = (
    (
        'Metro Manila (NCR)',
        (
            'Caloocan',
            'Las Piñas',
            'Makati',
            'Malabon',
            'Mandaluyong',
            'Manila',
            'Marikina',
            'Muntinlupa',
            'Navotas',
            'Parañaque',
            'Pasay',
            'Pasig',
            'Pateros',
            'Quezon City',
            'San Juan',
            'Taguig',
            'Valenzuela',
        ),
    ),
    (
        'Luzon',
        (
            'Alaminos',
            'Angeles City',
            'Antipolo',
            'Bacoor',
            'Baguio City',
            'Balanga',
            'Batac',
            'Batangas City',
            'Biñan',
            'Cabanatuan',
            'Cabuyao',
            'Calamba',
            'Calapan',
            'Candon',
            'Cauayan',
            'Cavite City',
            'Dagupan',
            'Dasmariñas',
            'Gapan',
            'General Trias',
            'Ilagan',
            'Imus',
            'Iriga',
            'Laoag',
            'Legazpi City',
            'Ligao',
            'Lipa',
            'Lucena',
            'Mabalacat',
            'Malolos',
            'Masbate City',
            'Meycauayan',
            'Muñoz',
            'Naga City',
            'Olongapo',
            'Palayan',
            'Puerto Princesa',
            'San Carlos (Pangasinan)',
            'San Fernando (La Union)',
            'San Fernando (Pampanga)',
            'San Jose (Nueva Ecija)',
            'San Jose del Monte',
            'San Pablo',
            'San Pedro',
            'Santa Rosa',
            'Santiago',
            'Sorsogon City',
            'Tabaco',
            'Tabuk',
            'Tagaytay',
            'Tanauan',
            'Tarlac City',
            'Tayabas',
            'Trece Martires',
            'Tuguegarao',
            'Urdaneta',
            'Vigan',
        ),
    ),
    (
        'Visayas',
        (
            'Bacolod City',
            'Bago',
            'Bais',
            'Bayawan',
            'Baybay',
            'Bogo',
            'Borongan',
            'Cadiz',
            'Calbayog',
            'Canlaon',
            'Carcar',
            'Catbalogan',
            'Cebu City',
            'Danao',
            'Dumaguete',
            'Escalante',
            'Guihulngan',
            'Himamaylan',
            'Iloilo City',
            'Kabankalan',
            'La Carlota',
            'Lapu-Lapu City',
            'Maasin',
            'Mandaue City',
            'Naga (Cebu)',
            'Ormoc',
            'Passi',
            'Roxas City',
            'Sagay',
            'San Carlos (Negros Occidental)',
            'Silay',
            'Sipalay',
            'Tacloban City',
            'Tagbilaran',
            'Talisay (Cebu)',
            'Talisay (Negros Occidental)',
            'Tanjay',
            'Toledo',
            'Victorias',
        ),
    ),
    (
        'Mindanao',
        (
            'Bayugan',
            'Bislig',
            'Butuan',
            'Cabadbaran',
            'Cagayan de Oro',
            'Cotabato City',
            'Dapitan',
            'Davao City',
            'Digos',
            'Dipolog',
            'El Salvador',
            'General Santos',
            'Gingoog',
            'Iligan',
            'Isabela City',
            'Kidapawan',
            'Koronadal',
            'Lamitan',
            'Malaybalay',
            'Marawi',
            'Mati',
            'Oroquieta',
            'Ozamiz',
            'Pagadian',
            'Panabo',
            'Samal',
            'Surigao City',
            'Tacurong',
            'Tagum',
            'Tandag',
            'Tangub',
            'Valencia',
            'Zamboanga City',
        ),
    ),
)

CITY_CHOICES = tuple(
    (group_name, tuple((city, city) for city in cities))
    for group_name, cities in CITY_GROUPS
)

OPTIONAL_CITY_CHOICES = (('', 'Select city (optional)...'),) + CITY_CHOICES
REQUIRED_CITY_CHOICES = (('', 'Select city...'),) + CITY_CHOICES

ALL_CANONICAL_CITIES = tuple(
    city for _, cities in CITY_GROUPS for city in cities
)
_CANONICAL_BY_LOWER = {city.lower(): city for city in ALL_CANONICAL_CITIES}

CITY_ALIASES = {
    'city of manila': 'Manila',
    'manila city': 'Manila',
    'qc': 'Quezon City',
    'quezon': 'Quezon City',
    'cebu': 'Cebu City',
    'davao': 'Davao City',
    'iloilo': 'Iloilo City',
    'baguio': 'Baguio City',
    'bacolod': 'Bacolod City',
    'cdo': 'Cagayan de Oro',
    'cagayan de oro city': 'Cagayan de Oro',
    'gensan': 'General Santos',
    'general santos city': 'General Santos',
    'zamboanga': 'Zamboanga City',
    'angeles': 'Angeles City',
    'batangas': 'Batangas City',
    'legazpi': 'Legazpi City',
    'tacloban': 'Tacloban City',
    'roxas': 'Roxas City',
    'surigao': 'Surigao City',
    'cotabato': 'Cotabato City',
    'lapu-lapu': 'Lapu-Lapu City',
    'mandaue': 'Mandaue City',
    'bgc': 'Taguig',
    'paranaque': 'Parañaque',
    'paranaque city': 'Parañaque',
    'las pinas': 'Las Piñas',
    'las pinas city': 'Las Piñas',
    'dasmarinas': 'Dasmariñas',
    'binan': 'Biñan',
    'munoz': 'Muñoz',
}


def normalize_city(value):
    """Map case/format variants (e.g. 'manila city', 'qc') to a canonical city name."""
    cleaned = ' '.join((value or '').strip().split())
    if not cleaned:
        return ''

    lowered = cleaned.lower()
    if lowered in _CANONICAL_BY_LOWER:
        return _CANONICAL_BY_LOWER[lowered]
    if lowered in CITY_ALIASES:
        return CITY_ALIASES[lowered]

    if lowered.endswith(' city'):
        base = lowered[:-5].strip()
        if base in _CANONICAL_BY_LOWER:
            return _CANONICAL_BY_LOWER[base]
        if base in CITY_ALIASES:
            return CITY_ALIASES[base]

    with_city = f'{lowered} city'
    if with_city in _CANONICAL_BY_LOWER:
        return _CANONICAL_BY_LOWER[with_city]

    return cleaned


def infer_city_from_text(text):
    """Infer a canonical city from a free-text address, ignoring 'Metro Manila'."""
    cleaned = ' '.join((text or '').strip().split())
    if not cleaned:
        return ''

    normalized = normalize_city(cleaned)
    if normalized in _CANONICAL_BY_LOWER.values():
        return normalized

    searchable = re.sub(r'\bmetro\s+manila\b', '', cleaned, flags=re.IGNORECASE)
    for city in sorted(ALL_CANONICAL_CITIES, key=len, reverse=True):
        if re.search(rf'(?<!\w){re.escape(city)}(?!\w)', searchable, flags=re.IGNORECASE):
            return city

    for alias, canonical in sorted(CITY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf'(?<!\w){re.escape(alias)}(?!\w)', searchable, flags=re.IGNORECASE):
            return canonical

    return ''
