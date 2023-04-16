from pycountry import countries, subdivisions

ALL_ZONE = "ALL"
ZONE_CHOICES = (
    (ALL_ZONE, "all"),
    *((country.alpha_2, country.name) for country in countries),
    *((subdivision.code, subdivision.name) for subdivision in subdivisions),
)
