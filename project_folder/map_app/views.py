# Mengimpor fungsi render dan redirect dari modul django.shortcuts untuk menampilkan template dan melakukan redirect
from django.shortcuts import render, redirect
# Mengimpor modul csv untuk membaca dan menulis file CSV
import csv
# Mengimpor pustaka pandas untuk memudahkan manipulasi data, terutama file CSV
import pandas as pd
# Mengimpor pustaka folium untuk membuat peta interaktif
import folium
# Mengimpor kelas Icon dari folium untuk mengustomisasi ikon marker pada peta
from folium import Icon
# Mengimpor groupby dari itertools untuk mengelompokkan data berdasarkan kriteria tertentu
from itertools import groupby
# Mengimpor itemgetter dari operator untuk mengambil nilai item pada dictionary, berguna saat pengelompokan
from operator import itemgetter
# Mengimpor settings dari Django untuk mengakses konfigurasi proyek (misalnya MEDIA_ROOT)
from django.conf import settings
# Mengimpor modul os untuk operasi yang bergantung pada sistem operasi (misalnya manajemen file dan folder)
import os
# Mengimpor decorator login_required untuk membatasi akses view hanya untuk pengguna yang sudah login
from django.contrib.auth.decorators import login_required
# Mengimpor fungsi authenticate, login, dan logout untuk proses otentikasi pengguna
from django.contrib.auth import authenticate, login, logout
# Mengimpor model User untuk mengelola data pengguna di basis data
from django.contrib.auth.models import User
# Mengimpor modul messages untuk mengirim pesan umpan balik ke pengguna (misalnya error atau sukses)
from django.contrib import messages

# ==============================
# PENDEFINISIAN PATH FILE
# ==============================

# Mendefinisikan path file CSV yang menyimpan data titik (koordinat) di Pekanbaru
CSV_FILE_PATH = 'data/data_titik_pekanbaru.csv'
# Mendefinisikan path file GeoJSON untuk wilayah. Perhatikan bahwa variabel GEOJSON_FILE_PATH di-assign ulang berkali-kali,
# sehingga hanya nilai terakhir ('data/Tenayan Raya.json') yang tersimpan. Namun, file-file GeoJSON yang berbeda akan digunakan di daftar geojson_files.
GEOJSON_FILE_PATH = 'data/Tampan.json'
GEOJSON_FILE_PATH = 'data/Payung Sekaki.json'
GEOJSON_FILE_PATH = 'data/Lima Puluh.json'
GEOJSON_FILE_PATH = 'data/Marpoyan Damai.json'
GEOJSON_FILE_PATH = 'data/Pekanbaru Kota.json'
GEOJSON_FILE_PATH = 'data/Rumbai Pesisir.json'
GEOJSON_FILE_PATH = 'data/Rumbai.json'
GEOJSON_FILE_PATH = 'data/Sail.json'
GEOJSON_FILE_PATH = 'data/Senapelan.json'
GEOJSON_FILE_PATH = 'data/Sukajadi.json'
GEOJSON_FILE_PATH = 'data/Bukit Raya.json'
GEOJSON_FILE_PATH = 'data/Tenayan Raya.json'


# ==============================
# VIEW UNTUK MENAMPILKAN PETA
# ==============================

