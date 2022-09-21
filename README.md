# PX 2013 machine readable specification

As guessed by reading 
the [specs](https://www.scb.se/globalassets/vara-tjanster/px-programmen/px-file_format_specification_2013.pdf),
a bunch of [PX data files](https://github.com/search?q=AXIS-VERSION+KEYS+extension%3Apx&type=Code),
and [PXWeb code](https://github.com/statisticssweden/PCAxis.Core/blob/master/PCAxis.Core/Parsers/PXFileParser.vb).

## PX file parse process

Our objective is to be able to open, parse, and process a PX file of multiple hundreds of megabytes with only a few hundred kilobytes of `malloc`'d memory.

So we have to process the file as a continuous stream, while only saving important metadata in memory, or we have to first create an index of the PX file in a separate disk file, and use that index to randomly access the PX file contents.

```mermaid
flowchart LR
    chp(Configure \n Header Parser)
    ph(Parse \n Header)
    cdp(Configure \n Data Parser)
    pd(Parse \n Data)

    chp --> ph
    ph --> cdp
    cdp --> pd
```

### 1. Configure the Header Parser

To configure the header parser, we need three pieces of information:

A. are the EOL marks `\r\n`, `\n`, or something else.

B. what the character encoding of the file is.

C. what specification version the file purports to follow.

The specification says nothing explicit about the end of line markings in the files.
Typically, the EOLs will be Windows ("\r\n"), and the character encoding (`CODEPAGE`) is `"Windows-1252"`. 
However, Google searches reveal that there are PX files in the wild with `CODEPAGE="UTF-8";`.

The specification is silent as to the possibility of PX files beginning with UTF-8 or UTF-16 BOM markers.

Open the file (as binary), and read 64 bytes (not characters) from the beginning of the file with a simple naive read.

Check whether the first bytes are `CHARSET="ANSI";` followed by `\r\n`. If so, that's the EOL marking you will use for the rest of the parse.

Read the first five lines, and check for `CODEPAGE` and `AXIS-VERSION` keywords. Save the values for those keywords to the header parser context.

### 2. Parse the Header

### 3. Configure the Data Parser

### 4. Parse the Data

There are two ways for laying out the data stored in a PX file. One for dense data cubes, where most data rows have cells with values, and one for sparse data cubes, where few of the potential data rows described by the space have values.

The dense data cube data layout has each and every data cell potentially described by the STUB × HEADER matrix space laid out, separated by spaces, with missing values especially marked as such.

The sparse data cube data layout identifies each data cube coordinate by laying out the data row by row, separated by EOL markers, and starting each row by describing a set space coordinates, followed by a whitespace character (" ") separator, followed by the data cell values for that coordinate. 

## Materials

Extract structured and freehand data from the PX 2013 PDF. 

```bash
java -jar tabula-1.0.5-jar-with-dependencies.jar \
  -i -l -f CSV -p 3-5 px-file_format_specification_2013.pdf \
   > ../pxspec/px2013-keywords.csv

pdftotext -f 6 -l 30 -raw px-file_format_specification_2013.pdf ../pxspec/px2013-details.txt
```
