"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

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