def map_view(request):
    # Membuat peta dasar menggunakan folium dengan lokasi awal dan tingkat zoom yang telah ditentukan
    map_pku = folium.Map(location=[0.5041780110643108, 101.44494778741002], zoom_start=12)

    # Mencoba membaca data titik dari file CSV menggunakan pandas
    try:
        data = pd.read_csv(CSV_FILE_PATH)
        data.reset_index(drop=True, inplace=True)  # Mengatur ulang index agar berurutan dari 0
    except FileNotFoundError:
        # Jika file CSV tidak ditemukan, buat DataFrame kosong dengan kolom-kolom yang diperlukan
        data = pd.DataFrame(columns=['ID', 'Nama', 'Kategori', 'Latitude', 'Longitude', 'Sumber', 'Deskripsi', 'Nama File Gambar'])

    # Jika kolom 'ID' tidak ada atau terdapat nilai NaN, tambahkan/isi kolom 'ID' secara berurutan
    if 'ID' not in data.columns or data['ID'].isna().any():
        data['ID'] = range(1, len(data) + 1)

    # Mengambil query pencarian dari parameter GET pada URL, lalu menghapus spasi ekstra
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Menyaring data berdasarkan apakah kolom 'Nama' atau 'Kategori' mengandung kata kunci pencarian (tidak case sensitive)
        data = data[
            (data['Nama'].str.contains(search_query, case=False, na=False)) |
            (data['Kategori'].str.contains(search_query, case=False, na=False))
        ]

    # Mengonversi data DataFrame ke dalam format list of dictionaries (setiap baris menjadi dictionary)
    data_dict = data.to_dict('records')

    # Fungsi untuk menentukan ikon yang akan digunakan pada marker berdasarkan kategori dan nama
    def get_icon_for_category(category, name=None):
        if category == "Halte":
            if "Utama" in name:
                # Jika nama mengandung kata "Utama", gunakan ikon bus dengan warna biru
                return Icon(color="blue", icon="bus-alt", prefix="fa")
            else:
                # Jika bukan "Utama", gunakan ikon bus dengan warna lightblue
                return Icon(color="lightblue", icon="bus", prefix="fa")
        elif category == "Bandara":
            if "Internasional" in name:
                # Untuk bandara internasional, gunakan ikon pesawat dengan warna darkgreen
                return Icon(color="darkgreen", icon="plane-departure", prefix="fa")
            else:
                # Untuk bandara non-internasional, gunakan ikon pesawat dengan warna green
                return Icon(color="green", icon="plane", prefix="fa")
        elif category == "Sekolah":
            if "SDN" in name:
                return Icon(color="orange", icon="school", prefix="fa")
            elif "SMPN" in name:
                return Icon(color="purple", icon="chalkboard", prefix="fa")
            elif "SMKN" in name or "SMAN" in name:
                return Icon(color="blue", icon="graduation-cap", prefix="fa")
            else:
                return Icon(color="gray", icon="book", prefix="fa")
        elif category == "Taman":
            return Icon(color="green", icon="tree", prefix="fa")
        elif category == "Rumah Sakit":
            return Icon(color="red", icon="hospital", prefix="fa")
        elif category == "Pasar":
            return Icon(color="orange", icon="shopping-cart", prefix="fa")
        elif category == "Tempat Ibadah":
            if "Masjid" in name:
                return Icon(color="green", icon="mosque", prefix="fa")
            elif "Gereja" in name:
                return Icon(color="brown", icon="church", prefix="fa")
            else:
                return Icon(color="gray", icon="place-of-worship", prefix="fa")
        elif category == "Universitas":
            return Icon(color="darkblue", icon="university", prefix="fa")
        elif category == "Pusat Perbelanjaan":
            return Icon(color="pink", icon="shopping-bag", prefix="fa")
        elif category == "GOR Olahraga":
            return Icon(color="darkred", icon="futbol", prefix="fa")
        else:
            # Jika kategori tidak dikenali, gunakan ikon info-sign berwarna gray
            return Icon(color="gray", icon="info-sign")

    # Mengelompokkan data yang telah dikonversi ke dictionary berdasarkan kategori menggunakan groupby
    data_grouped = {}
    if data_dict:
        # Mengurutkan data berdasarkan 'Kategori' kemudian mengelompokkannya
        for key, group in groupby(sorted(data_dict, key=itemgetter('Kategori')), key=itemgetter('Kategori')):
            data_grouped[key] = list(group)

    # Menambahkan marker ke peta berdasarkan masing-masing kategori
    for category, category_data in data_grouped.items():
        # Membuat layer fitur (feature group) untuk setiap kategori agar bisa diatur tampilannya secara terpisah di peta
        group = folium.FeatureGroup(name=category)
        for row in category_data:
            try:
                # Validasi dan konversi nilai latitude dan longitude menjadi float
                latitude = float(row['Latitude'])
                longitude = float(row['Longitude'])

                # Membuat konten popup dalam format HTML yang akan muncul saat marker diklik
                popup_html = f"""
                    <b>{row['Nama']}</b><br>
                    Kategori: {row['Kategori']}<br>
                    Latitude: {latitude}<br>
                    Longitude: {longitude}<br>
                    <p>{row.get('Deskripsi', 'Deskripsi tidak tersedia.')}</p>
                """
                # Jika ada nama file gambar, tambahkan tag <img> untuk menampilkan gambarnya
                if row.get('Nama File Gambar'):
                    popup_html += f"""
                    <img src="/media/{row['Nama File Gambar']}" alt="{row['Nama']}" style="width:200px; height:auto;" />
                    """

                # Menentukan ikon marker berdasarkan kategori dan nama
                icon = get_icon_for_category(row['Kategori'], name=row['Nama'])

                # Menambahkan marker ke dalam group layer dengan lokasi, popup, tooltip, dan ikon yang telah ditentukan
                folium.Marker(
                    location=[latitude, longitude],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=row['Nama'],
                    icon=icon
                ).add_to(group)

            except ValueError:
                # Jika terjadi error konversi (misalnya latitude atau longitude tidak valid), lewati baris tersebut
                continue

        # Menambahkan group layer kategori ke peta utama
        group.add_to(map_pku)

    # Fungsi untuk menentukan warna isian wilayah berdasarkan distrik
    def get_color(district):
        # Mendefinisikan mapping distrik dengan warna tertentu
        colors = {
            "Tampan": "#FF5733",  # Merah-oranye
            "Payung Sekaki": "#33FF57",  # Hijau
            "Bukit Raya": "#FFC300",  # Kuning
            "Lima Puluh": "#DAF7A6",  # Hijau pucat
            "Marpoyan Damai": "#C70039",  # Merah gelap
            "Pekanbaru Kota": "#900C3F",  # Merah marun
            "Rumbai Pesisir": "#581845",  # Ungu tua
            "Rumbai": "#8E44AD",  # Ungu cerah
            "Sail": "#2980B9",  # Biru cerah
            "Senapelan": "#1ABC9C",  # Toska
            "Sukajadi": "#E67E22",  # Oranye terang
            "Tenayan Raya": "#34495E",  # Abu-abu gelap
        }
        # Mengembalikan warna yang sesuai, atau warna default jika distrik tidak ditemukan
        return colors.get(district, "#3388FF")  # Default biru jika distrik tidak ditemukan

    # Membuat daftar file GeoJSON beserta nama layer untuk masing-masing wilayah
    geojson_files = [
        ('data/Tampan.json', "Wilayah Tampan"),
        ('data/Payung Sekaki.json', "Wilayah Payung Sekaki"),
        ('data/Bukit Raya.json', "Wilayah Bukit Raya"),
        ('data/Lima Puluh.json', "Wilayah Lima Puluh"),
        ('data/Marpoyan Damai.json', "Wilayah Marpoyan Damai"),
        ('data/Pekanbaru Kota.json', "Wilayah Pekanbaru Kota"),
        ('data/Rumbai Pesisir.json', "Wilayah Rumbai Pesisir"),
        ('data/Rumbai.json', "Wilayah Rumbai"),
        ('data/Sail.json', "Wilayah Sail"),
        ('data/Senapelan.json', "Wilayah Senapelan"),
        ('data/Sukajadi.json', "Wilayah Sukajadi"),
        ('data/Tenayan Raya.json', "Wilayah Tenayan Raya"),
    ]

    # Menambahkan setiap file GeoJSON ke dalam peta sebagai layer terpisah
    for file_path, layer_name in geojson_files:
        try:
            # Membuka file GeoJSON dan membaca isinya
            with open(file_path, 'r', encoding='utf-8') as f:
                geojson_data = f.read()
            # Membuat feature group untuk layer GeoJSON
            geojson_layer = folium.FeatureGroup(name=layer_name)
            # Menambahkan GeoJSON ke layer dengan style dan tooltip
            folium.GeoJson(
                geojson_data,
                name=f"{layer_name} Layer",
                style_function=lambda feature: {
                    'fillColor': get_color(feature['properties'].get('district', 'Unknown')),
                    'color': 'black',  # Warna border hitam
                    'weight': 0.2,  # Ketebalan border
                    'fillOpacity': 0.2,  # Tingkat transparansi isian
                },
                tooltip=folium.GeoJsonTooltip(fields=["province", "district"], aliases=["Province:", "District:"]),
            ).add_to(geojson_layer)
            # Menambahkan layer GeoJSON ke peta utama
            geojson_layer.add_to(map_pku)
        except FileNotFoundError:
            # Jika file GeoJSON tidak ditemukan, cetak pesan error ke console
            print(f"File not found: {file_path}")

    # Menambahkan kontrol layer ke peta sehingga pengguna bisa memilih layer yang ingin ditampilkan
    folium.LayerControl().add_to(map_pku)

    # Mengonversi peta yang telah dibuat ke dalam representasi HTML
    map_html = map_pku._repr_html_()
    # Merender template 'map_app/map.html' dan mengirimkan variabel-variabel yang diperlukan ke template
    return render(request, 'map_app/map.html', {
        'map': map_html,
        'data_grouped': data_grouped,
        'search_query': search_query,
        'user_authenticated': request.user.is_authenticated  # Menambahkan status autentikasi pengguna
    })


