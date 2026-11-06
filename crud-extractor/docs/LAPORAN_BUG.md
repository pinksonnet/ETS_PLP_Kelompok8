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

---
