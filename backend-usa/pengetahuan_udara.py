"""Basis pengetahuan kualitas udara terverifikasi — sumber untuk RAG Oxyra.
Tiap entri = satu topik utuh (akan jadi satu chunk untuk di-embed).
Berbasis standar US EPA (standar utama sistem). Disusun manual agar akurat."""

PENGETAHUAN = [
    {
        "topik": "Definisi AQI",
        "isi": "AQI (Air Quality Index) atau Indeks Kualitas Udara adalah indeks untuk "
                "melaporkan kualitas udara harian. AQI menyatakan seberapa bersih atau "
                "tercemarnya udara, dan dampak kesehatan yang mungkin timbul. Semakin tinggi "
                "nilai AQI, semakin tinggi tingkat pencemaran dan risiko kesehatannya. Sistem "
                "ini menggunakan standar AQI Amerika Serikat (US EPA) sebagai acuan utama."
    },
    {
        "topik": "Kategori AQI US EPA",
        "isi": "Standar AQI US EPA membagi kualitas udara menjadi enam kategori: "
                "0–50 Baik (Good) — kualitas udara memuaskan, risiko kecil; "
                "51–100 Sedang (Moderate) — dapat diterima, sebagian kecil orang sensitif perlu waspada; "
                "101–150 Tidak Sehat bagi Kelompok Sensitif — kelompok sensitif (anak, lansia, penderita "
                "gangguan pernapasan/jantung) dapat terdampak, masyarakat umum biasanya belum; "
                "151–200 Tidak Sehat — sebagian masyarakat umum mulai merasakan dampak, kelompok sensitif lebih serius; "
                "201–300 Sangat Tidak Sehat — peringatan kesehatan, semua orang berisiko; "
                "301–500 Berbahaya (Hazardous) — kondisi darurat, seluruh populasi terdampak."
    },
    {
        "topik": "Ozon permukaan vs stratosfer",
        "isi": "Penting membedakan dua jenis ozon. Ozon stratosfer berada jauh di atas permukaan "
                "(lapisan ozon) dan BERMANFAAT karena melindungi Bumi dari radiasi ultraviolet matahari. "
                "Namun, ozon PERMUKAAN (ground-level ozone) adalah POLUTAN berbahaya yang terbentuk di "
                "dekat tanah dari reaksi sinar matahari dengan polutan seperti NOx dan senyawa organik "
                "volatil (VOC) dari kendaraan dan industri. Sistem ini mengukur ozon permukaan, yaitu "
                "ozon sebagai polutan, bukan ozon pelindung di stratosfer. Ozon permukaan tertinggi "
                "biasanya pada siang hari saat sinar matahari kuat."
    },
    {
        "topik": "Karbon monoksida (CO)",
        "isi": "CO adalah karbon monoksida, gas tidak berwarna dan tidak berbau yang berasal dari "
                "pembakaran tidak sempurna bahan bakar, terutama dari kendaraan bermotor. CO berbahaya "
                "karena mengikat hemoglobin dalam darah lebih kuat daripada oksigen, sehingga mengurangi "
                "pasokan oksigen ke organ tubuh. Paparan tinggi dapat menyebabkan pusing, mual, hingga "
                "keracunan CO yang fatal. CO BUKAN karbon dioksida (CO2); keduanya gas berbeda."
    },
    {
        "topik": "Nitrogen dioksida (NO2)",
        "isi": "NO2 adalah nitrogen dioksida, gas berwarna kecokelatan dari pembakaran bahan bakar, "
                "terutama kendaraan bermotor dan pembangkit listrik. NO2 mengiritasi saluran pernapasan, "
                "memperburuk asma, dan menurunkan fungsi paru. NO2 juga berperan membentuk ozon permukaan "
                "dan hujan asam. NO2 TIDAK menyebabkan perubahan cuaca; dampaknya pada kesehatan pernapasan "
                "dan pembentukan polutan sekunder."
    },
    {
        "topik": "Sulfur dioksida (SO2)",
        "isi": "SO2 adalah sulfur dioksida, gas tajam dari pembakaran bahan bakar yang mengandung sulfur, "
                "terutama batu bara dan minyak, serta proses industri. SO2 mengiritasi saluran pernapasan "
                "dan mata, memperburuk asma, dan merupakan penyebab utama hujan asam yang merusak lingkungan."
    },
    {
        "topik": "Partikulat PM2.5 dan PM10",
        "isi": "PM2.5 adalah partikel halus berukuran 2,5 mikrometer atau lebih kecil; PM10 berukuran "
                "10 mikrometer atau lebih kecil. PM2.5 sangat berbahaya karena cukup kecil untuk masuk "
                "jauh ke paru-paru bahkan aliran darah, meningkatkan risiko penyakit pernapasan dan jantung. "
                "Sumbernya antara lain asap kendaraan, pembakaran, debu, dan industri."
    },
    {
        "topik": "Kelompok rentan polusi udara",
        "isi": "Kelompok yang lebih rentan terhadap polusi udara: anak-anak (paru-paru masih berkembang, "
                "menghirup lebih banyak udara per berat badan), lansia, ibu hamil, serta penderita gangguan "
                "pernapasan (asma, PPOK) dan penyakit jantung. Mereka perlu lebih waspada saat AQI meningkat."
    },
    {
        "topik": "Tindakan saat udara tidak sehat",
        "isi": "Saat AQI memasuki kategori tidak sehat (di atas 100, terutama untuk kelompok sensitif), "
                "tindakan yang dianjurkan: kurangi aktivitas fisik berat di luar ruangan, terutama bagi "
                "kelompok rentan; tutup jendela untuk mengurangi udara luar yang masuk; gunakan masker yang "
                "sesuai (mis. N95) jika harus keluar; dan pantau perkembangan kualitas udara. Pada kategori "
                "lebih tinggi, hindari aktivitas luar ruangan."
    },
]