# ==============================
# VIEW UNTUK MENAMBAHKAN KOORDINAT
# ==============================

# Hanya pengguna yang sudah login yang bisa mengakses view ini
@login_required
def add_coordinate(request):
    # Jika metode request adalah POST, artinya form telah disubmit
    if request.method == 'POST':
        # Mengambil data dari form dan menghapus spasi di awal/akhir string
        nama = request.POST.get('nama', '').strip()
        kategori = request.POST.get('kategori', '').strip()
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        # Mengambil file gambar (jika ada) dari data request
        gambar = request.FILES.get('gambar')

        # Validasi input: pastikan field nama, kategori, latitude, dan longitude tidak kosong
        if not (nama and kategori and latitude and longitude):
            return render(request, 'map_app/add_coordinate.html', {'error': 'Semua field wajib diisi!'})

        # Mencoba mengonversi latitude dan longitude menjadi float
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return render(request, 'map_app/add_coordinate.html', {'error': 'Latitude dan Longitude harus berupa angka!'})

        # Menyimpan file gambar ke direktori media (jika ada gambar)
        gambar_path = ""
        if gambar:
            gambar_path = f"images/{gambar.name}"
            gambar_full_path = os.path.join(settings.MEDIA_ROOT, gambar_path)
            # Membuat direktori tujuan jika belum ada
            os.makedirs(os.path.dirname(gambar_full_path), exist_ok=True)
            # Menulis file gambar secara bertahap (chunks) ke dalam file di server
            with open(gambar_full_path, 'wb') as f:
                for chunk in gambar.chunks():
                    f.write(chunk)

        # Membaca data CSV untuk menentukan ID baru (ID terakhir + 1)
        try:
            data = pd.read_csv(CSV_FILE_PATH)
            data.reset_index(drop=True, inplace=True)
            if 'ID' not in data.columns or data['ID'].isna().any():
                data['ID'] = range(1, len(data) + 1)
            new_id = int(data['ID'].max()) + 1 if not data.empty else 1
        except (FileNotFoundError, pd.errors.EmptyDataError):
            # Jika file tidak ditemukan atau kosong, mulai dengan ID 1
            new_id = 1

        # Menulis data baru ke file CSV dengan mode append ('a')
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Jika file CSV masih kosong, tulis header terlebih dahulu
            if os.stat(CSV_FILE_PATH).st_size == 0:
                writer.writerow(['ID', 'Nama', 'Kategori', 'Latitude', 'Longitude', 'Sumber', 'Deskripsi', 'Nama File Gambar'])
            # Menulis baris data baru dengan informasi yang didapat dari form
            writer.writerow([new_id, nama, kategori, latitude, longitude, "Manual Input", deskripsi, gambar_path])

        # Setelah data berhasil ditambahkan, redirect ke view peta
        return redirect('map_view')

    # Jika metode request bukan POST, render halaman form untuk menambah koordinat
    return render(request, 'map_app/add_coordinate.html')


