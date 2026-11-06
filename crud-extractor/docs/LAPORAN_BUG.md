# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: Keyword huruf kecil dibaca sebagai identifier

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** select a from t; gagal di-parse. select menjadi token IDENT, padahal spesifikasi 2.2 mewajibkan keyword tidak peka huruf besar/kecil dengan nilai token selalu huruf besar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select a from t;
```

**Akar masalah.** Bab 4, reserved words: Lexer membaca satu kata utuh, lalu mencocokkannya ke tabel keyword. Kode lama membandingkan teks apa adanya, jadi select tidak cocok dengan SELECT. Kata reserved harus dikenali lewat satu bentuk baku (huruf besar), dan nilai token disimpan dalam bentuk itu supaya parser hanya perlu satu pembanding.

**Perbaikan.** crud/lexer.py, fungsi _word: pengecekan memakai text.upper() in KEYWORDS dan nilai token disimpan huruf besar. Alternatif: menambahkan versi huruf kecil ke KEYWORDS. Ditolak karena daftar jadi dua kali lebih panjang dan campuran seperti Select tetap lolos.

**Test regresi.** test_regresi_keyword_huruf_kecil_menjadi_ident

**Peran AI.** Menunjuk _word() sebagai lokasi bug berdasarkan spesifikasi 2.2 dan menulis perbaikannya. Verifikasi: test regresi dibuat gagal dulu, lalu pytest dijalankan setelah perbaikan; tokenize("select Select SELECT") menghasilkan tiga KEYWORD bernilai SELECT, dan selection tetap IDENT.

## Bug 2: Keyword huruf kecil dibaca sebagai identifier

**Ditemukan oleh:** Alfina · **Diperbaiki oleh:** Alfina

**Gejala.** `a <> 1` dibaca sebagai `<` lalu `>`, sehingga parser error. Spesifikasi 2.5 meminta `<>` satu token `OP` (maximal munch).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
SELECT a FROM t WHERE a <> 1;
```

**Akar masalah.** Bab 4, maximal munch: Saat melihat `<`, lexer harus mencoba lexeme terpanjang yang mungkin (`<=`, `<>`) sebelum menerima `<` saja. Kode lama hanya mengecek `=`, jadi `<>` terpecah dua. Memutuskan batas lexeme adalah tugas lexer, bukan parser.

**Perbaikan.** `crud/lexer.py`, cabang `<`: cek `=` lalu `>` lewat `_match`. Alternatif: menambah aturan khusus di parser yang menggabungkan `<` dan `>` bersebelahan. Ditolak karena itu menambal gejala di tempat yang salah, sedangkan tugas memotong lexeme ada di lexer.

**Test regresi.** test_regresi_operator_tidak_sama_dipecah_jadi_dua_token

**Peran AI.** Menunjuk cabang `<` di `_scan_token()` sebagai lokasi bug berdasarkan §2.5 dan menulis perbaikannya. Verifikasi: test regresi gagal karena assertion sebelum perbaikan, lalu lulus sesudahnya; `<>` menjadi satu token `OP`, sedangkan `<` dan `<=` tetap benar.

