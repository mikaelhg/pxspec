#!/bin/env bash

# Extract structured and freehand data from the PX 2013 PDF. 

java -jar tabula-1.0.5-jar-with-dependencies.jar \
  -i -l -f CSV -p 3-5 px-file_format_specification_2013.pdf \
   > ../pxspec/px2013-keywords.csv

pdftotext -f 6 -l 30 -raw px-file_format_specification_2013.pdf ../pxspec/px2013-details.txt
