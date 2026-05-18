LATEX=pdflatex
TARGETS=notes.pdf presentation.pdf

all: $(TARGETS)

%.pdf: %.tex
	$(LATEX) -interaction=nonstopmode -halt-on-error $<
	$(LATEX) -interaction=nonstopmode -halt-on-error $<

clean:
	rm -f *.aux *.log *.out *.toc *.nav *.snm *.vrb