# ==============================
# VIEW UNTUK MENGEDIT KOORDINAT
# ==============================

# Hanya pengguna yang sudah login yang bisa mengakses view ini
@login_required
def edit_coordinate(request, id):
    # Mencoba membaca data CSV
    try:
        data = pd.read_csv(CSV_FILE_PATH)
        data.reset_index(drop=True, inplace=True)
    except FileNotFoundError:
        return redirect('map_view')

    # Jika request adalah POST, artinya form edit telah disubmit
    if request.method == 'POST':
        # Mendapatkan baris data yang akan diedit berdasarkan ID
        row_to_edit = data[data['ID'] == id]

        if not row_to_edit.empty:
            # Memperbarui nilai kolom 'Nama' dan 'Kategori' dari form input
            data.loc[data['ID'] == id, 'Nama'] = request.POST.get('nama', '').strip()
            data.loc[data['ID'] == id, 'Kategori'] = request.POST.get('kategori', '').strip()
            # Mencoba mengonversi dan memperbarui latitude dan longitude
            try:
                data.loc[data['ID'] == id, 'Latitude'] = float(request.POST.get('latitude', '').strip())
                data.loc[data['ID'] == id, 'Longitude'] = float(request.POST.get('longitude', '').strip())
            except ValueError:
                # Jika terjadi kesalahan konversi, render ulang form dengan pesan error
                return render(request, 'map_app/edit_coordinate.html', {
                    'error': 'Latitude dan Longitude harus berupa angka!',
                    'row': row_to_edit.iloc[0].to_dict(),
                    'id': id
                })

            # Memperbarui deskripsi dari input form
            data.loc[data['ID'] == id, 'Deskripsi'] = request.POST.get('deskripsi', '').strip()

            # Mengambil file gambar (jika ada) dari form
            gambar = request.FILES.get('gambar')
            if gambar:
                # Menghapus file gambar lama (jika ada) sebelum menyimpan gambar baru
                gambar_path_old = row_to_edit.iloc[0]['Nama File Gambar']
                if pd.notna(gambar_path_old) and os.path.exists(os.path.join(settings.MEDIA_ROOT, gambar_path_old)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, gambar_path_old))

                # Menyimpan gambar baru ke direktori media
                gambar_path_new = f"images/{gambar.name}"
                gambar_full_path = os.path.join(settings.MEDIA_ROOT, gambar_path_new)
                os.makedirs(os.path.dirname(gambar_full_path), exist_ok=True)
                with open(gambar_full_path, 'wb') as f:
                    for chunk in gambar.chunks():
                        f.write(chunk)
                # Memperbarui kolom 'Nama File Gambar' dengan path gambar baru
                data.loc[data['ID'] == id, 'Nama File Gambar'] = gambar_path_new

            # Menyimpan perubahan ke file CSV
            data.to_csv(CSV_FILE_PATH, index=False)

        # Setelah pengeditan selesai, redirect ke view peta
        return redirect('map_view')

    # Jika request bukan POST, tampilkan halaman form edit dengan data yang sudah ada
    row = data[data['ID'] == id]
    if not row.empty:
        return render(request, 'map_app/edit_coordinate.html', {'row': row.iloc[0].to_dict(), 'id': id})

    # Jika data tidak ditemukan, redirect ke view peta
    return redirect('map_view')


