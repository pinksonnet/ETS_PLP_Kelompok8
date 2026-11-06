# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

| No  | Keputusan                                                                                  | Alternatif yang ditolak                 | Alasan                                                                                                                                                                  |
| --- | ------------------------------------------------------------------------------------------ | --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | AND dan OR dipecah per tingkat presedensi: `_or` memanggil `_and`, `_and` memanggil `_not` | Parsing Pratt dengan tabel presedensi   | Grammar spesifikasi sudah berbentuk rantai aturan per tingkat, jadi recursive descent bisa dicocokkan baris demi baris. Pratt lebih rumit untuk jumlah operator sedikit |
| 2   | Error recovery membuang token sampai `;` pertama                                           | Berhenti di keyword `SELECT` berikutnya | Subquery juga memakai `SELECT`, jadi satu statement bisa pecah menjadi beberapa error. Spesifikasi 6 mewajibkan tepat satu error per statement rusak`                   |
| 3   | Lookup alias dari scope terdalam ke luar                                                   | Satu dict gabungan semua scope          | Satu dict tidak bisa menyatakan shadowing, dan correlated subquery butuh rantai induk                                                                                   |
| 4   | Kolom tanpa qualifier hanya melihat scope terdalam                                         | Mencari ke semua scope luar             | Sesuai spesifikasi 4.3. Kelemahan: tanpa skema, dengan lebih dari satu tabel hanya bisa memberi warning ambigu dan `resolved` tetap `None`                              |
| 5   | `INSERT ... SELECT` memakai `values=[]` dan sumber di field `query`                        | `values=None`; node baru `InsertSelect` | API node tidak boleh diubah (spec 7); resolver dan analyzer sudah melakukan `for row in ins.values`                                                                     |
