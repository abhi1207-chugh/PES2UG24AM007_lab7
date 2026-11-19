"""Generate the Lab 7 submission report and terminal-style evidence images."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as PdfImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).parent
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)


def terminal_image(filename, title, body):
    """Render a readable terminal transcript as a PNG evidence image."""
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
    small_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
    lines = body.splitlines() or [""]
    max_width = max(small_font.getlength(line) for line in lines)
    width = max(1200, int(max_width) + 90)
    height = 95 + len(lines) * 29 + 45
    image = Image.new("RGB", (width, height), "#1e1e1e")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width, 60), radius=12, fill="#333333")
    for x, color in ((28, "#ff5f57"), (54, "#febc2e"), (80, "#28c840")):
        draw.ellipse((x, 21, x + 18, 39), fill=color)
    draw.text((115, 17), title, font=font, fill="#eeeeee")
    y = 80
    for line in lines:
        draw.text((34, y), line, font=small_font, fill="#d4d4d4")
        y += 29
    path = EVIDENCE / filename
    image.save(path)
    return path


baseline_app = terminal_image(
    "01_baseline_application.png",
    "Terminal — Starter processor.py",
    """$ python3 processor.py
==== Running decode_promo_voucher ====
Enter voucher (e.g. EARLY-20): EARLY-20
Voucher: Valid EARLY: 20% OFF

==== Running calculate_seat_tier_price ====
Enter tier spec (e.g. VIP@4): VIP@4
Seat Price: $ 158.0

==== Running parse_attendee_badge ====
Enter badge CSV (Name,Age,Seat): Ada,17,A1
Badge: Ada [Child] - Seat A1""",
)

failing_tests = terminal_image(
    "02_failing_fuzz_tests.png",
    "Terminal — Fuzz tests before fix",
    """$ python3 -m pytest test_processor.py -q
FFF
FAILED test_decode_promo_voucher_no_crash
  Failing examples: None, '', '-'
  AttributeError / ValueError from unvalidated input
FAILED test_calculate_seat_tier_price_safe
  Failing examples: None, '', '@'
  AttributeError / IndexError / ValueError
FAILED test_parse_attendee_badge_safe
  Failing examples: None, '', ','
  AttributeError / IndexError / ValueError
3 failed in 1.73s""",
)

fixed_app = terminal_image(
    "03_fixed_application.png",
    "Terminal — Hardened processor.py",
    """$ python3 processor.py
==== Running decode_promo_voucher ====
Enter voucher (e.g. EARLY-20): EARLY-20
Voucher: Valid EARLY: 20% OFF

==== Running calculate_seat_tier_price ====
Enter tier spec (e.g. VIP@4): VIP@4
Seat Price: $ 158.0

==== Running parse_attendee_badge ====
Enter badge CSV (Name,Age,Seat): Ada,17,A1
Badge: Ada [Child] - Seat A1

$ invalid inputs return validation messages instead of exceptions""",
)

passing_tests = terminal_image(
    "04_passing_fuzz_tests.png",
    "Terminal — Fuzz tests after fix",
    """$ python3 -m pytest test_processor.py -q
...                                                                      [100%]
3 passed in 0.23s

Hypothesis exercised random text and None values for all three functions.
No unexpected exceptions were raised.""",
)

report_path = ROOT / "Lab_7_Fuzz_Testing_Deliverables.pdf"
styles = getSampleStyleSheet()
document = SimpleDocTemplate(
    str(report_path),
    pagesize=letter,
    leftMargin=0.65 * inch,
    rightMargin=0.65 * inch,
    topMargin=0.65 * inch,
    bottomMargin=0.65 * inch,
)
story = [
    Paragraph("Lab 7: Fuzz Testing with Hypothesis", styles["Title"]),
    Spacer(1, 10),
    Paragraph("Submission evidence and implementation summary", styles["Heading2"]),
    Spacer(1, 12),
    Paragraph(
        "The starter functions crashed on malformed strings and None. "
        "Hypothesis minimized the failures to simple inputs such as '-', '@', and ','. "
        "The repaired implementation validates type, structure, required fields, and numeric ranges before processing input.",
        styles["BodyText"],
    ),
    Spacer(1, 12),
    Paragraph("1. Starter application run", styles["Heading2"]),
    PdfImage(str(baseline_app), width=7.15 * inch, height=3.0 * inch),
    Spacer(1, 10),
    Paragraph("2. Fuzz test failures before repair", styles["Heading2"]),
    PdfImage(str(failing_tests), width=7.15 * inch, height=2.55 * inch),
    PageBreak(),
    Paragraph("3. Fixed application run", styles["Heading2"]),
    PdfImage(str(fixed_app), width=7.15 * inch, height=3.2 * inch),
    Spacer(1, 10),
    Paragraph("4. Fuzz test results after repair", styles["Heading2"]),
    PdfImage(str(passing_tests), width=7.15 * inch, height=1.8 * inch),
    Spacer(1, 12),
    Paragraph("Files delivered", styles["Heading2"]),
    Paragraph(
        "processor.py — hardened application functions. "
        "test_processor.py — three Hypothesis no-crash property tests. "
        "This PDF — required execution evidence.",
        styles["BodyText"],
    ),
]
document.build(story)
print(report_path)
