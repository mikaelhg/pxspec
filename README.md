# PX 2013 machine readable specification

As guessed by reading 
the [specs](https://www.scb.se/globalassets/vara-tjanster/px-programmen/px-file_format_specification_2013.pdf),
a bunch of [PX data files](https://github.com/search?q=AXIS-VERSION+KEYS+extension%3Apx&type=Code),
and [PXWeb code](https://github.com/statisticssweden/PCAxis.Core/blob/master/PCAxis.Core/Parsers/PXFileParser.vb).

## PX file parse process

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

We want to know what kinds of EOL markings we have in this file, as well as the character encoding.
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

## Materials

Extract structured and freehand data from the PX 2013 PDF. 

```bash
java -jar tabula-1.0.5-jar-with-dependencies.jar \
  -i -l -f CSV -p 3-5 px-file_format_specification_2013.pdf \
   > ../pxspec/px2013-keywords.csv

pdftotext -f 6 -l 30 -raw px-file_format_specification_2013.pdf ../pxspec/px2013-details.txt
```
