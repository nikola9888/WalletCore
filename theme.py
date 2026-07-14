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
# SURFACES / CARDS
# =========================

CARD = get_color_from_hex("#12304A")
CARD_LIGHT = get_color_from_hex("#184B70")

SURFACE = get_color_from_hex("#1E5A85")
SURFACE_2 = get_color_from_hex("#277AA8")

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
# CATEGORY COLORS
# =========================

CATEGORY = {

    "food": get_color_from_hex("#FFB703"),        # hrana - zlatna
    "transport": get_color_from_hex("#3B82F6"),   # prevoz - plava
    "shopping": get_color_from_hex("#C084FC"),    # kupovina - ljubičasta
    "bills": get_color_from_hex("#F43F5E"),       # računi - crvena
    "fun": get_color_from_hex("#34D399"),         # zabava - zelena
    "health": get_color_from_hex("#22D3EE"),      # zdravlje - cyan
    "salary": get_color_from_hex("#4ADE80"),      # plata - svetlo zelena
    "other": get_color_from_hex("#94A3B8"),       # ostalo - siva

}

# =========================
# CATEGORY CARD BACKGROUNDS
# =========================

CATEGORY_BG = {

    "food": get_color_from_hex("#B8C2CC"),
    "transport": get_color_from_hex("#B8C2CC"),
    "shopping": get_color_from_hex("#B8C2CC"),
    "bills": get_color_from_hex("#B8C2CC"),
    "fun": get_color_from_hex("#B8C2CC"),
    "health": get_color_from_hex("#B8C2CC"),
    "salary": get_color_from_hex("#B8C2CC"),
    "other": get_color_from_hex("#B8C2CC"),

}
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