.PHONY: all clean mrproper

all: report.pdf

clean:
	rm -f *.log *.aux *.toc *.out

mrproper: clean
	rm -f report.pdf

%.pdf: %.tex
	pdflatex $<
	pdflatex $<
