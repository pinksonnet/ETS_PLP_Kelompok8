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

Walaupun semua bug sudah diperbaiki, ada hal-hal yang tidak bisa ditangani dengan benar oleh tool ini. Batas-batas ini bukan bug, melainkan konsekuensi dari aturan spesifikasi (tanpa skema database, sintaks tertentu di luar lingkup) dan keputusan desain kami.

1. Tanpa skema database: kolom tidak bisa dipetakan ke tabelnya 
	* Contoh SQL / situasi: `SELECT * FROM crm.pelanggan;` dan `SELECT nama FROM pelanggan p, pesanan o;` 
	* Akibat pada CRUD matrix: Tabel tetap tercatat benar (`crm.pelanggan` R, serta `pelanggan` R dan `pesanan` R). Tetapi laporan kolom (`--kolom`) kosong untuk statement ini. Pada `SELECT *`, tool tidak tahu kolom apa saja yang dibaca. Pada kolom `nama` yang bisa milik dua tabel, tool memberi peringatan "kolom 'nama' ambigu tanpa skema" dan `resolved` tetap `None`. 
	* Informasi yang dibutuhkan: Metadata skema database (daftar kolom tiap tabel, misalnya dari data dictionary), supaya `*` bisa diperluas menjadi daftar kolom dan kolom tanpa qualifier bisa dipastikan milik tabel mana.

2. `t.*` tidak didukung: statement dilewati seluruhnya 
	* Contoh SQL / situasi: `SELECT p.* FROM crm.pelanggan p;` 
	* Akibat pada CRUD matrix: Parser berhenti dengan error sintaks (`diharapkan nama kolom setelah '.'`, ditemukan `*`) dan mengaktifkan panic mode. Statement itu dibuang dan tabel `crm.pelanggan` tidak tercatat di matriks (False Negative). Statement setelahnya tetap diproses. 
	* Informasi yang dibutuhkan: Penambahan aturan grammar untuk `IDENT "." "*"` di parser dan penanganannya di resolver. Untuk laporan kolom, tetap butuh skema seperti pada poin 1.

3. CTE (`WITH`), `UNION`, `MERGE`, dan quoted identifier di luar lingkup
   * Contoh SQL / situasi: `WITH aktif AS (SELECT id FROM crm.pelanggan) SELECT * FROM aktif;`, `SELECT a FROM t UNION SELECT b FROM u;`, dan `SELECT "nama" FROM t;`
   * Akibat pada CRUD matrix: Pada `WITH` dan `UNION`, parser mendeteksi error sintaks, statement dilewati, dan tabel di dalamnya (`crm.pelanggan`, `t`, `u`) tidak tercatat. Pada `UNION`, kata `UNION` dibaca sebagai alias tabel `t`, lalu parser menemukan `SELECT` di tempat yang salah. Quoted identifier lebih berat dampaknya: lexer tidak mengenal tanda `"`, sehingga melempar `LexError`, dan menurut spesifikasi 2.7 pemrosesan seluruh file berhenti. Jadi satu `"nama"` di baris 1 membuat statement sesudahnya di file yang sama tidak diproses.
   * Informasi yang dibutuhkan: Perluasan grammar di `crud/parser.py` untuk `WITH`, `UNION`, dan `MERGE`. Perluasan resolver untuk tabel sementara hasil CTE, supaya `aktif` tidak dihitung sebagai tabel fisik. Perluasan lexer untuk `"..."` dan `[...]`.

4. `COUNT(DISTINCT x)` kehilangan kata DISTINCT
   * Contoh SQL / situasi: `SELECT COUNT(DISTINCT a) FROM t;`
   * Akibat pada CRUD matrix: Matriks tetap benar (`t` R), tapi node `FunctionCall` tidak punya field untuk menyimpan DISTINCT dan spesifikasi melarang perubahan API publik, sehingga informasi itu hilang dari AST. Untuk CRUD ini tidak berpengaruh, tetapi analisis yang membedakan `COUNT(a)` dan `COUNT(DISTINCT a)` tidak bisa dilakukan dari AST.
   * Informasi yang dibutuhkan: Tambahan field `distinct` pada node `FunctionCall` di `crud/ast_nodes.py`, yang berarti mengubah API.

