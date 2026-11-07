# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No  | Siapa            | Prompt / tugas (ringkas)                                           | Hasil: diterima, diubah, atau ditolak | Alasan                                                                  | Cara verifikasi                                                                                          |
| --- | ---------------- | ------------------------------------------------------------------ | ------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 1   | Alfina dan Nazwa | Cari bug dan TODO dari kode dan spesifikasi                        | Diterima setelah dicek                | Setiap bug cocok dengan bagian spesifikasi                              | Test regresi dibuat gagal dulu, lalu lulus                                                               |
| 2   | Nazwa            | Tulis test regresi                                                 | Diubah                                | Typo T.TOP dan lupa import pytest lolos karena alasan gagal tidak dicek | Baca pesan gagal pytest, pastikan karena assertion                                                       |
| 3   | Alfina dan Nazwa | Pembagian commit satu batch per orang                              | Diterima                              | Mempercepat pekerjaan                                                   | git log menunjukkan kedua anggota                                                                        |
| 4   | Nazwa            | Cek ulang `_insert` terhadap grammar setelah T1                    | Diterima                              | `raise` terakhir di `_insert` ikut terhapus saat blok T1 diganti         | `INSERT INTO t;` dicoba langsung dan menghasilkan `AttributeError`; setelah `raise` dipulihkan, test lulus |
| 5   | Alfina dan Nazwa | Derivasi ground truth `audit.sql` dan `pemeliharaan.sql`           | Diterima setelah diperiksa manual     | Aturan dosen: label dari spesifikasi, bukan dari output tool            | Dicocokkan baris demi baris dengan spesifikasi bagian 5, lalu `evaluate.py` memberi parser P=1.00 R=1.00 |
| 6   | Alfina dan Nazwa | Menyusun draf laporan bug, kartu desain, laporan akhir, dan log AI | Diterima dan diubah                   | Aturan dosen: label dari spesifikasi, bukan dari output tool            | Membaca ulang dan saling menjelaskan secara lisan                                                        |

**Refleksi**.
AI paling membantu saat membandingkan kode dengan spesifikasi baris demi baris dan menemukan bug yang tidak terlihat dari gejalanya, seperti bug 10. AI juga membantu menyiapkan kerangka dokumen dan test. 
AI keliru atau tidak membantu pada test regresi yang lolos dengan alasan salah (typo `T.TOP` dan lupa `import pytest`), dan kami baru sadar setelah membaca pesan gagal pytest dengan teliti. 
Pelajarannya: keluaran AI harus selalu diverifikasi lewat test yang dijalankan sendiri, bukan diterima begitu saja.
