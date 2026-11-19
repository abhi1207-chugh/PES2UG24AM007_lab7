"""Input-safe helpers for the event ticketing application."""


def decode_promo_voucher(voucher_code):
    """Return a formatted voucher or a clear validation message."""
    if not isinstance(voucher_code, str):
        return "Invalid voucher code"

    parts = voucher_code.strip().split("-")
    if len(parts) != 2:
        return "Invalid voucher code"

    prefix, pct_str = (part.strip() for part in parts)
    if not prefix.isalpha():
        return "Invalid voucher code"

    try:
        percentage = int(pct_str)
    except ValueError:
        return "Invalid voucher code"

    if not 0 <= percentage <= 100:
        return "Invalid voucher code"

    return f"Valid {prefix.upper()}: {percentage}% OFF"


def calculate_seat_tier_price(tier_spec):
    """Calculate a ticket price from ``TIER@ROW`` without raising errors."""
    if not isinstance(tier_spec, str):
        return "Invalid tier specification"

    parts = tier_spec.strip().split("@")
    if len(parts) != 2:
        return "Invalid tier specification"

    tier, row_str = (part.strip() for part in parts)
    tier_rates = {
        "VIP": 150.0,
        "PREMIUM": 90.0,
        "GENERAL": 45.0,
    }
    base = tier_rates.get(tier.upper())
    if base is None:
        return "Invalid tier specification"

    try:
        row = int(row_str)
    except ValueError:
        return "Invalid tier specification"

    if row < 1:
        return "Invalid tier specification"

    return base + (row * 2.0)


def parse_attendee_badge(badge_csv):
    """Format a badge from ``Name,Age,Seat`` or report invalid input."""
    if not isinstance(badge_csv, str):
        return "Invalid attendee badge"

    tokens = [token.strip() for token in badge_csv.split(",")]
    if len(tokens) != 3:
        return "Invalid attendee badge"

    name, age_str, seat = tokens
    if not name or not seat:
        return "Invalid attendee badge"

    try:
        age = int(age_str)
    except ValueError:
        return "Invalid attendee badge"

    if not 0 <= age <= 120:
        return "Invalid attendee badge"

    category = "Child" if age < 18 else "Adult"
    return f"{name} [{category}] - Seat {seat}"

def main():
    print("==== Running decode_promo_voucher ====")
    v_input = input("Enter voucher (e.g. EARLY-20): ")
    print("Voucher:", decode_promo_voucher(v_input))

    print("\n==== Running calculate_seat_tier_price ====")
    t_input = input("Enter tier spec (e.g. VIP@4): ")
    print("Seat Price: $", calculate_seat_tier_price(t_input))

    print("\n==== Running parse_attendee_badge ====")
    b_input = input("Enter badge CSV (Name,Age,Seat): ")
    print("Badge:", parse_attendee_badge(b_input))

if __name__ == "__main__":
    main()
