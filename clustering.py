import pandas as pd

# KONFIGURASI
MAX_ITER   = 100

CENTROID_AWAL = [
    [5.00, 1.00, 1.00],  # C1 – dominan ChatGPT
    [1.00, 5.00, 1.00],  # C2 – dominan Gemini
    [1.00, 1.00, 5.00],  # C3 – dominan Claude
]

SEP  = "─" * 56
SEP2 = "=" * 56

# FUNGSI BANTU MATEMATIKA

def rata_rata(angka): #Fungsi yg mengembalikan nilai rata rata pada list
    return sum(angka) / len(angka)

def jarak_euclidean(titik, centroid): #Fungsi yg mengembalikan jarak antara titik dengan centroid 
    total = 0
    for k in range(len(titik)):
        total += (titik[k] - centroid[k]) ** 2
    return total ** 0.5

def cluster_terdekat(titik, centroids): #Mencari cluster terdekat pada titik, dan mengembalikan indeksnya
    jarak_min = jarak_euclidean(titik, centroids[0])
    index_min = 0
    for c in range(1, len(centroids)):
        j = jarak_euclidean(titik, centroids[c])
        if j < jarak_min:
            jarak_min = j
            index_min = c
    return index_min

def hitung_centroid_baru(data, labels, k):
    """Hitung posisi centroid baru dari rata-rata anggota tiap cluster."""
    centroids_baru = []
    for c in range(k):
        anggota_x = []
        anggota_y = []
        anggota_z = []
        for i in range(len(labels)):
            if labels[i] == c:
                anggota_x.append(data[i][0])
                anggota_y.append(data[i][1])
                anggota_z.append(data[i][2])
        centroids_baru.append([rata_rata(anggota_x), rata_rata(anggota_y), rata_rata(anggota_z)])
    return centroids_baru


# 1. BACA DATA DARI EXCEL → DATAFRAME
df = pd.read_excel(r'C:\Users\Lioo\Documents\Matfor\Proyek\Respons_kuesioner_Matfor.xlsx', 'Form Responses 1')

# Hitung rata-rata skor tiap AI tool (masing-masing 4 kolom)
df['ChatGPT'] = df.iloc[:, 4:8].mean(axis=1)
df['Gemini']  = df.iloc[:, 8:12].mean(axis=1)
df['Claude']  = df.iloc[:, 12:16].mean(axis=1)


data = df[['ChatGPT', 'Gemini', 'Claude']].values.tolist()
n    = len(data)


# 2. CETAK DATA VEKTOR
print(SEP2)
print("  DATA VEKTOR")
print(SEP2)
print(f"  {'ID':<6}  {'ChatGPT':>8}  {'Gemini':>8}  {'Claude':>8}")
print(SEP)

for i in range(n):
    d = data[i]
    print(f"  R{i+1:02d}     {d[0]:>8.2f}  {d[1]:>8.2f}  {d[2]:>8.2f}")

print(SEP)


# 3. Algoritma K-MEANS
centroids   = [baris[:] for baris in CENTROID_AWAL]
labels_lama = None

print("\n" + SEP2)
print("  CENTROID AWAL")
print(SEP2)
for c in range(3):
    cv = centroids[c]
    print(f"  C{c+1} = ({cv[0]:.2f}, {cv[1]:.2f}, {cv[2]:.2f})")
print(SEP)

print("\n" + SEP2)
print("  PERGERAKAN CENTROID TIAP ITERASI")
print(SEP2)

for it in range(1, MAX_ITER + 1):

    # kelompokkan tiap responden ke cluster terdekat
    labels_baru = []
    for i in range(n):
        c = cluster_terdekat(data[i], centroids)
        labels_baru.append(c)

    # Hitung centroid baru
    centroids_baru = hitung_centroid_baru(data, labels_baru, 3)

    # Cetak posisi centroid di iterasi ini
    print(f"\n  I{it}:")
    for c in range(3):
        cv = centroids_baru[c]
        print(f"  C{c+1} = ({cv[0]:.2f}, {cv[1]:.2f}, {cv[2]:.2f})")

    # Cek konvergen: tidak ada responden yang berpindah cluster
    if labels_baru == labels_lama:
        print(f"\nKONVERGEN pada iterasi ke-{it}")
        print(f"Tidak ada responden yang berpindah cluster")
        centroids = centroids_baru
        break

    centroids   = centroids_baru
    labels_lama = labels_baru

else:
    print(f"\nBelum konvergen setelah {MAX_ITER} iterasi — tambah MAX_ITER")

print(SEP)

labels = [l + 1 for l in labels_baru]


# 4. PERBANDINGAN CENTROID AWAL VS AKHIR
print("\n" + SEP2)
print("  PERBANDINGAN CENTROID AWAL VS AKHIR")
print(SEP2)
print(f"  {'Cluster':<14}  {'Awal':^26}  {'Akhir':^26}")
print(SEP)

nama_cluster = ['C1 (ChatGPT)', 'C2 (Gemini)', 'C3 (Claude)']

for i in range(3):
    ca = CENTROID_AWAL[i]
    ck = centroids[i]
    awal  = f"({ca[0]:.2f}, {ca[1]:.2f}, {ca[2]:.2f})"
    akhir = f"({ck[0]:.2f}, {ck[1]:.2f}, {ck[2]:.2f})"
    print(f"  {nama_cluster[i]:<14}  {awal:^26}  {akhir:^26}")

print(SEP)


# 5. HASIL CLUSTER TIAP RESPONDEN
print("\n" + SEP2)
print("  HASIL CLUSTER TIAP RESPONDEN")
print(SEP2)
print(f"  {'ID':<6}  {'ChatGPT':>8}  {'Gemini':>8}  {'Claude':>8}  {'Cluster':>8}")
print(SEP)

for i in range(n):
    d = data[i]
    c = labels[i]
    print(f"  R{i+1:02d}     {d[0]:>8.2f}  {d[1]:>8.2f}  {d[2]:>8.2f}  {'C'+str(c):>8}")



# 6. RINGKASAN CLUSTER
print("\n" + SEP2)
print("  RINGKASAN CLUSTER")
print(SEP2)

for c in range(1, 4):
    anggota = []
    for i in range(len(labels)):
        if labels[i] == c:
            anggota.append(f"R{i+1:02d}")
    ids = ", ".join(anggota)
    print(f"  C{c}  ({len(anggota):2d} responden) : {ids}")

print(SEP)
