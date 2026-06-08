# ============================================================
# 1. IMPORT LIBRARY DAN PERSIAPAN DATA
# ============================================================

import pandas as pd                          # membaca file Excel
import matplotlib.pyplot as plt              # membuat grafik
from mpl_toolkits.mplot3d import Axes3D      # grafik 3D

SEP = "─" * 60
SEP2 = "=" * 60

# Membaca data dari file Excel
df = pd.read_excel(
    r"C:\\Users\\Lioo\\Documents\\Matfor\\Proyek\\Respons_kuesioner_Matfor.xlsx",
    "Form Responses 1"
)

# Menghitung rata-rata skor tiap AI dari kolom kuesioner
df["ChatGPT"] = df.iloc[:, 4:8].mean(axis=1)   # kolom 5-8
df["Gemini"]  = df.iloc[:, 8:12].mean(axis=1)   # kolom 9-12
df["Claude"]  = df.iloc[:, 12:16].mean(axis=1)  # kolom 13-16

# Menyimpan data sebagai list 2D → [[chatgpt, gemini, claude], ...]
data = df[["ChatGPT", "Gemini", "Claude"]].values.tolist()
n = len(data)  # jumlah responden


# ============================================================
# 2. PRAPROSES DATA
# ============================================================
# Praproses terdiri dari 2 langkah:
#   a) Deteksi outlier menggunakan metode IQR
#   b) Normalisasi data menggunakan Min-Max Scaling

# --- 2a. Fungsi Deteksi Outlier IQR ---

def percentile_manual(data, p):
    """Menghitung nilai persentil ke-p dari data secara manual."""
    urut = sorted(data)
    pos = (len(urut) - 1) * p
    bawah = int(pos)
    atas = min(bawah + 1, len(urut) - 1)
    frac = pos - bawah
    return urut[bawah] + frac * (urut[atas] - urut[bawah])


