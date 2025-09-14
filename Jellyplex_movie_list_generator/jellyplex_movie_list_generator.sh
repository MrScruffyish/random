#!/bin/bash

# Init stuff
TMPFILE=$(mktemp -p /tmp XXXXXXXXXXXXXXXX)
MOVIES="$TMPFILE.movies"
SERIES="$TMPFILE.series"
TEX="$TMPFILE.tex"
DVI="$TMPFILE.dvi"
PDF="$TMPFILE.pdf"

echo "" > $MOVIES
echo "" > $SERIES

for basedir in "$@"; do
    echo $basedir
    pushd $basedir
    find . -type f |grep -E -v '^.+Season [[:digit:]]{2}.+ - S[[:digit:]]{2}E[[:digit:]]{2}.+$' |sed 's/).*/)/' |sort |uniq >> $MOVIES.dup
    find . -type d |grep -E    'Season [[:digit:]]{2}$' | sed 's!/Season [0-9][0-9]!!' |sort |uniq >> $SERIES.dup
    popd
done

sed 's!.*/!!' $MOVIES.dup | sort | uniq > $MOVIES
sed 's!.*/!!' $SERIES.dup | sort | uniq > $SERIES


cat <<EOF > $TEX
\documentclass[twocolumn]{article}
\usepackage{enumitem,amssymb}
\usepackage[a4paper,margin=1cm,nohead,foot=0.5cm]{geometry}
\pagestyle{plain}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

\newlist{todolist}{itemize}{2}
\setlist[todolist]{label=$\square$}
\usepackage{pifont}
\newcommand{\cmark}{\ding{51}}%
\newcommand{\xmark}{\ding{55}}%
\newcommand{\done}{\rlap{$\square$}{\raisebox{2pt}{\large\hspace{1pt}\cmark}}%
\hspace{-2.5pt}}
\newcommand{\wontfix}{\rlap{$\square$}{\large\hspace{1pt}\xmark}}

\title{Filmer}
\begin{document}
\maketitle

EOF
#\item[\done] Frame the problem
#\item Write solution
#\item[\wontfix] profit

echo "\\subsection{Movies}" >> $TEX
echo "\\begin{todolist}" >> $TEX

sed 's/^/\\item /' $MOVIES >> $TEX
echo "\\end{todolist}" >> $TEX


echo "\\subsection{Series}" >> $TEX
echo "\\begin{todolist}" >> $TEX

sed 's/^/\\item /' $SERIES >> $TEX
echo "\\end{todolist}" >> $TEX

cat <<EOF >> $TEX
\end{document}
EOF


#echo "Done  $TEX DVI PDF"
latex -output-format=pdf -output-directory=/tmp $TEX
