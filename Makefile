PYTHON ?= python3
RELEASE_KIND := $(or $(BUMP),$(filter major minor patch,$(MAKECMDGOALS)))

.PHONY: release tag patch minor major

release:
	@test "$(words $(RELEASE_KIND))" -eq 1 || { echo "usage: make release [patch|minor|major]" >&2; exit 2; }
	@set -eu; release_tag="$$( $(PYTHON) tools/next_release_version.py $(RELEASE_KIND) )"; \
	$(PYTHON) tools/release_tag.py "$$release_tag"; \
	git push origin HEAD "refs/tags/$$release_tag"

tag:
	$(PYTHON) tools/release_tag.py "$(VERSION)"

patch minor major:
ifeq ($(filter release,$(MAKECMDGOALS)),)
	@$(MAKE) release BUMP=$@
else
	@:
endif

.PHONY: release-check
release-check:
	$(PYTHON) tools/check_release.py $(if $(VERSION),--version $(VERSION),)