# ==============================
# VIEW UNTUK MENGHAPUS KOORDINAT
# ==============================

# Hanya pengguna yang sudah login yang bisa mengakses view ini
@login_required
def delete_coordinate(request, id):
    # Mencoba membaca data CSV
    try:
        data = pd.read_csv(CSV_FILE_PATH)
        data.reset_index(drop=True, inplace=True)
    except FileNotFoundError:
        return redirect('map_view')

    # Jika request adalah POST, artinya penghapusan telah dikonfirmasi
    if request.method == 'POST':
        # Mendapatkan baris data yang akan dihapus berdasarkan ID
        row_to_delete = data[data['ID'] == id]

        if not row_to_delete.empty:
            # Jika terdapat file gambar yang terkait, hapus file tersebut dari direktori media
            gambar_path = row_to_delete.iloc[0]['Nama File Gambar']
            if pd.notna(gambar_path) and os.path.exists(os.path.join(settings.MEDIA_ROOT, gambar_path)):
                os.remove(os.path.join(settings.MEDIA_ROOT, gambar_path))

            # Menghapus baris data dengan ID yang sesuai dari DataFrame
            data = data[data['ID'] != id]

            # Menyimpan DataFrame yang telah diperbarui ke file CSV
            data.to_csv(CSV_FILE_PATH, index=False)

        # Setelah penghapusan selesai, redirect ke view peta
        return redirect('map_view')

    # Jika request bukan POST, tampilkan halaman konfirmasi penghapusan
    row = data[data['ID'] == id]
    if not row.empty:
        return render(request, 'map_app/delete_coordinate.html', {'row': row.iloc[0].to_dict()})

    return redirect('map_view')


