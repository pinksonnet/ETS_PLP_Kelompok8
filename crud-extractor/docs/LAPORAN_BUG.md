# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: Keyword huruf kecil dibaca sebagai identifier

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** `select a from t;` gagal di-parse. `select` menjadi token `IDENT`, padahal spesifikasi 2.2 mewajibkan keyword tidak peka huruf besar/kecil dengan nilai token selalu huruf besar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select a from t;
```

**Akar masalah.** Bab 4, reserved words: Lexer membaca satu kata utuh, lalu mencocokkannya ke tabel keyword. Kode lama membandingkan teks apa adanya, jadi `select` tidak cocok dengan `SELECT`. Kata reserved harus dikenali lewat satu bentuk baku (huruf besar), dan nilai token disimpan dalam bentuk itu supaya parser hanya perlu satu pembanding.

**Perbaikan.** `crud/lexer.py`, fungsi `_word`: pengecekan memakai `text.upper() in KEYWORDS` dan nilai token disimpan huruf besar. Alternatif: menambahkan versi huruf kecil ke `KEYWORDS`. Ditolak karena daftar jadi dua kali lebih panjang dan campuran seperti `Select` tetap lolos.

**Test regresi.** test_regresi_keyword_huruf_kecil_menjadi_ident

**Peran AI.** Menunjuk `_word()` sebagai lokasi bug berdasarkan spesifikasi 2.2 dan menulis perbaikannya. Verifikasi: test regresi dibuat gagal dulu, lalu `pytest` dijalankan setelah perbaikan; `tokenize("select Select SELECT")` menghasilkan tiga `KEYWORD` bernilai `SELECT`, dan `selection` tetap `IDENT`.

---

## Bug 2: `<>` terpecah menjadi dua token

**Ditemukan oleh:** Alfina · **Diperbaiki oleh:** Alfina

**Gejala.** `a <> 1` dibaca sebagai `<` lalu `>`, sehingga parser error. Spesifikasi 2.5 meminta `<>` satu token `OP` (maximal munch).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT a FROM t WHERE a <> 1;
```

**Akar masalah.** Bab 4, maximal munch: Saat melihat `<`, lexer harus mencoba lexeme terpanjang yang mungkin (`<=`, `<>`) sebelum menerima `<` saja. Kode lama hanya mengecek `=`, jadi `<>` terpecah dua. Memutuskan batas lexeme adalah tugas lexer, bukan parser.

**Perbaikan.** `crud/lexer.py`, cabang `<`: cek `=` lalu `>` lewat `_match`. Alternatif: menambah aturan khusus di parser yang menggabungkan `<` dan `>` bersebelahan. Ditolak karena itu menambal gejala di tempat yang salah, sedangkan tugas memotong lexeme ada di lexer.

**Test regresi.** test_regresi_operator_tidak_sama_dipecah_jadi_dua_token

**Peran AI.** Menunjuk cabang `<` di `_scan_token()` sebagai lokasi bug berdasarkan spesifikasi 2.5 dan menulis perbaikannya. Verifikasi: test regresi gagal karena assertion sebelum perbaikan, lalu lulus sesudahnya; `<>` menjadi satu token `OP`, sedangkan `<` dan `<=` tetap benar.

---

## Bug 3: `''` di dalam string mengakhiri string

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** `'O''Brien'` terpotong di `O`. Spesifikasi 2.4: dua kutip berturut-turut mewakili satu kutip, hasilnya satu `STRING` bernilai `O'Brien`.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT a FROM t WHERE n = 'O''Brien';
```

**Akar masalah.** Bab 4, string literal: Pada `'`, lexer langsung menganggapnya penutup tanpa melihat karakter sesudahnya. Perlu lookahead satu karakter: jika yang berikutnya `'` juga, itu kutip yang di-escape, dan string lanjut.

**Perbaikan.** `crud/lexer.py`, fungsi `_string`: jika setelah `'` masih ada `'`, tambahkan satu `'` ke nilai dan lanjut. Alternatif: menghapus semua `''` lewat pre-processing teks. Ditolak karena merusak nomor kolom dan menyentuh teks di luar string.

**Test regresi.** test_regresi_dua_kutip_dalam_string_memotong_string

**Peran AI.** Menunjuk `_string()` sebagai lokasi bug berdasarkan spesifikasi 2.4 dan menulis perbaikannya. Verifikasi: `'O''Brien'` menghasilkan satu `STRING` bernilai `O'Brien`, dan string yang tidak ditutup tetap `LexError`; semua test dijalankan dengan `pytest`.

---

