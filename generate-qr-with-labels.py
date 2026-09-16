#!/usr/bin/env python3
"""
Bangalore Exhibition - QR Code Generator WITH LABELS
Generates QR codes with the brand name and catalog/model name printed
underneath each one. Only the label text is added below the QR — the
QR's scannable pixel data is unaffected by brand/name changes.
"""

import os
import sys

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Missing packages. Install with:")
    print("   pip install qrcode[pil] pillow")
    sys.exit(1)

# (model name, pdf filename, brand)
catalogs = [
    ('DEX32_52DM', 'DEX32_52DM.pdf', 'HUATANG LOIVA'),
    ('DY 1411PSF-D', 'DY 1411PSF-D.pdf', 'DUKE'),
    ('DY 1509 PD', 'DY 1509 PD.pdf', 'DUKE'),
    ('DY 1790S', 'DY 1790S.pdf', 'DUKE'),
    ('DY 2210G', 'DY 2210G.pdf', 'DUKE'),
    ('DY 3020', 'DY 3020.pdf', 'DUKE'),
    ('DY 430GT-01', 'DY 430GT-01.pdf', 'DUKE'),
    ('DY 438GT LA 971', 'DY 438GT LA 971.pdf', 'DUKE'),
    ('DY 4406P-D', 'DY 4406P-D.pdf', 'DUKE'),
    ('DY 5030', 'DY 5030.pdf', 'DUKE'),
    ('DY GC510-360 SERIES', 'DY GC510-360 SERIES.pdf', 'DUKE'),
    ('DY R9', 'DY R9.pdf', 'DUKE'),
    ('FB 450-12-0640', 'FB 450-12-0640.pdf', 'HUATANG LOIVA'),
    ('FB450', 'FB450.pdf', 'HUATANG LOIVA'),
    ('IEX32_52DM', 'IEX32_52DM.pdf', 'HUATANG LOIVA'),
    ('JT A8', 'JT A8.pdf', 'JUITA'),
    ('JTK 18F', 'JTK 18F.pdf', 'JUITA'),
    ('JTK6-60A', 'JTK6-60A.pdf', 'JUITA'),
    ('LS6021NP', 'LS6021NP.pdf', 'LENSH'),
    ('LS9231C', 'LS9231C.pdf', 'LENSH'),
    ('NF 1104_1106', 'NF 1104_1106.pdf', 'HUATANG LOIVA'),
    ('VIOS 669', 'VIOS 669.pdf', 'VIOS'),
    ('VIOS 867', 'VIOS 867.pdf', 'VIOS'),
    ('VIOS 868', 'VIOS 868.pdf', 'VIOS'),
    ('DY G36', 'DY G36.pdf', 'DUKE'),
    ('LOIVA ST21', 'LOIVA ST21.pdf', 'HUATANG LOIVA'),
    ('DUKE Q1 Tagging Machine', 'DUKE Q1_Tagging Machine.pdf', 'DUKE'),
    ('DY 878', 'DY 878.pdf', 'DUKE'),
]

# ============================================================
# IMPORTANT: Set this to your final website URL before printing
# ============================================================
BASE_URL = 'https://blr-exhibition.vercel.app'

QR_SIZE = 400           # QR code image size (px, square) — never changes
BRAND_FONT_SIZE = 20
MODEL_FONT_SIZE = 26
LABEL_HEIGHT = 130      # fixed space below QR for brand + model text
PADDING = 20
LINE_GAP = 10           # gap between brand line and model line(s)


def sanitize_filename(text):
    return "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in text)


def get_font(size, bold=True):
    """Try a few common fonts, fall back to PIL default."""
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        test = (current + ' ' + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered_line(draw, line, y, canvas_w, font, fill):
    bbox = draw.textbbox((0, 0), line, font=font)
    text_w = bbox[2] - bbox[0]
    x = (canvas_w - text_w) // 2
    draw.text((x, y), line, fill=fill, font=font)


def make_labeled_qr(data_url, brand_text, model_text, out_path):
    # --- QR pixel data: depends only on data_url, nothing else below
    # touches this, so relabeling never changes what the QR scans to.
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(data_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='#8b2e2e', back_color='#ffffff').convert('RGB')
    qr_img = qr_img.resize((QR_SIZE, QR_SIZE))

    canvas_w = QR_SIZE + PADDING * 2
    canvas_h = QR_SIZE + PADDING * 2 + LABEL_HEIGHT
    canvas = Image.new('RGB', (canvas_w, canvas_h), '#ffffff')
    canvas.paste(qr_img, (PADDING, PADDING))

    draw = ImageDraw.Draw(canvas)
    brand_font = get_font(BRAND_FONT_SIZE, bold=False)
    model_font = get_font(MODEL_FONT_SIZE, bold=True)
    max_width = canvas_w - PADDING * 2

    model_lines = wrap_text(draw, model_text, model_font, max_width)

    brand_line_height = BRAND_FONT_SIZE + 6
    model_line_height = MODEL_FONT_SIZE + 6
    total_height = brand_line_height + LINE_GAP + model_line_height * len(model_lines)

    y = PADDING + QR_SIZE + max(0, (LABEL_HEIGHT - total_height) // 2)

    # Brand name (smaller, accent color, uppercase)
    draw_centered_line(draw, brand_text.upper(), y, canvas_w, brand_font, fill='#8b2e2e')
    y += brand_line_height + LINE_GAP

    # Model name (bold, dark, possibly wrapped over multiple lines)
    for line in model_lines:
        draw_centered_line(draw, line, y, canvas_w, model_font, fill='#1a1a1a')
        y += model_line_height

    canvas.save(out_path)


def generate_all():
    os.makedirs('qr-codes', exist_ok=True)

    print(f'Generating labeled QR codes -> {BASE_URL}\n')

    # Main gallery QR (no single brand, so just a category label)
    make_labeled_qr(
        f'{BASE_URL}/index.html',
        'EXHIBITION',
        'ALL CATALOGS',
        'qr-codes/00_MAIN-GALLERY_All_Catalogs.png'
    )
    print('Generated: 00_MAIN-GALLERY_All_Catalogs.png  [EXHIBITION / ALL CATALOGS]')

    for idx, (name, filename, brand) in enumerate(catalogs, 1):
        catalog_url = f'{BASE_URL}/index.html?catalog={idx}'
        clean_name = sanitize_filename(name)
        out_file = f'qr-codes/{str(idx).zfill(2)}_{clean_name}.png'
        make_labeled_qr(catalog_url, brand, name, out_file)
        print(f'Generated: {out_file}  [{brand} / {name}]')

    print('\nAll QR codes generated with brand + model labels underneath!')
    print('Location: qr-codes/ folder')
    print('\nIMPORTANT: Update BASE_URL at the top of this script')
    print(f'Current BASE_URL: {BASE_URL}')


if __name__ == '__main__':
    generate_all()