## Bug 4: Keyword huruf kecil dibaca sebagai identifier

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** select a from t; gagal di-parse. select menjadi token IDENT, padahal spesifikasi 2.2 mewajibkan keyword tidak peka huruf besar/kecil dengan nilai token selalu huruf besar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select a from t;
```

**Akar masalah.** Bab 4, reserved words: Lexer membaca satu kata utuh, lalu mencocokkannya ke tabel keyword. Kode lama membandingkan teks apa adanya, jadi select tidak cocok dengan SELECT. Kata reserved harus dikenali lewat satu bentuk baku (huruf besar), dan nilai token disimpan dalam bentuk itu supaya parser hanya perlu satu pembanding.

**Perbaikan.** crud/lexer.py, fungsi _word: pengecekan memakai text.upper() in KEYWORDS dan nilai token disimpan huruf besar. Alternatif: menambahkan versi huruf kecil ke KEYWORDS. Ditolak karena daftar jadi dua kali lebih panjang dan campuran seperti Select tetap lolos.

**Test regresi.** test_regresi_keyword_huruf_kecil_menjadi_ident

**Peran AI.** Menunjuk _word() sebagai lokasi bug berdasarkan spesifikasi 2.2 dan menulis perbaikannya. Verifikasi: test regresi dibuat gagal dulu, lalu pytest dijalankan setelah perbaikan; tokenize("select Select SELECT") menghasilkan tiga KEYWORD bernilai SELECT, dan selection tetap IDENT.

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

**Peran AI.** menunjuk `_synchronize()` sebagai lokasi bug berdasarkan §6 dan menulis perbaikannya. Verifikasi: `campuran_error.sql` dijalankan lewat CLI, baris 6 dan 8 sekarang terproses, dan setiap statement rusak menghasilkan tepat satu error; `pytest` penuh.

## Bug 6: Keyword huruf kecil dibaca sebagai identifier

**Ditemukan oleh:** Nazwa · **Diperbaiki oleh:** Nazwa

**Gejala.** select a from t; gagal di-parse. select menjadi token IDENT, padahal spesifikasi 2.2 mewajibkan keyword tidak peka huruf besar/kecil dengan nilai token selalu huruf besar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select a from t;
```

**Akar masalah.** Bab 4, reserved words: Lexer membaca satu kata utuh, lalu mencocokkannya ke tabel keyword. Kode lama membandingkan teks apa adanya, jadi select tidak cocok dengan SELECT. Kata reserved harus dikenali lewat satu bentuk baku (huruf besar), dan nilai token disimpan dalam bentuk itu supaya parser hanya perlu satu pembanding.

**Perbaikan.** crud/lexer.py, fungsi _word: pengecekan memakai text.upper() in KEYWORDS dan nilai token disimpan huruf besar. Alternatif: menambahkan versi huruf kecil ke KEYWORDS. Ditolak karena daftar jadi dua kali lebih panjang dan campuran seperti Select tetap lolos.

**Test regresi.** test_regresi_keyword_huruf_kecil_menjadi_ident

**Peran AI.** Menunjuk _word() sebagai lokasi bug berdasarkan spesifikasi 2.2 dan menulis perbaikannya. Verifikasi: test regresi dibuat gagal dulu, lalu pytest dijalankan setelah perbaikan; tokenize("select Select SELECT") menghasilkan tiga KEYWORD bernilai SELECT, dan selection tetap IDENT.

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

**Peran AI.** menunjuk `_join()` sebagai lokasi bug dengan membandingkan fungsi dengan aturan `join` di grammar §3, lalu menulis perbaikannya. Verifikasi: `LEFT OUTER JOIN` diterima, `LEFT JOIN` dan `INNER JOIN` tetap berfungsi; `pytest` penuh.

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

**Peran AI.** menunjuk cabang `Update` di `analyzer.py` sebagai lokasi bug berdasarkan aturan CRUD §5 dan menulis perbaikannya. Verifikasi: `UPDATE a SET v = (SELECT m FROM b)` menghasilkan `a` = U dan `b` = R; `pytest` penuh.

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

**Peran AI.** menunjuk `_insert()` sebagai lokasi TODO berdasarkan grammar spesifikasi 3 dan aturan CRUD spesifikasi 5, lalu menulis implementasinya. Verifikasi: `INSERT INTO a SELECT x FROM b` menghasilkan `a` = C dan `b` = R, dicek dengan `pytest` dan CLI.

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

**Peran AI.** menunjuk `_scan_token()` sebagai lokasi penambahan komentar blok berdasarkan §2.3 dan menulis implementasinya. Verifikasi: dua test (komentar lintas baris yang berisi `*` dilewati, dan komentar tidak ditutup melempar `LexError` di posisi pembuka), lalu `pytest` penuh.

---
