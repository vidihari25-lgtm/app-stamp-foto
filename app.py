def add_stamp_to_image(image, text_content):
    # --- 1. RESIZE FOTO ---
    target_width = 1280
    w_percent = (target_width / float(image.size[0]))
    h_size = int((float(image.size[1]) * float(w_percent)))
    image = image.resize((target_width, h_size), Image.Resampling.LANCZOS)
    img = image.convert("RGBA")
    width, height = img.size
    
    # --- 2. LOGIKA UKURAN ---
    font_size = int(width * 0.03) 
    
    # --- 3. LOAD FONT (ARIAL NARROW) ---
    font = None
    # Daftar file yang mungkin ada di folder Anda
    possible_fonts = ["arialn.ttf", "ARIALN.TTF", "arialnb.ttf", "ARIALNB.TTF"]
    
    for f_name in possible_fonts:
        try:
            # Mencari file di folder yang sama dengan skrip .py
            font = ImageFont.truetype(f_name, font_size)
            if font: break
        except:
            continue

    if font is None:
        try:
            # Mencari di folder Windows jika dijalankan lokal
            font = ImageFont.truetype("C:/Windows/Fonts/arialn.ttf", font_size)
        except:
            # Langkah terakhir agar aplikasi TIDAK MATI
            font = ImageFont.load_default()

    # --- 4. PENEMPELAN TEXT ---
    temp_draw = ImageDraw.Draw(img)
    bbox = temp_draw.multiline_textbbox((0, 0), text_content, font=font, align="right")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    margin_x = int(width * 0.04)
    margin_y = int(height * 0.04)
    x, y = width - text_width - margin_x, height - text_height - margin_y

    # Layer Bayangan
    shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    offset = max(2, int(font_size / 15))
    shadow_draw.multiline_text((x + offset, y + offset), text_content, font=font, fill=(0, 0, 0, 180), align="right")
    
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=max(1, int(font_size / 25))))
    final_img = Image.alpha_composite(img, shadow_layer)
    
    # Teks Utama
    final_draw = ImageDraw.Draw(final_img)
    final_draw.multiline_text((x, y), text_content, font=font, fill="white", align="right")

    return final_img
