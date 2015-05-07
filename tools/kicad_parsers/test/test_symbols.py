__author__ = 'MegabytePhreak'

from kicad_parsers.symbols import tokenize, quote, load_lib
from io import StringIO

#F0 "Q" 300 50 60 H V C CNN
#F1 "A06400" 400 -50 60 H V C CNN
#F5 "785-1067-1-ND" -50 -750 60 H I C CNN "Supplier 1 Part Number"
#F3 "http://aosmd.com/res/data_sheets/AO6400.pdf" 250 -850 60 H I C CNN

def test_tokenize():
    assert tokenize('F0 "Q" 300 50 60 H V C CNN') == ['F0', '"Q"', '300', '50', '60', 'H', 'V', 'C', 'CNN']
    assert tokenize('F5 "785-1067-1-ND" -50 -750 60 H I C CNN "Supplier 1 Part Number"') == \
        ['F5', '"785-1067-1-ND"', '-50', '-750', '60', 'H', 'I', 'C', 'CNN', '"Supplier 1 Part Number"']
    assert tokenize('F3  "http://aosmd.com/res/data_sheets/AO6400.pdf" 250    -850 60 H I C CNN  ') == \
        ['F3', '"http://aosmd.com/res/data_sheets/AO6400.pdf"', '250', '-850', '60', 'H', 'I', 'C', 'CNN']

def test_quote():
    assert quote('785-1067-1-ND') == '"785-1067-1-ND"'
    assert quote('Supplier 1 Part Number') == '"Supplier 1 Part Number"'
    assert quote('Supplier 1 Part Number', if_needed=True) == '"Supplier 1 Part Number"'
    assert quote('CNN', if_needed=True) == 'CNN'


TEST_LIB_DATA = """
enEESchema-LIBRARY Version 2.3
#encoding utf-8
#
# A06400
#
DEF AO6400 Q 0 0 Y N 1 F N
F0 "Q" 300 50 60 H V C CNN
F1 "AO6400" 400 -50 60 H V C CNN
F2 "Footprints:TSOP_6_950_3100X1700_AO" 50 -600 60 H I C CNN
F3 "http://aosmd.com/res/data_sheets/AO6400.pdf" 250 -850 60 H I C CNN
F4 "Digi-Key" -700 -700 60 H I C CNN "Supplier 1"
F5 "785-1067-1-ND" -50 -750 60 H I C CNN "Supplier 1 Part Number"
DRAW
P 2 0 1 0  -150 -200  -150 200 N
P 2 0 1 0  -100 -150  0 -150 N
P 2 0 1 0  -100 -100  -100 -200 N
P 3 0 1 0  50 50  150 50  100 50 N
P 4 0 1 0  -100 0  -50 50  -50 -50  -100 0 N
P 4 0 1 0  0 200  100 200  100 -200  0 -200 N
P 4 0 1 0  100 50  50 -50  150 -50  100 50 N
P 5 0 1 0  -100 50  -100 -50  -100 0  0 0  0 -300 N
P 6 0 1 0  300 250  0 250  0 150  -100 150  -100 200  -100 100 N
X D 1 0 450 200 D 50 50 1 1 P
X D 2 100 450 200 D 50 50 1 1 P
X G 3 -350 -200 200 R 50 50 1 1 P
X S 4 0 -450 200 U 50 50 1 1 P
X D 5 200 450 200 D 50 50 1 1 P
X D 6 300 450 200 D 50 50 1 1 P
ENDDRAW
ENDDEF
#
#End Library
"""

def test_load_lib_1():
    symbols = load_lib(StringIO(TEST_LIB_DATA))

    assert len(symbols) == 1
    assert symbols[0].serialize() == """\
DEF AO6400 Q 0 0 Y N 1 F N
F0 "Q" 300 50 60 H V C CNN
F1 "AO6400" 400 -50 60 H V C CNN
F2 "Footprints:TSOP_6_950_3100X1700_AO" 50 -600 60 H I C CNN
F3 "http://aosmd.com/res/data_sheets/AO6400.pdf" 250 -850 60 H I C CNN
F4 "Digi-Key" -700 -700 60 H I C CNN "Supplier 1"
F5 "785-1067-1-ND" -50 -750 60 H I C CNN "Supplier 1 Part Number"
DRAW
P 2 0 1 0  -150 -200  -150 200 N
P 2 0 1 0  -100 -150  0 -150 N
P 2 0 1 0  -100 -100  -100 -200 N
P 3 0 1 0  50 50  150 50  100 50 N
P 4 0 1 0  -100 0  -50 50  -50 -50  -100 0 N
P 4 0 1 0  0 200  100 200  100 -200  0 -200 N
P 4 0 1 0  100 50  50 -50  150 -50  100 50 N
P 5 0 1 0  -100 50  -100 -50  -100 0  0 0  0 -300 N
P 6 0 1 0  300 250  0 250  0 150  -100 150  -100 200  -100 100 N
X D 1 0 450 200 D 50 50 1 1 P
X D 2 100 450 200 D 50 50 1 1 P
X G 3 -350 -200 200 R 50 50 1 1 P
X S 4 0 -450 200 U 50 50 1 1 P
X D 5 200 450 200 D 50 50 1 1 P
X D 6 300 450 200 D 50 50 1 1 P
ENDDRAW
ENDDEF\
"""

def test_field_read():
     symbol = load_lib(StringIO(TEST_LIB_DATA))[0]

     assert symbol.get_field('Name') == 'AO6400'
     assert symbol.get_field('Reference') == 'Q'
     assert symbol.get_field('Footprint') == 'Footprints:TSOP_6_950_3100X1700_AO'
     assert symbol.get_field('Datasheet') == 'http://aosmd.com/res/data_sheets/AO6400.pdf'
     assert symbol.get_field('Supplier 1') == 'Digi-Key'

def test_field_write():
     symbol = load_lib(StringIO(TEST_LIB_DATA))[0]

     symbol.set_name('abcd')
     assert symbol.get_field('Name') == 'abcd'

     symbol.set_reference('M')
     assert symbol.get_field('Reference') == 'M'

     assert symbol._lines[0] == 'DEF abcd M 0 0 Y N 1 F N'

def test_field_create():
    symbol = load_lib(StringIO(TEST_LIB_DATA))[0]

    symbol.set_or_add_field("Test Field","Test Value")
    assert symbol.get_field("Test Field") == "Test Value"
