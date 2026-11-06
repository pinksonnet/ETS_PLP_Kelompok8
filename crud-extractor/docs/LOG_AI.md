# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 |Alfina dan Nazwa |Cari bug dan TODO dari kode dan spesifikasi |Diterima setelah dicek |Setiap bug cocok dengan bagian spesifikasi |Test regresi dibuat gagal dulu, lalu lulus |
| 2 |Nazwa |Tulis test regresi |Diubah |Typo T.TOP dan lupa import pytest lolos karena alasan gagal tidak dicek |Baca pesan gagal pytest, pastikan karena assertion |
| 2 |Alfina dan Nazwa |Pembagian commit satu batch per orang |Diterima |Mempercepat pekerjaan |git log menunjukkan kedua anggota |

**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuinya?
