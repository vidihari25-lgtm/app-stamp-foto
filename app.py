import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import os
from io import BytesIO

# ==========================================
# FUNGSI UTAMA (MENGGUNAKAN ARIAL BOLD)
# ==========================================
def add_stamp_to_image(image, text_content):
    # --- 1. RESIZE FOTO (Agar Ukuran Konsisten) ---
    target_width = 1280
    w_percent = (target_width / float(image.size[0]))
    h_size = int((float(image.size[1]) * float(w_percent)))
    image = image.resize((target_width, h_size), Image.Resampling.LANCZOS)
    img = image.convert("RGBA")
    width, height = img.size
    
    # --- 2. LOGIKA UKURAN (5% dari Lebar Gambar) ---
    font_size = int(width * 0.03) 
    
    # --- 3. LOAD FONT (ARIAL BOLD) ---
    font = None
    # Menggunakan arialbd.ttf sesuai yang ada di GitHub Anda
    font_file = "arialbd.ttf"
    
    try:
        if os.path.exists(font_file):
            font = ImageFont.truetype(font_file, font_size)
        else:
            # Fallback jika file tidak ditemukan
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # --- 4. PENEMPELAN TEXT ---
    temp_draw = ImageDraw.Draw(img)
    bbox = temp_draw.multiline_textbbox((0, 0), text_content, font=font, align="right")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Margin 3% agar seimbang dengan ukuran font yang besar
    margin_x = int(width * 0.03)
    margin_y = int(height * 0.03)
    
    x = width - text_width - margin_x
    y = height - text_height - margin_y

    # Efek Bayangan (Shadow)
    shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_color = (0, 0, 0, 200) 
    
    offset = max(3, int(font_size / 12))
    shadow_draw.multiline_text((x + offset, y + offset), text_content, font=font, fill=shadow_color, align="right")
    
    blur_radius = max(2, int(font_size / 20))
    shadow_layer_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    final_img = Image.alpha_composite(img, shadow_layer_blurred)
    
    # Teks Utama (Putih)
    final_draw = ImageDraw.Draw(final_img)
    final_draw.multiline_text((x, y), text_content, font=font, fill="white", align="right")

    return final_img

# ==========================================
# TAMPILAN APLIKASI (UI)
# ==========================================
st.set_page_config(page_title="Stamp Foto App", layout="wide")
st.title("📸 Stamp Foto Massal")

# Sidebar Reset
if st.sidebar.button("🔄 Hapus & Mulai Baru", type="primary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if 'processed_images' not in st.session_state:
    st.session_state.processed_images = {}

# Upload Section
uploaded_files = st.file_uploader("📂 Pilih Foto", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    with st.form("form_proses_utama"):
        # Limit 5 foto per proses agar stabil
        files_to_process = uploaded_files[:5]
        
        input_data = [] 
        for i, uploaded_file in enumerate(files_to_process):
            st.markdown(f"---")
            col_img, col_text = st.columns([1, 2])
            with col_img:
                st.image(Image.open(uploaded_file), use_container_width=True)
            with col_text:
                waktu_default = datetime.now().strftime("%d %b %Y %H.%M.%S")
                in_waktu = st.text_input(f"Waktu", value=waktu_default, key=f"waktu_{i}")
                in_coord = st.text_input(f"Koordinat", value="5,0382S 105,2763E ±18,00m", key=f"coord_{i}")
                in_lokasi = st.text_area(f"Lokasi", value="Tanggul Angin\nKecamatan Punggur\nKabupaten Lampung Tengah\nLampung", height=100, key=f"lokasi_{i}")
                
                teks_full = f"{in_waktu}\n{in_coord}\n{in_lokasi}"
                input_data.append({"file": uploaded_file, "teks": teks_full, "index": i, "nama": in_waktu})

        submitted = st.form_submit_button("🚀 PROSES STAMP")

    if submitted:
        st.session_state.processed_images = {} 
        progress_bar = st.progress(0)
        
        for idx, item in enumerate(input_data):
            img_asli = Image.open(item["file"])
            hasil_rgba = add_stamp_to_image(img_asli, item["teks"])
            
            st.session_state.processed_images[item["index"]] = {
                "image": hasil_rgba.convert("RGB"),
                "nama": item["nama"]
            }
            progress_bar.progress((idx + 1) / len(input_data))
        
        st.success("✅ Proses Selesai!")

# Download Section
if st.session_state.processed_images:
    st.markdown("### 📥 Download Hasil")
    cols = st.columns(len(st.session_state.processed_images))
    for i, (idx, data) in enumerate(st.session_state.processed_images.items()):
        with cols[i]:
            st.image(data["image"], caption=f"Hasil #{idx+1}", use_container_width=True)
            buf = BytesIO()
            data["image"].save(buf, format="JPEG", quality=95)
            # Membersihkan nama file dari karakter ilegal
            nama_file_final = f"{data['nama'].replace(':', '.').replace('/', '-')}.jpg"
            st.download_button(label="📥 Download", data=buf.getvalue(), file_name=nama_file_final, key=f"dl_{idx}")