## Bug 4: AND dan OR di satu tingkat presedensi

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** `a=1 OR b=2 AND c=3` dibaca `(a=1 OR b=2) AND c=3`; di `--ast` akar `where` di `audit.sql` baris 2 adalah `AND`. Spesifikasi 3.1: `AND` mengikat lebih kuat dari `OR`.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT a FROM t WHERE a = 1 OR b = 2 AND c = 3;
```

**Akar masalah.** Bab 6, presedensi: Dalam recursive descent, tiap tingkat presedensi adalah satu fungsi yang memanggil tingkat yang lebih kuat. Satu fungsi untuk `AND` dan `OR` membuat keduanya setara dan dikelompokkan dari kiri ke kanan. Setelah dipecah, `OR` memanggil `AND`, sehingga `AND` selalu terbentuk lebih dalam di pohon.

**Perbaikan.** `crud/parser.py`: `_logical` dipecah menjadi `_or` (memanggil `_and`) dan `_and` (memanggil `_not`). Alternatif: parsing Pratt dengan tabel presedensi. Ditolak karena grammar spesifikasi sudah berbentuk rantai aturan per tingkat.

**Test regresi.** test_regresi_and_or_berada_di_tingkat_presedensi_sama

**Peran AI.** Menunjuk `_logical()` sebagai lokasi bug berdasarkan spesifikasi 3.1 dan menulis perbaikannya. Verifikasi: output `--ast` pada `audit.sql` baris 2 dibandingkan sebelum dan sesudah (akar `where` berubah dari `AND` menjadi `OR`), lalu `pytest` penuh.

---

## Bug 5: Error recovery membuang sampai akhir file

**Ditemukan oleh:** Alfina · **Diperbaiki oleh:** Alfina

**Gejala.** Setelah satu statement rusak, semua statement sesudahnya hilang. Parser melewatkan baris 6 dan 8 di `campuran_error.sql`. Spesifikasi 6: buang sampai dan termasuk `;` berikutnya, lalu lanjut.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT FROM a;
SELECT x FROM b;
```

**Akar masalah.** Bab 6, panic mode: Setelah error, parser harus sinkron kembali ke titik aman (di sini sesudah `;`). Kode lama tidak berhenti di titik aman dan terus membuang token sampai akhir file, sehingga statement valid sesudahnya ikut hilang.

**Perbaikan.** `crud/parser.py`, `_synchronize`: berhenti setelah `;` pertama. Alternatif: berhenti di keyword `SELECT` berikutnya. Ditolak karena subquery juga memakai `SELECT`.

**Test regresi.** test_regresi_error_recovery_membuang_statement_sesudahnya

**Peran AI.** Menunjuk `_synchronize()` sebagai lokasi bug berdasarkan spesifikasi 6 dan menulis perbaikannya. Verifikasi: `campuran_error.sql` dijalankan lewat CLI, baris 6 dan 8 sekarang terproses, dan setiap statement rusak menghasilkan tepat satu error; `pytest` penuh.

---

## Bug 6: `LEFT OUTER JOIN` ditolak

**Ditemukan oleh:** Alfina · **Diperbaiki oleh:** Alfina

**Gejala.** `LEFT OUTER JOIN` menghasilkan parse error. Grammar: `"LEFT" [ "OUTER" ]`.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT a FROM t LEFT OUTER JOIN u ON t.i = u.i;
```

**Akar masalah.** Bab 6, grammar vs fungsi: Setiap bagian opsional grammar (`[ "OUTER" ]`) harus punya padanan di fungsi parser. Kode lama tidak menangani `OUTER`, jadi kata itu dianggap token tak terduga.

**Perbaikan.** `crud/parser.py`, `_join`: `_match_kw("OUTER")` setelah `LEFT`. Alternatif: membuat `OUTER` menjadi keyword yang diabaikan di lexer. Ditolak karena itu mengubah arti kata di semua konteks.

**Test regresi.** test_regresi_left_outer_join_ditolak_parser

**Peran AI.** Menunjuk `_join()` sebagai lokasi bug dengan membandingkan fungsi dengan aturan `join` di grammar spesifikasi 3, lalu menulis perbaikannya. Verifikasi: `LEFT OUTER JOIN` diterima, `LEFT JOIN` dan `INNER JOIN` tetap berfungsi; `pytest` penuh.

---

## Bug 7: Pencarian scope dari terluar

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** `x.total` di `audit.sql` baris 12 ter-resolve ke `pelanggan`, bukan `pesanan`. Spesifikasi 4.3: qualifier dicari dari scope terdalam, sehingga alias subquery menutupi alias luar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT 1 FROM t p WHERE p.a IN (SELECT p.b FROM u p);
```

**Akar masalah.** Bab 11, scope chain: Resolusi variabel harus mulai dari scope terdalam lalu naik ke induk, supaya nama di scope dalam menutupi nama yang sama di luar (shadowing). Kode lama mencari dari terluar, jadi nama luar menang.

