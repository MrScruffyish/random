#!/usr/bin/env bash

# Given a file with a6 pages, this will create a ps+pdf file ready to print 
# with duplex, turn on long side, on a4 paper, so it can be cut and folded 
# into signatures and create a "book"

# Notice, signatures that are not a multiple of 8 will produce some empty waste.

function error_usage(){
    echo "Usage: $0 signature  filename"
    echo "$1"
    exit 1
}
if [  $# -ne 2 ]; then
    error_usage 
fi

SIGNATUR=$1
FILE=$2
NUMPAGES=$(gs -o /dev/null -sDEVICE=bbox $FILE 2>&1 | grep HiResBoundingBox | wc -l)
OUTFILE="$FILE.$SIGNATUR.a4print"

BLOCKS=$(( ($NUMPAGES/$SIGNATUR) ))

SIGCHECK=$(( $BLOCKS * $SIGNATUR ))
if [ $SIGCHECK -ne $NUMPAGES ]; then
    MISSING_PAGES=$(( $SIGCHECK + $SIGNATUR - $NUMPAGES  ))
    echo "You can't split $NUMPAGES into $SIGNATUR signatures evenly, so the program will add $MISSING_PAGES blank pages to your document and fix it for you, or fix it manually by mixing signature sizes"
    tmpfile=$(mktemp /tmp/bookbinding.XXXXXX)
    extrapages=$(seq 0 $MISSING_PAGES |sed 's/.*/_/' |paste -sd,)
    
    # The underscore means a blank page will be added
    psselect -p1-$NUMPAGES,$extrapages $FILE $tmpfile
    FILE=$tmpfile
    BLOCKS=$(( $BLOCKS + 1 ))
fi

for x in $(seq 0 $(($BLOCKS -1)) ); do
    start=$(( $x * $SIGNATUR + 1))
    stop=$(( $x * $SIGNATUR + $SIGNATUR ))

    pages=$(seq $start $stop | paste -sd,)

    psselect -p $pages $FILE > out.$x.ps

    # Pages are placed from upper left to the right and then the line below.
    if [ $SIGNATUR -eq 8 ]; then
        pstops '8:7@1(0,0.5h)+0@1(0.5w,0.5h)+3@1(0,0)+4@1(0.5w,0),1@1(0,0.5h)+6@1(0.5w,0.5h)+5@1(0,0)+2@1(0.5w,0)'  out.$x.ps out2.$x.ps
    elif [ $SIGNATUR -eq 12 ]; then
        pstops '12:11@1(0,0.5h)+0@1(0.5w,0.5h)+3@1(0,0)+8@1(0.5w,0),1@1(0,0.5h)+10@1(0.5w,0.5h)+9@1(0,0)+2@1(0.5w,0),7@1(0,0.5h)+4@1(0.5w,0.5h),5@1(0,0.5h)+6@1(0.5w,0.5h)'  out.$x.ps out2.$x.ps
    elif [ $SIGNATUR -eq 16 ]; then
        pstops '16:15@1(0,0.5h)+0@1(0.5w,0.5h)+7@1(0,0)+8@1(0.5w,0),1@1(0,0.5h)+14@1(0.5w,0.5h)+9@1(0,0)+6@1(0.5w,0),13@1(0,0.5h)+2@1(0.5w,0.5h)+5@1(0,0)+10@1(0.5w,0),3@1(0,0.5h)+12@1(0.5w,0.5h)+11@1(0,0)+4@1(0.5w,0)'  out.$x.ps out2.$x.ps
    elif [ $SIGNATUR -eq 24 ]; then
        pstops '24:23@1(0,0.5h)+0@1(0.5w,0.5h)+11@1(0,0)+12@1(0.5w,0),1@1(0,0.5h)+22@1(0.5w,0.5h)+13@1(0,0)+10@1(0.5w,0),21@1(0,0.5h)+2@1(0.5w,0.5h)+9@1(0,0)+14@1(0.5w,0),3@1(0,0.5h)+20@1(0.5w,0.5h)+15@1(0,0)+8@1(0.5w,0),19@1(0,0.5h)+4@1(0.5w,0.5h)+7@1(0,0)+16@1(0.5w,0),5@1(0,0.5h)+18@1(0.5w,0.5h)+17@1(0,0)+6@1(0.5w,0)'  out.$x.ps out2.$x.ps
    elif [ $SIGNATUR -eq 32 ]; then
        pstops '32:31@1(0,0.5h)+0@1(0.5w,0.5h)+15@1(0,0)+16@1(0.5w,0),1@1(0,0.5h)+30@1(0.5w,0.5h)+17@1(0,0)+14@1(0.5w,0),29@1(0,0.5h)+2@1(0.5w,0.5h)+13@1(0,0)+18@1(0.5w,0),3@1(0,0.5h)+28@1(0.5w,0.5h)+19@1(0,0)+12@1(0.5w,0),27@1(0,0.5h)+4@1(0.5w,0.5h)+11@1(0,0)+20@1(0.5w,0),5@1(0,0.5h)+26@1(0.5w,0.5h)+21@1(0,0)+10@1(0.5w,0),25@1(0,0.5h)+6@1(0.5w,0.5h)+9@1(0,0)+22@1(0.5w,0),7@1(0,0.5h)+24@1(0.5w,0.5h)+23@1(0,0)+8@1(0.5w,0)'  out.$x.ps out2.$x.ps
    else
        error_usage "Supports only signature: 8, 12, 16, 24, 32"
    fi
    rm out.$x.ps

    # out.$x.ps now contains a block
done

cmd="psmerge -o$OUTFILE.ps"
for x in $(seq 0 $(($BLOCKS -1)) ); do
    cmd="$cmd out2.$x.ps"
done

$cmd

for x in $(seq 0 $(($BLOCKS -1)) ); do
    rm out2.$x.ps
done

ps2pdf $OUTFILE.ps $OUTFILE.pdf
echo "Result in $OUTFILE.ps and $OUTFILE.pdf"
