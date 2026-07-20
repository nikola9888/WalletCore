from kivy.utils import get_color_from_hex

# =========================================================
# WALLETCORE OCEAN WAVE THEME SYSTEM
# =========================================================


# =========================
# BACKGROUND
# =========================

BACKGROUND = get_color_from_hex("#0B3B66")       
BACKGROUND_DARK = get_color_from_hex("#082A4A")

# Ocean wave layers
OCEAN_1 = get_color_from_hex("#0B3B66")
OCEAN_2 = get_color_from_hex("#176B9E")
OCEAN_3 = get_color_from_hex("#2596BE")
OCEAN_4 = get_color_from_hex("#38BDF8")
# =========================
# OCEAN WAVE PATTERN
# =========================

WAVE_LIGHT = get_color_from_hex("#7DD3FC")   # svetlo plava
WAVE_WHITE = get_color_from_hex("#BAE6FD")   # skoro bela voda
WAVE_GLOW = get_color_from_hex("#E0F2FE")    # blagi beli sjaj

# =========================
# PREMIUM GLASS CARDS
# =========================

CARD = get_color_from_hex("#1B2430")
CARD_LIGHT = get_color_from_hex("#263445")

SURFACE = get_color_from_hex("#303B4A")
SURFACE_2 = get_color_from_hex("#3A4758")

# =========================
# PRIMARY COLORS
# =========================

PRIMARY = get_color_from_hex("#3B82F6")
PRIMARY_DARK = get_color_from_hex("#2563EB")

CYAN = get_color_from_hex("#06B6D4")
AQUA = get_color_from_hex("#22D3EE")


# =========================
# STATUS COLORS
# =========================

SUCCESS = get_color_from_hex("#22C55E")
WARNING = get_color_from_hex("#FACC15")
DANGER = get_color_from_hex("#EF4444")


# =========================
# TEXT
# =========================

WHITE = get_color_from_hex("#FFFFFF")
TEXT = get_color_from_hex("#F8FAFC")
TEXT_SECONDARY = get_color_from_hex("#CBD5E1")
TEXT_MUTED = get_color_from_hex("#94A3B8")


# =========================
# TRANSPARENCY
# =========================

GLASS = get_color_from_hex("#FFFFFF22")
SHADOW = get_color_from_hex("#00000066")


# =========================
# GLASS CATEGORY COLORS
# =========================

CATEGORY = {

    "food": get_color_from_hex("#F59E0B55"),
    "transport": get_color_from_hex("#3B82F655"),
    "shopping": get_color_from_hex("#A855F755"),
    "bills": get_color_from_hex("#EF444455"),
    "fun": get_color_from_hex("#22C55E55"),
    "health": get_color_from_hex("#06B6D455"),
    "salary": get_color_from_hex("#10B98155"),
    "other": get_color_from_hex("#94A3B855"),

}
# =========================
# PREMIUM GLASS CATEGORY CARDS
# =========================

CATEGORY_BG = {

    "food": get_color_from_hex("#163A5F99"),
    "transport": get_color_from_hex("#163A5F99"),
    "shopping": get_color_from_hex("#163A5F99"),
    "bills": get_color_from_hex("#163A5F99"),
    "fun": get_color_from_hex("#163A5F99"),
    "health": get_color_from_hex("#163A5F99"),
    "salary": get_color_from_hex("#163A5F99"),
    "other": get_color_from_hex("#163A5F99"),

}

SILVER = get_color_from_hex("#C4CBD6")
SILVER_MUTED = get_color_from_hex("#9CA8B8")
# =========================
# UI SETTINGS
# =========================

RADIUS_SMALL = 10
RADIUS = 26
RADIUS_LARGE = 32

PADDING = 16
PADDING_LARGE = 24

SPACING = 12
SPACING_SMALL = 20


# =========================
# TYPOGRAPHY
# =========================

TITLE = 50
SUBTITLE = 22
BODY = 17
SMALL = 14
TINY = 12


def darken(color, factor=0.8):

    r, g, b, a = color

    return (
        r * factor,
        g * factor,
        b * factor,
        a
    )