**Perbaikan.** `crud/resolver.py`, `_lookup`: iterasi chain dari terdalam tanpa `reversed`. Alternatif: satu dict gabungan semua scope. Ditolak karena tidak bisa menyatakan shadowing.

**Test regresi.** test_regresi_alias_subquery_tidak_menutupi_alias_luar

**Peran AI.** Menunjuk `_lookup()` sebagai lokasi bug berdasarkan spesifikasi 4.3 dan menulis perbaikannya. Verifikasi: output `--ast` pada `audit.sql` baris 12 dibandingkan sebelum dan sesudah (`x.total` berubah dari `pelanggan` menjadi `pesanan`); `pytest` penuh.

---

## Bug 8: Scope DELETE tidak di-pop

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** `s.id` di `audit.sql` baris 18 ter-resolve ke `sesi`, tabel statement sebelumnya. Spesifikasi 4.5: statement berikutnya tidak boleh melihat alias statement sebelumnya.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
DELETE FROM a x WHERE x.i = 1;
SELECT x.i FROM b;
```

**Akar masalah.** Bab 11, scope stack: Setiap `_push` harus berpasangan dengan `_pop` agar scope hanya hidup selama statement-nya. `_delete` melakukan push tanpa pop, jadi alias bocor dan terlihat oleh statement berikutnya. 

**Perbaikan.** `crud/resolver.py`, `_delete`: tambah `self._pop()` di akhir. Alternatif: mereset seluruh stack di tiap awal statement. Ditolak karena menyembunyikan kesalahan push/pop alih-alih memperbaikinya.

**Test regresi.** test_regresi_alias_delete_bocor_ke_statement_berikutnya

**Peran AI.** Menunjuk `_delete()` sebagai lokasi bug berdasarkan spesifikasi 4.5 dan menulis perbaikannya. Verifikasi: `--ast` pada `audit.sql` baris 18 sekarang menghasilkan error alias tidak terdefinisi untuk `s.id`, bukan ter-resolve ke `sesi`; `pytest` penuh.

---

## Bug 9: Subquery di UPDATE ditandai U

**Ditemukan oleh:** Alfina · **Diperbaiki oleh:** Alfina

**Gejala.** Tabel yang dibaca lewat subquery di `UPDATE` dihitung `U`. Spesifikasi 5: membaca lewat subquery selalu `R`.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
UPDATE a SET v = (SELECT m FROM b);
```

**Akar masalah.** spesifikasi 5, analisis di atas AST: Analyzer menurunkan jenis operasi ke subtree. Pada cabang Update, subquery diberi `U` padahal aturan lokal proyek bilang membaca lewat subquery selalu `R`. Operasi yang diturunkan harus sesuai peran tabel, bukan jenis statement luarnya.

**Perbaikan.** `crud/analyzer.py`, cabang Update: ganti `"U"` jadi `"R"` pada dua pemanggilan `_collect`. Alternatif: mengoreksi hasil di akhir. Ditolak karena menambal gejala, bukan sumbernya.

**Test regresi.** test_regresi_subquery_di_update_dihitung_u

**Peran AI.** Menunjuk cabang `Update` di `analyzer.py` sebagai lokasi bug berdasarkan aturan CRUD spesifikasi 5 dan menulis perbaikannya. Verifikasi: `UPDATE a SET v = (SELECT m FROM b)` menghasilkan `a` = U dan `b` = R; `pytest` penuh.

---

## Bug 10: `_insert` mengembalikan `None`

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** `INSERT INTO t`; membuat program crash dengan `AttributeError: 'NoneType' object has no attribute 'line'`. Spesifikasi 6: seharusnya satu `ParseError` dan statement sesudahnya tetap diproses.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
INSERT INTO t;
```

**Akar masalah.** Bab 6, grammar vs fungsi: Alternatif wajib di grammar berarti fungsi harus selalu mengembalikan node atau melempar error. Jika tidak ada alternatif yang cocok dan fungsi tidak raise, Python mengembalikan `None`, yang diperlakukan sebagai statement valid dan baru crash di tahap berikutnya.

**Perbaikan.** `crud/parser.py`, `_insert`: `raise ParseError("diharapkan VALUES atau SELECT", self._peek())` di akhir fungsi. Alternatif: memeriksa `None` di pipeline. Ditolak karena kesalahan harus ditolak di parser.

**Test regresi.** test_regresi_insert_tanpa_values_atau_select_harus_parse_error

**Peran AI.** Menemukan bug ini lewat pengecekan ulang `parser.py` terhadap grammar spesifikasi 3 dan menunjuk akhir `_insert()` sebagai lokasinya (spesifikasi 6), lalu menulis perbaikannya. Verifikasi: `INSERT INTO t;` dicoba langsung dan menghasilkan `AttributeError` sebelum perbaikan; test regresi dibuat gagal dulu, lalu lulus setelah `raise ParseError`; statement valid sesudahnya tetap diproses dan `pytest` penuh lulus.

---

## T1: `INSERT ... SELECT` belum didukung

**Ditemukan oleh:** Alfina berdasarkan penanda TODO(T1) pada kode awal · **Diperbaiki oleh:** Alfina

**Gejala.** `INSERT INTO a SELECT ...` tidak di-parse. Spesifikasi 3 dan 5: tabel target C, tabel sumber R.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
INSERT INTO a SELECT x FROM b;
```

