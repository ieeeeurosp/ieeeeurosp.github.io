###
### This Makefile is for making the website only!
###

GITHUB_PAGES_BRANCH=gh-pages
THEME = eurosp

MARKDOWN = python3 -m markdown
BASEDIR = .
SRCDIR = .
PAGEDIR = $(BASEDIR)/content/2022

posters: posters.py
	cd $(SRCDIR); python3 posters.py
	cat $(SRCDIR)/Papers.top $(SRCDIR)/posters.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/posters.md

html:
	cd $(SRCDIR); python3 process.py
##	cat $(SRCDIR)/papers.top $(SRCDIR)/sessions.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/sessions.md
##	cat $(SRCDIR)/papers.top $(SRCDIR)/fullsessions.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/fullsessions.md
	cat $(SRCDIR)/papers.top $(SRCDIR)/topics.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/topics.md
	cat $(SRCDIR)/papers.top $(SRCDIR)/fulltopics.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/fulltopics.md
#	cp $(SRCDIR)/session-??.md $(PAGEDIR)
	cp $(SRCDIR)/topic-?.md $(PAGEDIR)
	cp $(SRCDIR)/topic-??.md $(PAGEDIR)
	cat $(SRCDIR)/papers.top $(SRCDIR)/papers.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/papers.md
	cat $(SRCDIR)/papers.top $(SRCDIR)/openpapers.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/openpapers.md
	cat $(SRCDIR)/papers.top $(SRCDIR)/artifacts.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/artifacts.md
	cat $(SRCDIR)/papers.top $(SRCDIR)/authors.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/authors.md
	cat $(SRCDIR)/papers.top $(SRCDIR)/institutions.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/institutions.md
##	cat $(SRCDIR)/papers.top $(SRCDIR)/finalists.html $(SRCDIR)/papers.bottom > $(PAGEDIR)/finalists.md
	hugo --theme=$(THEME)

develop:
	make html
	hugo server --theme=$(THEME) --buildDrafts --watch

github: html
	cp -r public/* ../
	git add -A; git commit -m "Rebuilt site" ; git push

.PHONY: html clean develop
