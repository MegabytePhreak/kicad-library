
PYTHON ?= python3

BASE_SYMBOLS := symbols/base-symbols.lib



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
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb capacitors > tables/capacitors.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb resistors > tables/resistors.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb diodes > tables/diodes.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb crystals > tables/crystals.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb connectors > tables/connectors.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb miscellaneous > tables/misc.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb ics > tables/ics.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb leds > tables/leds.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb inductors > tables/inductors.csv
	mdb-export ../../Dropbox/Altium\ Libraries/Components/Components.mdb transistors > tables/transistors.csv

	
clean: 
	rm generated/resistors.lib
	rm generated/capacitors.lib