**Akar masalah.** Grammar `insert_stmt` punya alternatif `VALUES ... | select_stmt`. Fungsi hanya mengimplementasikan satu alternatif, jadi alternatif kedua belum ada.

**Perbaikan.** `crud/parser.py`, `_insert`: `return ast.Insert(table, columns, [], self._select(), line=start.line)`. Alternatif: `values=None`. Ditolak karena kode lain mengiterasi `values`, dan API node tidak boleh diubah.

**Test regresi.** test_regresi_insert_select_belum_didukung

**Peran AI.** Menunjuk `_insert()` sebagai lokasi TODO berdasarkan grammar spesifikasi 3 dan aturan CRUD spesifikasi 5, lalu menulis implementasinya. Verifikasi: `INSERT INTO a SELECT x FROM b` menghasilkan `a` = C dan `b` = R, dicek dengan `pytest` dan CLI.

---

## T2: Kolom tanpa qualifier belum di-resolve

**Ditemukan oleh:** Nazwa berdasarkan penanda TODO(T2) pada kode awal · **Diperbaiki oleh:** Nazwa

**Gejala.** `ColumnRef.resolved` tetap `None` untuk kolom tanpa qualifier. Spesifikasi 4.3: satu tabel di-resolve, lebih dari satu menghasilkan warning `kolom 'nama' ambigu tanpa skema`.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT nama FROM pelanggan;
```

**Akar masalah.** Bab 11, resolving variable: Kolom tanpa qualifier hanya dilihat di scope terdalam. Dengan satu tabel hasilnya pasti, tapi dengan beberapa tabel tidak bisa dipastikan tanpa skema, jadi hanya bisa memberi warning.

**Perbaikan.** `crud/resolver.py`, `_column`: lihat hanya scope terdalam; 1 tabel resolve, lebih dari 1 warning, 0 tabel warning; cek `if self.scope` karena `INSERT ... VALUES` tidak punya scope. Alternatif: mencari ke semua scope luar. Ditolak karena spesifikasi menyebut hanya scope terdalam.

**Test regresi.** test_regresi_kolom_tanpa_qualifier_tidak_diresolusi dan test_regresi_kolom_ambigu_menghasilkan_warning

**Peran AI.** Menunjuk `_column()` sebagai lokasi TODO berdasarkan spesifikasi 4.3 dan menulis implementasinya. Verifikasi: dua test (satu tabel ter-resolve, lebih dari satu tabel menghasilkan warning), dan `INSERT ... VALUES` tidak crash karena tidak punya scope; `pytest` penuh.

---

## T3: Komentar blok belum didukung

**Ditemukan oleh:** Alfina berdasarkan penanda TODO(T3) pada kode awal · **Diperbaiki oleh:** Alfina

**Gejala.** `/* ... */` tidak dikenali sebagai komentar. Spesifikasi 2.3: boleh lintas baris, boleh berisi `*`, tidak menghasilkan token, dan yang tidak ditutup adalah `LexError`.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
/* komentar
   dua baris */
SELECT a FROM t;
```

**Akar masalah.** Bab 4, komentar: Komentar tidak menghasilkan token, jadi lexer harus mengonsumsinya sampai penutup `*/` tanpa ikut mengirim ke parser. Perlu lookahead dua karakter, dan penutup yang tidak ketemu harus jadi error dengan posisi pembuka supaya mudah ditemukan.

**Perbaikan.** `crud/lexer.py`, `_scan_token`: setelah `/*`, maju sampai `*/`, dan `LexError` di posisi pembuka jika tidak ketemu. Alternatif: memakai regex untuk menghapus komentar. Ditolak karena posisi baris dan kolom token ikut bergeser.

**Test regresi.** `test_regresi_komentar_blok_lintas_baris_dilewati` dan `test_regresi_komentar_blok_tidak_ditutup_melempar_lex_error`

**Peran AI.** Menunjuk `_scan_token()` sebagai lokasi penambahan komentar blok berdasarkan spesifikasi 2.3 dan menulis implementasinya. Verifikasi: dua test (komentar lintas baris yang berisi `*` dilewati, dan komentar tidak ditutup melempar `LexError` di posisi pembuka), lalu `pytest` penuh.

---
