import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import os
from io import BytesIO

# ==========================================
# FUNGSI UTAMA (BERSIH TANPA DIAGNOSA)
# ==========================================
def add_stamp_to_image(image, text_content):
    # --- 1. RESIZE FOTO (Agar Ukuran Konsisten) ---
    target_width = 1280
    w_percent = (target_width / float(image.size[0]))
    h_size = int((float(image.size[1]) * float(w_percent)))
    image = image.resize((target_width, h_size), Image.Resampling.LANCZOS)
    img = image.convert("RGBA")
    width, height = img.size
    
    # --- 2. LOGIKA UKURAN ---
    # Menggunakan 3% dari lebar (Sesuai kode terakhir Anda)
    font_size = int(width * 0.03) 
    
    # --- 3. LOAD FONT ---
    font = None
    try:
        # Coba load file arialbd.ttf
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except Exception as e:
        # Jika gagal, load font default
        font = ImageFont.load_default()

    # --- 4. PENEMPELAN TEXT ---
    # Hitung Posisi
    temp_draw = ImageDraw.Draw(img)
    bbox = temp_draw.multiline_textbbox((0, 0), text_content, font=font, align="right")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Margin 4% 
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

# ==========================================
# TAMPILAN APLIKASI
# ==========================================
st.set_page_config(page_title="Stamp Foto App", layout="wide")
st.title("📸 Stamp Foto Massal")

# --- TOMBOL RESET / CLEAR ---
# Tombol ini ditaruh di Sidebar agar rapi
if st.sidebar.button("🔄 Hapus & Mulai Baru", type="primary"):
    # Hapus semua session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Rerun aplikasi agar kembali kosong
    st.rerun()

if 'processed_images' not in st.session_state:
    st.session_state.processed_images = {}

# --- UPLOAD ---
uploaded_files = st.file_uploader("📂 Pilih Foto", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    with st.form("form_proses_utama"):
        files_to_process = uploaded_files[:5]
        
        input_data = [] 
        for i, uploaded_file in enumerate(files_to_process):
            st.markdown(f"---")
            st.subheader(f"Foto #{i+1}")
            col_img, col_text = st.columns([1, 2])
            with col_img:
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)
            with col_text:
                waktu_default = datetime.now().strftime("%d %b %Y %H.%M.%S")
                coord_default = "5,0382S 105,2763E ±18,00m"
                lokasi_default = "Tanggul Angin\nKecamatan Punggur\nKabupaten Lampung Tengah\nLampung"
                
                in_waktu = st.text_input(f"Waktu", value=waktu_default, key=f"waktu_{i}")
                in_coord = st.text_input(f"Koordinat", value=coord_default, key=f"coord_{i}")
                in_lokasi = st.text_area(f"Lokasi", value=lokasi_default, height=120, key=f"lokasi_{i}")
                teks_full = f"{in_waktu}\n{in_coord}\n{in_lokasi}"
                input_data.append({"file": uploaded_file, "teks": teks_full, "index": i, "waktu_nama_file": in_waktu})

        submitted = st.form_submit_button("🚀 PROSES STAMP")

    # --- PROSES ---
    if submitted:
        st.session_state.processed_images = {} 
        
        # Baris progress
        progress_bar = st.progress(0)
        
        for idx, item in enumerate(input_data):
            img_asli = Image.open(item["file"])
            
            # Panggil fungsi (Tanpa diagnosa)
            hasil_rgba = add_stamp_to_image(img_asli, item["teks"])
            hasil_rgb = hasil_rgba.convert("RGB")
            
            st.session_state.processed_images[item["index"]] = {
                "image": hasil_rgb,
                "waktu_untuk_nama": item["waktu_nama_file"]
            }
            # Update progress
            progress_bar.progress((idx + 1) / len(input_data))
        
        st.success("✅ Proses Selesai!")
        
# --- DOWNLOAD ---
if st.session_state.processed_images:
    st.markdown("### 📥 Download Hasil")
    cols = st.columns(len(st.session_state.processed_images))
    for i, (idx, data) in enumerate(st.session_state.processed_images.items()):
        col_idx = i if i < len(cols) else 0 
        with cols[col_idx]:
            st.image(data["image"], caption=f"Hasil #{idx+1}", use_container_width=True)
            buf = BytesIO()
            data["image"].save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            nama_file_final = f"{data['waktu_untuk_nama'].replace(':', '.').replace('/', '-').strip()}.jpg"
            st.download_button(label=f"📥 Download", data=byte_im, file_name=nama_file_final, mime="image/jpeg", key=f"btn_dl_{idx}")
