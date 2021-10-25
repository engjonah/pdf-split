#!/bin/bash
#./split.sh `find *.pdf`

cd /home/pi/Documents/pdf_split

file="${1:-/dev/stdin}"
gs \
   -oleft.pdf \
    -sDEVICE=pdfwrite \
    -g3960x6120 \
    -c"<</PageOffset [0 0]>> setpagedevice" \
    -f $file

gs  -o right.pdf \
    -sDEVICE=pdfwrite \
    -g3960x6120 \
    -c "<</PageOffset [-396 0]>> setpagedevice" \
    -f $file

pdftk \
  A=right.pdf \
  B=left.pdf \
  shuffle B A \
  output tmp.pdf \
  verbose


pdftk \
  tmp.pdf \
  cat 2-end 1 \
  output "${file%.*}"_split.pdf \
  verbose

rm tmp.pdf left.pdf right.pdf

