SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
MODULE        ?= science_lib

.PHONY: help apidoc html clean

help:
	@echo "Use 'make apidoc' to generate API stubs"
	@echo "Use 'make html' to build HTML documentation"

apidoc:
	sphinx-apidoc -f -o $(SOURCEDIR)/api ../src/$(MODULE)

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

clean:
	rm -rf $(BUILDDIR)
