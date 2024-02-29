help:
	@echo ""
	@echo "Available make targets for radionets:"
	@echo ""
	@echo "  help         Print this help message (the default)"
	@echo "  clean        Remove temporary doc files"
	@echo "  docs         Generate Sphinx docs"
	@echo ""

docs:
	cd docs && $(MAKE) html SPHINXOPTS="-n --color"
	@echo "------------------------------------------------"
	@echo "Documentation is in: docs/_build/html/index.html"

clean:
	$(RM) -rf docs/_build docs/api
