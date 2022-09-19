# PX 2013 machine readable specification

As guessed by reading the specs and PXWeb code.

## Parse process

### 1. Determine end of line characters, character encoding, and 

Read 64 bytes from the beginning of the file. 

Check for UTF-16 and UTF-8 BOMs.
If the file has BOMs, open the file as a memmapped character buffer
with that character encoding.
Otherwise open the file as a memmapped 

Check whether the first bytes are `CHARSET="ANSI";` followed by `\r\n`.
Consume the first row, including newline characters.



## Materials

### Extract structured and freehand data from the PX 2013 PDF

Pages 3-5.

```bash
java -jar tabula-1.0.5-jar-with-dependencies.jar \
  -i -l -f CSV -p 3-5 px-file_format_specification_2013.pdf \
   > ../pxspec/px2013-keywords.csv

pdftotext -f 6 -l 30 -raw px-file_format_specification_2013.pdf ../pxspec/px2013-details.txt
```
