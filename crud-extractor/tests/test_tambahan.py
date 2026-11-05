"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
import pytest
from crud.lexer import tokenize, LexError, TokenType as T
from crud.parser import parse_sql
from crud.resolver import Resolver
from crud.analyzer import analyze_statement
from crud.pipeline import analyze_source

def test_regresi_keyword_huruf_kecil_menjadi_ident():
    tokens = tokenize("select Select SELECT")
    assert [(t.type, t.value) for t in tokens[:3]] == [(T.KEYWORD, "SELECT")] * 3

def test_regresi_operator_tidak_sama_dipecah_jadi_dua_token():
    #<> harus satu token OP, bukan '<', lalu '>' (maximal munch, spec 2.5)
    tokens = tokenize("a <> b")
    assert [(t.type, t.value) for t in tokens[:3]] == [
        (T.IDENT, "a"), (T.OP, "<>"), (T.IDENT, "b")
    ]

def test_regresi_dua_kutip_dalam_string_memotong_string():
    # '' di dalam string harus jadi satu karakter kutip, bukan akhir string (spec 2.4)
    tokens = tokenize("'O''Brien'")
    assert tokens[0].type == T.STRING and tokens[0].value == "O'Brien"
    assert tokens[1].type == T.EOF

def test_regresi_komentar_blok_lintas_baris_dilewati():
    # Komentar blok tidak menghasilkan token dan posisi baris/kolom harus tetap benar (spec 2.3)
    tokens = tokenize("/* a * b\n c */ x")
    assert (tokens[0].type, tokens[0].value) == (T.IDENT, "x")
    assert (tokens[0].line, tokens[0].col) == (2, 7)

def test_regresi_komentar_blok_tidak_ditutup_melempar_lex_error():
    # Komentar yang tidak ditutup harus LexError, bukan diam-diam menelan sisa input (spec 2.3)
    with pytest.raises(LexError):
        tokenize("/* tidak ditutup")

def test_regresi_and_or_berada_di_tingkat_presedensi_sama():
    # AND harus mengikat lebih kuat dari OR: a=1 OR (b=2 AND c=3) (spec 3.1)
    script = parse_sql("SELECT a FROM t WHERE a = 1 OR b = 2 AND c = 3")
    where = script.statements[0].where
    assert where.op == "OR"
    assert where.right.op == "AND"

def test_regresi_error_recovery_membuang_statement_sesudahnya():
    # Setelah error, parser lanjut ke statement setelah ';' (spec 6)
    script = parse_sql("SELECT FROM a; SELECT x FROM b")
    assert len(script.errors) == 1
    assert len(script.statements) == 1

def test_regresi_left_outer_join_ditolak_parser():
    # OUTER bersifat opsional setelah LEFT (spec 3)
    script = parse_sql("SELECT a FROM t LEFT OUTER JOIN u ON t.i = u.i")
    assert script.errors == []
    assert script.statements[0].joins[0].kind == "LEFT"

def test_regresi_insert_select_belum_didukung():
    # INSERT ... SELECT: tabel target C, tabel sumber R (spec 3 dan 5)
    script = parse_sql("INSERT INTO a SELECT x FROM b")
    assert script.errors == []
    assert analyze_statement(script.statements[0]) == {"a": {"C"}, "b": {"R"}}

def test_regresi_alias_subquery_tidak_menutupi_alias_luar():
    # Alias di subquery harus menutupi alias luar yang sama (shadowing, spec 4.3)
    hasil = analyze_source("SELECT 1 FROM t p WHERE p.a IN (SELECT p.b FROM u p)")
    assert hasil.statements[0].columns == {("t", "a", "R"), ("u", "b", "R")}

def test_regresi_alias_delete_bocor_ke_statement_berikutnya():
    # Alias dari DELETE tidak boleh terlihat oleh statement sesudahnya (spec 4.5)
    hasil = analyze_source("DELETE FROM a x WHERE x.i = 1; SELECT x.i FROM b")
    assert [d.level for d in hasil.diagnostics] == ["error"]
    assert "'x'" in hasil.diagnostics[0].message

def test_regresi_kolom_tanpa_qualifier_tidak_diresolusi():
    # Satu tabel di scope terdalam: kolom di-resolve ke tabel itu (spec 4.3)
    hasil = analyze_source("SELECT nama FROM pelanggan")
    assert hasil.statements[0].columns == {("pelanggan", "nama", "R")}

def test_regresi_kolom_ambigu_menghasilkan_warning():
    # Dua tabel di scope terdalam: warning ambigu, resolved tetap None (spec 4.3)
    hasil = analyze_source("SELECT a FROM t, u")
    assert [d.level for d in hasil.diagnostics] == ["warning"]
    assert "ambigu" in hasil.diagnostics[0].message
    assert hasil.statements[0].columns == set()

def test_regresi_subquery_di_update_dihitung_u():
    # Tabel yang dibaca lewat subquery selalu R, apa pun statement luarnya (spec 5)
    script = parse_sql("UPDATE a SET v = (SELECT m FROM b) WHERE k IN (SELECT k FROM c)")
    assert analyze_statement(script.statements[0]) == {"a": {"U"}, "b": {"R"}, "c": {"R"}}

def test_tepi_komentar_blok_berisi_bintang_dan_lintas_baris():
    # '*' di dalam komentar jangan dikira penutup; hanya pasangan '*/' yang menutup
    tokens = tokenize("/* a * b ** c\n d */ x")
    assert [(t.type, t.value) for t in tokens] == [(T.IDENT, "x"), (T.EOF, "")]

def test_tepi_string_empat_kutip_bernilai_satu_kutip():
    # '''' = kutip buka + '' (satu kutip) + kutip tutup; salah hitung membuat string tidak tertutup
    tokens = tokenize("''''")
    assert tokens[0].type == T.STRING and tokens[0].value == "'"

def test_tepi_update_tanpa_tabel_satu_error_dan_statement_berikutnya_jalan():
    # Error tepat di ';' : synchronize harus tetap membuangnya, bukan melompati statement sesudahnya
    hasil = analyze_source("UPDATE;\nSELECT x FROM b;")
    assert len(hasil.parse_errors) == 1
    assert hasil.matrix() == {"b": "R"}

def test_regresi_insert_tanpa_values_atau_select_harus_parse_error():
    # Cabang akhir _insert dulu mengembalikan None dan membuat pipeline crash (spec 6)
    hasil = analyze_source("INSERT INTO t (a); SELECT x FROM b;")
    assert len(hasil.parse_errors) == 1
    assert hasil.matrix() == {"b": "R"}

