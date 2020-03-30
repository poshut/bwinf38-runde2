rm examples.tex

for i in {1..9}; do
    echo "\\subsection{Ziffer $i}" >> examples.tex

    for j in 2019 2030 2080 2980; do
        echo "\\subsubsection{$j}" >> examples.tex
        if [ "$j" = 2019 ]; then
            echo "Der von meinem Programm gefundene Term hat genauso viele Ziffern wie das Beispiel aus der Aufgabenstellung:" >> examples.tex
        fi
        echo "\\begin{lstlisting}" >> examples.tex
        echo "\$ command time -f 'Zeit: %E' python main.py $j $i" >> examples.tex
        { command time -f "Zeit: %E" python main.py $j $i ; } >> examples.tex 2>&1
        echo "\\end{lstlisting}" >> examples.tex
    done
done