# ==============================
# VIEW UNTUK LOGIN PENGGUNA
# ==============================

def login_view(request):
    # Jika metode request adalah POST, artinya form login telah disubmit
    if request.method == 'POST':
        # Mengambil username dan password dari form
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Mengotentikasi pengguna dengan data yang diberikan
        user = authenticate(request, username=username, password=password)

        if user:
            # Jika autentikasi berhasil, lakukan login dan redirect ke view peta
            login(request, user)
            print(f"User {user.username} berhasil login.")  # Debug: mencetak pesan sukses ke console
            return redirect('map_view')
        else:
            # Jika autentikasi gagal, tampilkan pesan error
            messages.error(request, 'Username atau password salah!')

    # Render halaman login
    return render(request, 'map_app/login.html')


# ==============================
# VIEW UNTUK LOGOUT PENGGUNA
# ==============================

def logout_view(request):
    # Melakukan logout pengguna
    logout(request)
    # Redirect ke view peta setelah logout
    return redirect('map_view')


# ==============================
# VIEW UNTUK REGISTRASI PENGGUNA
# ==============================

def register_view(request):
    # Jika metode request adalah POST, artinya form registrasi telah disubmit
    if request.method == 'POST':
        # Mengambil data username, email, password, dan konfirmasi password dari form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Memeriksa apakah password dan konfirmasi password cocok
        if password != confirm_password:
            messages.error(request, 'Password tidak cocok!')
            return redirect('register')

        # Memeriksa apakah username sudah digunakan
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan!')
            return redirect('register')

        # Membuat user baru dengan data yang diberikan dan menyimpannya ke basis data
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Akun berhasil dibuat! Silakan login.')
        return redirect('login')

    # Jika metode request bukan POST, render halaman registrasi
    return render(request, 'map_app/register.html')


# ==============================
# VIEW UNTUK HALAMAN ABOUT (TENTANG PEKANBARU)
# ==============================

# (Baris import render di bawah ini sebenarnya sudah diimpor di awal file, jadi ini bersifat duplikat)
from django.shortcuts import render

def about_pekanbaru(request):
    # Render halaman about yang menjelaskan informasi mengenai Pekanbaru
    return render(request, 'map_app/about.html')
