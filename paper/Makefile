# Build the paper. Regenerates every derived input first, so a stale card can
# never reach a compiled PDF.
#
#   make          -> main.pdf
#   make inputs   -> just the generated numbers, table and figures
#   make clean    -> remove build artifacts (keeps generated inputs)
#
# Builds with tectonic by default (see TEX below). Overleaf builds it unchanged
# too: upload the paper/ directory and set main.tex as root.

REPO  := ..
# tectonic fetches only the packages the document uses and needs no TeX Live
# install; `brew install tectonic`. Override for a conventional toolchain:
#   make TEXCMD="latexmk -pdf -interaction=nonstopmode -halt-on-error"
# NOT named TEX: make predefines that to `tex`, and ?= will not override a
# built-in, so the rule silently ran the wrong binary.
TEXCMD ?= tectonic -X compile
FIGS  := figs/fig1_state_space.pdf figs/fig2_scale.pdf figs/fig3_strength.pdf \
         figs/fig4_detector.pdf figs/fig5_persona.pdf
GEN   := numbers.tex table_main.tex table_stated.tex table_revealed.tex \
         appendix_prompts.tex $(FIGS)

.PHONY: all inputs slides lint clean distclean

all: main.pdf slides.pdf

main.pdf: main.tex refs.bib $(GEN)
	$(TEXCMD) main.tex

slides: slides.pdf

slides.pdf: slides.tex $(GEN)
	$(TEXCMD) slides.tex

inputs: $(GEN)

# Structural checks that need no TeX install: undefined macros, unbuilt
# figures, missing \input, citations with no bib entry.
lint: $(GEN)
	cd $(REPO) && python3 scripts/lint_paper.py

# One script emits all four, so they share one rule and one dependency list;
# splitting it would let make run paper_numbers.py four times in parallel and
# race on the same outputs.
numbers.tex table_main.tex table_stated.tex table_revealed.tex: \
		$(REPO)/card.json $(REPO)/site/persona_depth.json \
		$(REPO)/site/deception.json \
		$(REPO)/self_report_summary.json \
		$(REPO)/self_report_summary_personas.json
	cd $(REPO) && python3 scripts/paper_numbers.py

# The appendix renders prompts from the battery and answers from the result
# rows, so it depends on the battery and on the module that builds prompts.
# results/ is gitignored, which is why the generated .tex is committed.
appendix_prompts.tex: $(REPO)/battery/outcomes_3arm.json \
		$(REPO)/battery/self_report.json \
		$(REPO)/nullcard/runner/forced_choice.py \
		$(REPO)/modal_app/sweep.py
	cd $(REPO) && python3 scripts/appendix_prompts.py

figs/fig1_state_space.pdf figs/fig2_scale.pdf figs/fig3_strength.pdf: $(REPO)/card.json
	cd $(REPO) && python3 scripts/figures.py --out paper/figs --format pdf --themes light

figs/fig5_persona.pdf: $(REPO)/site/persona_depth.json
	cd $(REPO) && python3 scripts/persona_depth.py --out paper/figs --format pdf --themes light

# Was missing: fig4 ships in the paper but `make` never rebuilt it, so an edit to
# fig_detector.py or the detector JSON could not reach the PDF without a manual run.
figs/fig4_detector.pdf: $(REPO)/site/nonsense_detector.json $(REPO)/scripts/fig_detector.py
	cd $(REPO) && python3 scripts/fig_detector.py --out paper/figs --format pdf --themes light

clean:
	rm -f *.bbl *.blg *.aux *.log *.out *.nav *.snm *.toc *.xdv
	rm -f main.pdf slides.pdf

# Also drops the generated inputs. `make` regenerates them from the card.
distclean: clean
	rm -f $(GEN)
