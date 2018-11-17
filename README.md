
# kicad-library

My database/csv backed KiCAD library implementation.
The structure of these libraries is that each component in the final library is created from three distinct items:
1. The PCB footprint, repesented by standard KiCAD footprints in the footprints.pretty directory.
2. The symbol, which is logically represented by the symbols in the base-symbols library under the symbols directory. AS KiCAD lacks a symbol/part abstraction, physically these are copies to the output libraries.
3. The part, which is represented by a row in one of the CSV files in the tables directory. A part connects a footprint, symbol and metadata. Each part materialized as a seperate KiCAD symbol by the parameterization process.

Currently the input CSV files are derived from an unpublished MS Access database for cross-compatibility with my previous proprietary CAD tool. Becuase the library originated with this tools, the set of symbols is not complete, and only parts in the tables where a matching symbol exists in the base-symbols are actually generated. In the future the CSV files should become the primary data source.

This part/footprint/symbol seperation is based on the EDA library design patterns I have observed in several seperate hardware engineering organizations.
Compared to the stock KiCAD libraries it is particularly advantageous for passives, as it allows exact part numbers and sourceing information to be directly associated with each component with little effort.
This simplifies the process of ordering components to build a project. Overall it provides a more comprehensive data model while avoiding duplication of effort.


## Parameterization Process

The process of building the final symbol libraries from the base-symbols and tables is reffered to as parameterization, as the graphical symbol data is copied verbatim from base-symbols.
Only the parameters are changed for each output symbol.

The parameterization process is performed using the parameterize.py script under tools, written in python3. Parts of the process are controlled by parameterize.json, which allows various rules to be applied.
In particular, fields may be renamed, ignored or made visible/invisible on the schematic. Strings may also be prepended to field values (such as footprint library names).
The rules may be applied globally or on a per-table basis, including negation of parameters previously set.

In normal usage it is suffient to make edits to the csv tables, base-symbols library or parameterize.json files and run make in the library root. This will regenerate libraries as needed.


