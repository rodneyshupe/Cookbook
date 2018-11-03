.PHONY: all clean

# name of the PDF to create
pdf = ../RodneyFavoriteRecipes.pdf

# name of the rst file to build
input_rst_file = RodneyFavoriteRecipes.rst

# calculate the name of the build temp files
build_temp_file = $(input_rst_file:%.rst=%.rst.build_temp)
TEMP_SUBSTITUTION_FILE = temp_substitutions.rst
REVISION_MAJOR_NUMBER_FILE = revision-number-major.txt
REVISION_MINOR_NUMBER_FILE = revision-number-minor.txt

#git:
#	if ! test -f $(REVISION_MAJOR_NUMBER_FILE); then echo 0 > $(REVISION_MAJOR_NUMBER_FILE); fi
#	echo $$(($$(cat $(REVISION_MAJOR_NUMBER_FILE)) + 1)) > $(REVISION_MAJOR_NUMBER_FILE)
#	echo 0 > $(REVISION_MINOR_NUMBER_FILE)

# default target: build the PDF file if the rst file, a style file or an image changes
$(pdf): $(wildcard *.rst) $(wildcard */?*.rst) $(wildcard *.style) RodneyFavoriteRecipes.style.json
	rm -fR *.build_temp
	rm -f $(TEMP_SUBSTITUTION_FILE)

	echo ".. |Date| replace:: $$(date +%B\ %d\,\ %Y)"  > $(TEMP_SUBSTITUTION_FILE)
	echo "  "  >> $(TEMP_SUBSTITUTION_FILE)

	if ! test -f $(REVISION_MINOR_NUMBER_FILE); then echo 0 > $(REVISION_MINOR_NUMBER_FILE); fi
	echo $$(($$(cat $(REVISION_MINOR_NUMBER_FILE)) + 1)) > $(REVISION_MINOR_NUMBER_FILE)

	echo ".. |Revision| replace:: $$(cat $(REVISION_MAJOR_NUMBER_FILE)).$$(cat $(REVISION_MINOR_NUMBER_FILE))" >> $(TEMP_SUBSTITUTION_FILE)
	echo "  " >> $(TEMP_SUBSTITUTION_FILE)

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

	git add --all
	git commit --message="Automatic commit of successful build $$(cat $(REVISION_MAJOR_NUMBER_FILE)).$$(cat $(REVISION_MINOR_NUMBER_FILE))"
	git push origin master

# make clean: deletes the pdf, keynote and build_temp files
clean:
	rm -f $(pdf)
	rm -fR *.build_temp
	rm -f $(TEMP_SUBSTITUTION_FILE)
