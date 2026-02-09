import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import os
from io import BytesIO

# ==========================================
# FUNGSI UTAMA (TIDAK DIUBAH SAMA SEKALI)
# ==========================================
def add_stamp_to_image(image, text_content):
    # 1. Siapkan Gambar Dasar (RGBA)
    img = image.convert("RGBA")
    width, height = img.size
    
    # 2. Ukuran Font (proporsional)
    font_size = int(height * 0.035)
    
    # 3. Load Font
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # 4. Hitung Posisi Teks
    temp_draw = ImageDraw.Draw(img)
    bbox = temp_draw.multiline_textbbox((0, 0), text_content, font=font, align="right")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    margin_x = int(width * 0.05)
    margin_y = int(height * 0.05)
    x = width - text_width - margin_x
    y = height - text_height - margin_y

    # --- MEMBUAT EFEK BAYANGAN LEMBUT ---
    shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_color = (0, 0, 0, 180) 
    
    # Offset (Jarak bayangan)
    offset_x = max(1, int(font_size / 25))
    offset_y = max(1, int(font_size / 25))
    
    # Gambar bayangan
    shadow_draw.multiline_text(
        (x + offset_x, y + offset_y), 
        text_content, 
        font=font, 
        fill=shadow_color, 
        align="right"
    )
    
    # Blur bayangan
    blur_radius = max(1, int(font_size / 30))
    shadow_layer_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # Gabungkan layer
    final_img = Image.alpha_composite(img, shadow_layer_blurred)
    
    # --- MENGGAMBAR TEKS UTAMA ---
    final_draw = ImageDraw.Draw(final_img)
    final_draw.multiline_text(
        (x, y), 
        text_content, 
        font=font, 
        fill="white", 
        align="right"
    )

    return final_img

# ==========================================
# TAMPILAN APLIKASI
# ==========================================
st.set_page_config(page_title="Stamp Multi Foto", layout="wide")
st.title("📸 Stamp Foto Massal (Rename Sesuai Tanggal)")
st.write("Upload hingga 5 foto. Nama file hasil download akan otomatis mengikuti Tanggal yang Anda input.")

# Inisialisasi Session State untuk menyimpan hasil
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = {}

# --- UPLOAD FOTO (MULTIPLE) ---
uploaded_files = st.file_uploader("📂 Pilih Foto (Bisa pilih banyak sekaligus)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    # Form Pembungkus
    with st.form("form_proses_utama"):
        # Batasi maksimal 5 foto
        files_to_process = uploaded_files[:5]
        if len(uploaded_files) > 5:
            st.warning("⚠️ Maksimal 5 foto! Hanya 5 foto pertama yang akan diproses.")

        input_data = [] 
        
        # Loop Input Data
        for i, uploaded_file in enumerate(files_to_process):
            st.markdown(f"---")
            st.subheader(f"Foto #{i+1}")
            
            col_img, col_text = st.columns([1, 2])
            
            with col_img:
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)
            
            with col_text:
                # Default value
                waktu_default = datetime.now().strftime("%d %b %Y %H.%M.%S")
                coord_default = "5,0382S 105,2763E ±18,00m"
                lokasi_default = "Tanggul Angin\nKecamatan Punggur\nKabupaten Lampung Tengah\nLampung"
                
                # Input Text
                in_waktu = st.text_input(f"Waktu (Akan jadi nama file)", value=waktu_default, key=f"waktu_{i}")
                in_coord = st.text_input(f"Koordinat", value=coord_default, key=f"coord_{i}")
                in_lokasi = st.text_area(f"Lokasi", value=lokasi_default, height=120, key=f"lokasi_{i}")
                
                # Simpan data inputan
                teks_full = f"{in_waktu}\n{in_coord}\n{in_lokasi}"
                
                input_data.append({
                    "file": uploaded_file, 
                    "teks": teks_full,
                    "index": i,
                    "waktu_nama_file": in_waktu # <--- Kita simpan ini untuk nama file nanti
                })

        st.markdown("---")
        submitted = st.form_submit_button("🚀 PROSES SEMUA FOTO")

    # --- LOGIKA PROSES ---
    if submitted:
        st.session_state.processed_images = {} # Reset hasil lama
        
        progress_bar = st.progress(0)
        
        for idx, item in enumerate(input_data):
            # Buka foto
            img_asli = Image.open(item["file"])
            
            # Panggil Fungsi Stamp
            hasil_rgba = add_stamp_to_image(img_asli, item["teks"])
            
            # Konversi ke RGB (JPEG)
            hasil_rgb = hasil_rgba.convert("RGB")
            
            # Simpan ke memory state beserta nama waktu yang diinginkan
            st.session_state.processed_images[item["index"]] = {
                "image": hasil_rgb,
                "waktu_untuk_nama": item["waktu_nama_file"]
            }
            
            progress_bar.progress((idx + 1) / len(input_data))
        
        st.success("✅ Selesai! Nama file sudah disesuaikan dengan tanggal.")

# --- TAMPILAN HASIL & DOWNLOAD ---
if st.session_state.processed_images:
    st.markdown("### 📥 Download Hasil")
    
    cols = st.columns(len(st.session_state.processed_images))
    
    for i, (idx, data) in enumerate(st.session_state.processed_images.items()):
        with cols[i] if i < len(cols) else st.container():
            st.image(data["image"], caption=f"Hasil #{idx+1}", use_container_width=True)
            
            # Siapkan buffer gambar
            buf = BytesIO()
            data["image"].save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            # --- LOGIKA NAMA FILE BARU ---
            # Ambil teks waktu dari input user
            nama_mentah = data["waktu_untuk_nama"]
            
            # Bersihkan karakter yang dilarang di Windows/Android (titik dua, garis miring, dll)
            # Ganti spasi dengan underscore, ganti titik dua dengan titik/dash
            nama_bersih = nama_mentah.replace(":", ".").replace("/", "-").replace("\\", "-")
            
            # Tambahkan ekstensi .jpg
            nama_file_final = f"{nama_bersih}.jpg"
            
            st.download_button(
                label=f"📥 Download {nama_file_final}",
                data=byte_im,
                file_name=nama_file_final,
                mime="image/jpeg",
                key=f"btn_dl_{idx}"
            )
