def add_stamp_to_image(image, text_content):
    # --- 1. RESIZE FOTO (Agar Ukuran Konsisten) ---
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
    # Daftar kemungkinan nama file font Arial Narrow
    font_names = ["ARIALN.TTF", "arialn.ttf", "Arialn.ttf"]
    
    for font_name in font_names:
        try:
            font = ImageFont.truetype(font_name, font_size)
            break # Jika berhasil, keluar dari loop
        except:
            continue

    if font is None:
        # Jika file lokal tidak ketemu, coba cari di direktori sistem (khusus Windows)
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialn.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # --- 4. PENEMPELAN TEXT ---
    temp_draw = ImageDraw.Draw(img)
    bbox = temp_draw.multiline_textbbox((0, 0), text_content, font=font, align="right")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    margin_x = int(width * 0.04)
    margin_y = int(height * 0.04)
    
    x = width - text_width - margin_x
    y = height - text_height - margin_y

    # Efek Bayangan
    shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_color = (0, 0, 0, 180) 
    
    offset_x = max(3, int(font_size / 15))
    offset_y = max(3, int(font_size / 15))
    
    shadow_draw.multiline_text((x + offset_x, y + offset_y), text_content, font=font, fill=shadow_color, align="right")
    
    blur_radius = max(2, int(font_size / 25))
    shadow_layer_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    final_img = Image.alpha_composite(img, shadow_layer_blurred)
    
    # Teks Utama
    final_draw = ImageDraw.Draw(final_img)
    final_draw.multiline_text((x, y), text_content, font=font, fill="white", align="right")

    return final_img
