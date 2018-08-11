
PYTHON ?= python3

BASE_SYMBOLS := symbols/base-symbols.lib

DATABASE ?= "${DATABASE}"

all: generated/resistors.lib \
     generated/capacitors.lib \
	 generated/diodes.lib \
	 generated/misc.lib \
	 generated/connectors.lib \
	 generated/ics.lib \
	 generated/leds.lib \
	 generated/inductors.lib \
	 generated/transistors.lib \
	 generated/crystals.lib 

generated/%.lib: tables/%.csv ${BASE_SYMBOLS} parameterize.json
	${PYTHON} tools/parametrize.py ${BASE_SYMBOLS} $< generated/$* --config parameterize.json
	
export:
	mdb-export ${DATABASE} capacitors > tables/capacitors.csv
	mdb-export ${DATABASE} resistors > tables/resistors.csv
	mdb-export ${DATABASE} diodes > tables/diodes.csv
	mdb-export ${DATABASE} crystals > tables/crystals.csv
	mdb-export ${DATABASE} connectors > tables/connectors.csv
	mdb-export ${DATABASE} miscellaneous > tables/misc.csv
	mdb-export ${DATABASE} ics > tables/ics.csv
	mdb-export ${DATABASE} leds > tables/leds.csv
	mdb-export ${DATABASE} inductors > tables/inductors.csv
	mdb-export ${DATABASE} transistors > tables/transistors.csv

	
clean: 
	rm generated/resistors.lib
	rm generated/capacitors.lib
