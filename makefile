.PHONY: all pdf html epub tidy commit clean

# name of the PDF to create
pdf = ../RodneyFavoriteRecipes.pdf
html = ../RodneyFavoriteRecipes.html
epub = ../RodneyFavoriteRecipes.epub

# name of the rst file to build
input_rst_file = RodneyFavoriteRecipes.rst

# calculate the name of the build temp files
build_temp_file = $(input_rst_file:%.rst=%.rst.build_temp)
TEMP_SUBSTITUTION_FILE = temp_substitutions.rst
REVISION_MAJOR_NUMBER_FILE = revision-number-major.txt
REVISION_MINOR_NUMBER_FILE = revision-number-minor.txt

# Checking Message File
CHECKIN_MSG_FILE = checkin_msg.temp

define generate_temp_sub
	@#if ! test -f $(REVISION_MAJOR_NUMBER_FILE); then echo 0 > $(REVISION_MAJOR_NUMBER_FILE); fi
	@# TODO: Figure out when to add generate the next major revision number
	@#	echo $$(($$(cat $(REVISION_MAJOR_NUMBER_FILE)) + 1)) > $(REVISION_MAJOR_NUMBER_FILE) \
	@#	 && echo 0 > $(REVISION_MINOR_NUMBER_FILE)
	@if ! test -f $(REVISION_MINOR_NUMBER_FILE); then echo 0 > $(REVISION_MINOR_NUMBER_FILE); fi
	@if ! test -f $(TEMP_SUBSTITUTION_FILE); then echo $$(($$(cat $(REVISION_MINOR_NUMBER_FILE)) + 1)) > $(REVISION_MINOR_NUMBER_FILE); fi
	@echo ".. |Date| replace:: $$(date +%B\ %d\,\ %Y)"  > $(TEMP_SUBSTITUTION_FILE)
	@echo "  "  >> $(TEMP_SUBSTITUTION_FILE)
	@echo ".. |Revision| replace:: $$(cat $(REVISION_MAJOR_NUMBER_FILE)).$$(cat $(REVISION_MINOR_NUMBER_FILE))" >> $(TEMP_SUBSTITUTION_FILE)
	@echo "  " >> $(TEMP_SUBSTITUTION_FILE)
endef

# default target: build the PDF file if the rst file, a style file
all:pdf html epub tidy commit

pdf: $(pdf)

html: $(pdf)

epub: $(epub)

$(pdf): $(wildcard *.rst) $(wildcard */?*.rst) $(wildcard *.style) $(wildcard *.style.json)
	@rm -fR *.build_temp
	$(call generate_temp_sub)
	@echo "Creating PDF..."
	@rst2pdf $(input_rst_file) \
		--break-level=1 \
		--section-header-depth=1 \
		--fit-background-mode=scale \
		--smart-quotes=0 \
		--fit-literal-mode=shrink \
		--repeat-table-rows \
		--stylesheets=Cookbook.style \
		--output="$(pdf)" \
		--strip-elements-with-class=handout \
		--extension-module=preprocess
	@rm -fR *.build_temp


$(html): $(wildcard *.rst) $(wildcard */?*.rst) $(wildcard *.css)
	$(call generate_temp_sub)
	@echo "Creating HTML..."
	@rst2html5 \
	     --stylesheet-inline=Cookbook.css \
			 --strip-elements-with-class=handout \
			 --strip-comments \
			 $(input_rst_file:%.rst=%.html.rst) \
			 "$(html)"

$(epub): $(html) RecipesCover.png
	$(call generate_temp_sub)
	@echo "Creating EPUB..."
	@ebook-convert "$(html)" "$(epub)" \
	     --title "Recipes From the Messy Chef" \
	     --authors "Rodney Shupe" \
	     --author-sort "Shupe Rodney" \
			 --language English \
			 --comments "A collection of recipes containing the favorites of Rodney Shupe and family." \
			 --tags Cookbook,Cooking,Recipes \
			 --cover RecipesCover.png \
			 --max-toc-links 29 \
			 --embed-all-fonts > /dev/null

tidy:
	@rm -fR *.build_temp
	@rm -f $(TEMP_SUBSTITUTION_FILE)

# make clean: deletes the pdf, keynote and build_temp files
commit:
	@echo "$(m)" > $(CHECKIN_MSG_FILE)
	@if [ "$(m)" = "" ]; then echo "Automatic commit of successful build $$(cat $(REVISION_MAJOR_NUMBER_FILE)).$$(cat $(REVISION_MINOR_NUMBER_FILE))" > $(CHECKIN_MSG_FILE); fi

	@git add --all
	@git commit --message="$$(cat $(CHECKIN_MSG_FILE))"
	@git push origin master
	@rm -f $(CHECKIN_MSG_FILE)

clean:
	@rm -f $(pdf)
	@rm -f $(html)
	@rm -f $(epub)
	@rm -fR *.build_temp
	@rm -f $(TEMP_SUBSTITUTION_FILE)
	@rm -f $(CHECKIN_MSG_FILE)
