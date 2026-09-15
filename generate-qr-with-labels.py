#!/usr/bin/env python3
"""
Bangalore Exhibition - QR Code Generator WITH LABELS
Generates QR codes with the catalog/model name printed underneath each one
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

catalogs = [
    ('DEX32_52DM', 'DEX32_52DM.pdf'),
    ('DY 1411PSF-D', 'DY 1411PSF-D.pdf'),
    ('DY 1509 PD', 'DY 1509 PD.pdf'),
    ('DY 1790S', 'DY 1790S.pdf'),
    ('DY 2210G', 'DY 2210G.pdf'),
    ('DY 3020', 'DY 3020.pdf'),
    ('DY 430GT-01', 'DY 430GT-01.pdf'),
    ('DY 438GT LA 971', 'DY 438GT LA 971.pdf'),
    ('DY 4406P-D', 'DY 4406P-D.pdf'),
    ('DY 5030', 'DY 5030.pdf'),
    ('DY GC510-360 SERIES', 'DY GC510-360 SERIES.pdf'),
    ('DY R9', 'DY R9.pdf'),
    ('FB 450-12-0640', 'FB 450-12-0640.pdf'),
    ('FB450', 'FB450.pdf'),
    ('IEX32_52DM', 'IEX32_52DM.pdf'),
    ('JT A8', 'JT A8.pdf'),
    ('JTK 18F', 'JTK 18F.pdf'),
    ('JTK6-60A', 'JTK6-60A.pdf'),
    ('LS6021NP', 'LS6021NP.pdf'),
    ('LS9231C', 'LS9231C.pdf'),
    ('NF 1104_1106', 'NF 1104_1106.pdf'),
    ('VIOS 669', 'VIOS 669.pdf'),
    ('VIOS 867', 'VIOS 867.pdf'),
    ('VIOS 868', 'VIOS 868.pdf'),
    ('DY G36', 'DY G36.pdf'),
    ('LOIVA ST21', 'LOIVA ST21.pdf'),
    ('DUKE Q1 Tagging Machine', 'DUKE Q1_Tagging Machine.pdf'),
]

# ============================================================
# IMPORTANT: Set this to your final website URL before printing
# ============================================================
BASE_URL = 'https://blr-exhibition.vercel.app'

QR_SIZE = 400          # QR code image size (px, square)
LABEL_HEIGHT = 70       # space reserved for text below QR
FONT_SIZE = 26
PADDING = 20


def sanitize_filename(text):
    return "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in text)


def get_font(size):
    """Try a few common fonts, fall back to PIL default."""
    candidates = [
        "arialbd.ttf",              # Windows bold
        "arial.ttf",                # Windows
        "DejaVuSans-Bold.ttf",      # Linux
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_labeled_qr(data_url, label_text, out_path):
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
    font = get_font(FONT_SIZE)

    # Wrap text if too long for the canvas width
    max_width = canvas_w - PADDING * 2
    words = label_text.split(' ')
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

    # Vertically center the (possibly 2-line) label in the label area
    line_height = FONT_SIZE + 6
    total_text_height = line_height * len(lines)
    text_y = PADDING + QR_SIZE + (LABEL_HEIGHT - total_text_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = (canvas_w - text_w) // 2
        draw.text((text_x, text_y), line, fill='#1a1a1a', font=font)
        text_y += line_height

    canvas.save(out_path)


def generate_all():
    os.makedirs('qr-codes', exist_ok=True)

    print(f'Generating labeled QR codes -> {BASE_URL}\n')

    # Main gallery QR
    make_labeled_qr(
        f'{BASE_URL}/index.html',
        'ALL CATALOGS',
        'qr-codes/00_MAIN-GALLERY_All_Catalogs.png'
    )
    print('Generated: 00_MAIN-GALLERY_All_Catalogs.png  [ALL CATALOGS]')

    for idx, (name, filename) in enumerate(catalogs, 1):
        catalog_url = f'{BASE_URL}/index.html?catalog={idx}'
        clean_name = sanitize_filename(name)
        out_file = f'qr-codes/{str(idx).zfill(2)}_{clean_name}.png'
        make_labeled_qr(catalog_url, name, out_file)
        print(f'Generated: {out_file}  [{name}]')

    print('\nAll QR codes generated with labels underneath!')
    print('Location: qr-codes/ folder')
    print('\nIMPORTANT: Update BASE_URL at the top of this script')
    print(f'Current BASE_URL: {BASE_URL}')


if __name__ == '__main__':
    generate_all()