def deteksi_outlier_iqr(data, nama):
    """
    Mendeteksi outlier menggunakan metode IQR (Interquartile Range).

    Parameter:
    data (list) : daftar nilai numerik satu kolom (misal skor ChatGPT).
    nama (str)  : nama kolom, untuk ditampilkan di output.

    Cara kerja:
    - Hitung Q1 (persentil 25%) dan Q3 (persentil 75%)
    - IQR = Q3 - Q1
    - Batas bawah = Q1 - 1.5 * IQR
    - Batas atas  = Q3 + 1.5 * IQR
    - Nilai di luar batas → outlier
    """
    q1 = percentile_manual(data, 0.25)
    q3 = percentile_manual(data, 0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outlier = [(i + 1, v) for i, v in enumerate(data) if v < lower or v > upper]

    print("\n" + SEP2)
    print(f"OUTLIER IQR - {nama}")
    print(SEP2)
    print(f"Q1    : {q1:.2f}")
    print(f"Q3    : {q3:.2f}")
    print(f"IQR   : {iqr:.2f}")
    print(f"Lower : {lower:.2f}")
    print(f"Upper : {upper:.2f}")

    if not outlier:
        print("Tidak ada outlier")
    else:
        for idx, nilai in outlier:
            print(f"R{idx:02d} = {nilai:.2f}")


# --- 2b. Fungsi Min-Max Scaling ---

def min_max_scaling(data):
    """
    Normalisasi data ke rentang [0, 1] menggunakan rumus:
        scaled = (x - min) / (max - min)

    Parameter:
    data (list of list): dataset asli [[chatgpt, gemini, claude], ...]

    Return:
    data_scaled (list of list): dataset yang sudah dinormalisasi.
    min_val (list): nilai minimum tiap kolom (untuk scale centroid).
    max_val (list): nilai maksimum tiap kolom (untuk scale centroid).
    """
    n_kolom = len(data[0])

    # Cari min dan max tiap kolom
    min_val = [min(row[j] for row in data) for j in range(n_kolom)]
    max_val = [max(row[j] for row in data) for j in range(n_kolom)]

    # Skalakan setiap nilai
    data_scaled = []
    for row in data:
        baris = []
        for j in range(n_kolom):
            rentang = max_val[j] - min_val[j]
            baris.append((row[j] - min_val[j]) / rentang if rentang != 0 else 0.0)
        data_scaled.append(baris)

    return data_scaled, min_val, max_val


def scale_centroid(centroid, min_val, max_val):
    """
    Menyesuaikan skala centroid awal agar sama dengan data yang sudah di-scale.

    Parameter:
    centroid (list of list): daftar centroid awal [[x,y,z], ...].
    min_val (list): nilai min tiap kolom dari data asli.
    max_val (list): nilai max tiap kolom dari data asli.

    Return:
    list of list: centroid yang sudah dinormalisasi.
    """
    hasil = []
    for c in centroid:
        baris = []
        for j in range(len(c)):
            rentang = max_val[j] - min_val[j]
            baris.append((c[j] - min_val[j]) / rentang if rentang != 0 else 0.0)
        hasil.append(baris)
    return hasil


# --- Jalankan Praproses ---

# Deteksi outlier pada data asli (sebelum scaling)
deteksi_outlier_iqr(df["ChatGPT"].tolist(), "ChatGPT")
deteksi_outlier_iqr(df["Gemini"].tolist(), "Gemini")
deteksi_outlier_iqr(df["Claude"].tolist(), "Claude")

# Normalisasi data ke rentang [0, 1]
data_scaled, min_data, max_data = min_max_scaling(data)

# Tampilkan info scaling
print("\n" + SEP2)
print("MIN-MAX SCALING")
print(SEP2)
for j, nama in enumerate(["ChatGPT", "Gemini", "Claude"]):
    print(f"{nama}: min = {min_data[j]:.4f}, max = {max_data[j]:.4f}")


# ============================================================
# 3. PENENTUAN JUMLAH CLUSTER DAN CENTROID AWAL
# ============================================================
# Jumlah cluster (k) = 3 → ChatGPT, Gemini, Claude
# Centroid awal dipilih secara manual berdasarkan karakteristik responden

k = 3
MAX_ITER = 100

CENTROID_AWAL = [
    [4.25, 1.75, 1.25],  # Cluster 1: dominan ChatGPT
    [1.25, 4.5,  2.0],   # Cluster 2: dominan Gemini
    [1.75, 1.5,  4.75],  # Cluster 3: dominan Claude
]

# Sesuaikan centroid awal ke skala [0, 1] agar cocok dengan data_scaled
centroids = scale_centroid(CENTROID_AWAL, min_data, max_data)


# ============================================================
# 4. PROSES CLUSTERING (K-Means)
# ============================================================

def jarak_euclidean(a, b):
    """Menghitung jarak Euclidean antara dua titik a dan b."""
    return sum((a[i] - b[i]) ** 2 for i in range(len(a))) ** 0.5


def cluster_terdekat(titik, centroids):
    """
    Mencari cluster terdekat untuk satu titik data.

    Parameter:
    titik (list)     : koordinat satu data, misal [0.5, 0.3, 0.8].
    centroids (list) : daftar koordinat semua centroid.

    Return:
    idx (int): indeks cluster terdekat (0, 1, atau 2).
    """
    idx = 0
    minimum = jarak_euclidean(titik, centroids[0])
    for i in range(1, len(centroids)):
        d = jarak_euclidean(titik, centroids[i])
        if d < minimum:
            minimum = d
            idx = i
    return idx


def hitung_centroid_baru(data, labels, k):
    """
    Menghitung posisi centroid baru = rata-rata posisi anggota tiap cluster.

    Parameter:
    data (list of list): dataset (sudah di-scale).
    labels (list)      : label cluster tiap data (0, 1, atau 2).
    k (int)            : jumlah cluster.

    Return:
    list of list: koordinat centroid baru.
    """
    hasil = []
    for c in range(k):
        anggota = [data[i] for i in range(len(data)) if labels[i] == c]
        if len(anggota) == 0:
            hasil.append(centroids[c][:])
            continue
        centroid = []
        for d in range(len(data[0])):
            centroid.append(sum(row[d] for row in anggota) / len(anggota))
        hasil.append(centroid)
    return hasil


# --- Jalankan K-Means ---

labels_lama = None

for it in range(MAX_ITER):
    # Tentukan cluster terdekat untuk setiap data
    labels_baru = [cluster_terdekat(row, centroids) for row in data_scaled]

    # Hitung centroid baru
    centroids_baru = hitung_centroid_baru(data_scaled, labels_baru, k)

    # Jika label tidak berubah → konvergen, berhenti
    if labels_baru == labels_lama:
        centroids = centroids_baru
        break

    labels_lama = labels_baru
    centroids = centroids_baru

# Label untuk tampilan (1-based: C1, C2, C3)
labels = [x + 1 for x in labels_baru]

# Tampilkan ringkasan cluster
print("\n" + SEP2)
print("RINGKASAN CLUSTER")
print(SEP2)
for c in range(1, k + 1):
    anggota = [f"R{i+1:02d}" for i in range(n) if labels[i] == c]
    print(f"C{c} ({len(anggota)} responden): {', '.join(anggota)}")


# ============================================================
# 5. VISUALISASI HASIL CLUSTERING (3D Scatter Plot)
# ============================================================

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

warna = ["red", "blue", "green"]

# Plot setiap cluster
for c in range(k):
    x = [data_scaled[i][0] for i in range(n) if labels_baru[i] == c]
    y = [data_scaled[i][1] for i in range(n) if labels_baru[i] == c]
    z = [data_scaled[i][2] for i in range(n) if labels_baru[i] == c]
    ax.scatter(x, y, z, s=80, color=warna[c], label=f"Cluster {c+1}")

# Plot centroid (tanda X hitam)
for c in range(k):
    ax.scatter(
        centroids[c][0], centroids[c][1], centroids[c][2],
        marker="X", s=300, color="black"
    )

ax.set_xlabel("ChatGPT (Scaled)")
ax.set_ylabel("Gemini (Scaled)")
ax.set_zlabel("Claude (Scaled)")
ax.set_title("Visualisasi Clustering K-Means")
ax.legend()
plt.show()


# ============================================================
# 6. EVALUASI MODEL (Silhouette Score)
# ============================================================
# Silhouette Score mengukur kualitas clustering.
# Rentang nilai: -1 sampai 1
#   mendekati 1  → cluster bagus (data rapat di dalam, jauh dari cluster lain)
#   mendekati 0  → data berada di perbatasan antar cluster
#   mendekati -1 → data kemungkinan salah cluster

def rata_jarak(titik, anggota):
    """Menghitung rata-rata jarak dari satu titik ke semua anggota cluster."""
    return sum(jarak_euclidean(titik, x) for x in anggota) / len(anggota)


def silhouette_score_manual(data, labels):
    """
    Menghitung Silhouette Score untuk setiap data.

    Parameter:
    data (list of list): dataset (sudah di-scale).
    labels (list)      : label cluster tiap data (0, 1, atau 2).

    Rumus per data:
      a = rata-rata jarak ke anggota cluster sendiri
      b = rata-rata jarak minimum ke cluster lain
      silhouette = (b - a) / max(a, b)

    Return:
    list: nilai silhouette untuk setiap data.
    """
    hasil = []
    for i in range(len(data)):
        cluster_sendiri = labels[i]

        # Ambil anggota cluster sendiri (kecuali dirinya)
        sendiri = [data[j] for j in range(len(data))
                   if labels[j] == cluster_sendiri and j != i]

        if len(sendiri) == 0:
            hasil.append(0)
            continue

        a = rata_jarak(data[i], sendiri)

        # Cari jarak rata-rata terkecil ke cluster lain
        b = float("inf")
        for c in set(labels):
            if c == cluster_sendiri:
                continue
            lain = [data[j] for j in range(len(data)) if labels[j] == c]
            b = min(b, rata_jarak(data[i], lain))

        hasil.append((b - a) / max(a, b))
    return hasil


# --- Jalankan Evaluasi ---

silhouette = silhouette_score_manual(data_scaled, labels_baru)

print("\n" + SEP2)
print("SILHOUETTE SCORE")
print(SEP2)

# Nilai per responden
for i in range(n):
    print(f"R{i+1:02d} C{labels[i]} = {silhouette[i]:.4f}")

# Rata-rata per cluster
print("\nRata-rata Silhouette per Cluster:")
print(SEP)
for c in range(k):
    nilai_c = [silhouette[i] for i in range(n) if labels_baru[i] == c]
    rata = sum(nilai_c) / len(nilai_c) if nilai_c else 0.0
    print(f"Cluster {c+1} = {rata:.4f}")

# Rata-rata keseluruhan
print(SEP)
overall = sum(silhouette) / len(silhouette)
print(f"Silhouette Keseluruhan = {overall:.4f}")
