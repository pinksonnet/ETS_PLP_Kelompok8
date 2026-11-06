# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text

Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')

```

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. **Komentar dan string (lexing).** 
    `laporan_penjualan.sql` baris 2 berisi `DELETE` di komentar, dan string `'FROM rahasia'`. Regex memotong teks per `;` lalu mencari kata kunci tanpa tahu mana komentar atau string. Akibatnya: `pelanggan D` dan `rahasia R` salah ditemukan, dan baris statement bergeser ke baris komentar (FP di baris 2, FN di baris 3). Hal yang sama terjadi di `pemeliharaan.sql` (`pelanggan_lama U`, `crm.alamat` dan `crm.pelanggan` di baris 2). Parser benar karena lexer membuang komentar dan menjadikan string satu token `STRING`, sehingga isinya tidak pernah dibaca sebagai SQL (Bab 4).

2. **`DELETE FROM` terbaca ganda.**
    `DELETE FROM sesi` cocok dengan pola `DELETE FROM` (D) dan pola `FROM` (R). Hasilnya FP (`'audit.sql', 16, 'sesi', 'R'`), juga `keranjang` (campuran_error baris 8) dan `pesanan` (laporan_penjualan baris 15). Parser benar karena grammar `delete_stmt` memasukkan `FROM` sebagai bagian dari `DELETE`, bukan sumber `SELECT`, dan analyzer bekerja dari node AST (Bab 5 dan 6).

3. **Tabel kedua setelah koma terlewat, dan statement rusak tetap dihitung.**
    Di `audit.sql` baris 2 `FROM pelanggan p, pesanan o`, regex hanya menangkap nama setelah `FROM`, jadi `pesanan R` terlewat (FN). Sebaliknya `campuran_error.sql` baris 4 berisi statement rusak, tapi regex tetap melaporkan `pesanan R` (FP), padahal spec 5 bilang statement gagal parse tidak dihitung. Parser benar karena grammar `table_ref { "," table_ref }` dan karena panic mode membuang statement rusak (Bab 6).

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. **Tanpa skema database.**
    `SELECT nama FROM pelanggan p, pesanan o` menghasilkan warning “ambigu tanpa skema”, `resolved` tetap `None`, dan `column_usage` tidak bisa memetakan kolom. Yang dibutuhkan: skema (tabel dan kolomnya).

2. **`COUNT(DISTINCT x)` kehilangan flag DISTINCT.**
    `FunctionCall` tidak punya field itu dan API tidak boleh diubah. Matriks CRUD tidak terpengaruh, tapi informasi DISTINCT hilang dari AST. Yang dibutuhkan: field baru di node (perubahan API).

3. **Di luar lingkup: CTE (`WITH`), `UNION`, quoted identifier.**
    Statement yang memakainya jadi parse error atau tabelnya tidak tercatat. Yang dibutuhkan: perluasan grammar dan resolver.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.
