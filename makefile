.PHONY: all clean

# name of the PDF to create
pdf = ../RodneyFavoriteRecipes.pdf

# name of the rst file to build
input_rst_file = RodneyFavoriteRecipes.rst

# calculate the name of the build temp files
build_temp_file = $(input_rst_file:%.rst=%.rst.build_temp)
TEMP_SUBSTITUTION_FILE = temp_substitutions.rst
REVISION_NUMBER_FILE = revision-number.txt

# default target: build the PDF file if the rst file, a style file or an image changes
$(pdf): $(wildcard *.rst) $(wildcard Appendix/*.rst) $(wildcard Recipes/*.rst) $(wildcard *.style) RodneyFavoriteRecipes.style.json
	rm -fR *.build_temp
	rm -f $(TEMP_SUBSTITUTION_FILE)

	echo ".. |Date| replace:: $$(date +%B\ %d\,\ %Y)"  > $(TEMP_SUBSTITUTION_FILE)
	echo "  "  >> $(TEMP_SUBSTITUTION_FILE)

	if ! test -f $(REVISION_NUMBER_FILE); then echo 0 > $(REVISION_NUMBER_FILE); fi
	echo $$(($$(cat $(REVISION_NUMBER_FILE)) + 1)) > $(REVISION_NUMBER_FILE)

	echo ".. |Revision| replace:: $$(cat $(REVISION_NUMBER_FILE))"  >> $(TEMP_SUBSTITUTION_FILE)
	echo "  "  >> $(TEMP_SUBSTITUTION_FILE)

	rst2pdf $(input_rst_file) \
		-b1 \
		--section-header-depth=1 \
		--fit-background-mode=scale \
		--smart-quotes=0 \
		--fit-literal-mode=shrink \
		--repeat-table-rows \
		-s RodneyFavoriteRecipes.style \
		--output="$(pdf)" \
		--strip-elements-with-class=handout \
		-e preprocess \
	&& rm -fR *.build_temp \
	&& rm -f $(TEMP_SUBSTITUTION_FILE)

# make clean: deletes the pdf, keynote and build_temp files
clean:
	rm -f $(pdf)
	rm -fR *.build_temp
	rm -f $(TEMP_SUBSTITUTION_FILE)
