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