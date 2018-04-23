

# default color
COLOR=${2:-'#1b4971'}

if [ "$1" == "" ]; then
  echo "Usage: $0 file.png ['#color']"
  exit 0;
fi

FILE=`basename $1 .png`

if [ ! -e $FILE.png ]; then
  echo $FILE.png does not exist
  exit 1;
fi

echo "converting to bitmap"
convert $FILE.png -background White -alpha Background $FILE.ppm

echo "generating svg"
cat $FILE.ppm | potrace -t 25 --progress -s -a 0.8 --color=$COLOR -o $FILE.svg

echo "generating pdf"
cat $FILE.ppm | potrace -t 25 --progress -b pdf -a 0.8 --color=$COLOR -o $FILE.pdf

echo "cleanup"
rm $FILE.ppm