## 4. Pembagian kerja

Proyek ini dikerjakan oleh Alfina dan Nazwa. Pada pengerjaan modul kami membagi agar tiap anggota bisa mengerjakan semua modul.

1. **Alfina:**
	* Modul: crud/lexer.py (sebagian), crud/parser.py (sebagian), dan crud/analyzer.py (sebagian).
	* Fitur (TODO): 
		* *T1: Dukungan sintaks INSERT INTO ... SELECT ... di parser.* 
		* *T3: Pemindaian komentar blok multi-baris /* ... / dan error jika tidak ditutup di lexer.
	- Perbaikan Bug:
		* *Bug 2: Operator <> terpecah menjadi dua token (maximal munch) di lexer.* 
		* *Bug 5: Panic mode error recovery berhenti di semicolon (;) bukan di akhir file.* 
		* *Bug 6: Dukungan keyword OUTER pada LEFT OUTER JOIN di parser.* 
		* *Bug 9: Subquery di UPDATE ditandai U, dikoreksi menjadi R di analyzer.*
	- Data, Test, & Dokumen:
		- *Pelabelan ground truth di data/ground_truth.csv.* 
		- *Test regresi untuk Bug 2, 5, 6, 9, T1, dan T3 di tests/test_tambahan.py.* 
		- *Tiga test kasus tepi di tests/test_tambahan.py.* 
		- *Penulisan KARTU_DESAIN.md, entri LAPORAN_BUG.md untuk bug milik Alfina, dan bagian kedua LOG_AI.md.*

2. **Nazwa**
   * Modul: crud/lexer.py (sebagian), crud/parser.py (sebagian), dan crud/resolver.py.
   * Fitur (TODO):
      * *T2: Resolusi kolom tanpa qualifier pada scope terdalam di resolver.*
   * Perbaikan Bug:
      * *Bug 1: Keyword huruf kecil (case-insensitive) dinormalisasi di lexer.*
      * *Bug 3: Dua tanda petik berturut-turut ('') di string literal menjadi satu kutip*
      * *Bug 4: AND dan OR dipecah ke tingkat presedensi terpisah di parser.*
      * *Bug 7: Arah pencarian scope terbalik pada _lookup() di resolver.*
      * *Bug 8: Scope DELETE tidak di-pop sehingga alias bocor ke statement berikutnya.*
   * Data, Test, & Dokumen:
      - *Test regresi untuk Bug 1, 3, 4, 7, 8, dan T2 di tests/test_tambahan.py.*
      - *Dua test kasus tepi di tests/test_tambahan.py.*
      - *Penulisan LAPORAN_AKHIR.md, entri LAPORAN_BUG.md untuk bug milik Nazwa, dan bagian kedua LOG_AI.md.*

**Cara memastikan keduanya memahami seluruh kode**
1. Pola kerja yang sama di tiap perbaikan: sebelum memperbaiki, kami menulis test regresi dan memastikan gagal karena assertion, lalu memperbaiki kode, menjalankan seluruh test, baru commit. Dengan pola yang sama, tiap perbaikan mudah dibaca dan dicek oleh partner.

2. Komentar kode dan pull sebelum push: kode yang kami tulis diberi komentar singkat satu baris agar partner mudah memahaminya, dan kami selalu `git pull` sebelum `git push` sehingga setiap perubahan partner terbaca dulu.

3. Pengecekan ulang bersama: setelah semua perbaikan selesai, kami membaca ulang kode terhadap grammar di SPESIFIKASI.md dan menemukan bahwa cabang akhir _insert hilang saat T1, lalu memulihkannya