
PYTHON ?= python3

BASE_SYMBOLS := symbols/base-symbols.lib

all: generated/resistors.lib \
     generated/capacitors.lib

generated/%.lib: tables/%.csv ${BASE_SYMBOLS}
	${PYTHON} tools/parametrize.py ${BASE_SYMBOLS} $< generated/$* 