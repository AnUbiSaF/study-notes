# Unified TP26 study site source

This source builds the static site in the parent directory. Run from this directory:

```sh
python3 scripts/build_site.py --vault "/path/to/Учеба" --out ..
```

The build validates embedded note sections and image references before replacing the output. The subject list is in `scripts/subjects.json`; update it to exclude or include course folders intentionally. Machine learning is intentionally excluded from this test build.
