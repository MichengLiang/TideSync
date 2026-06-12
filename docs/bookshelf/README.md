# My Books

This is an AsciiDoc multi-book workspace. It starts with sample books that show common ways to organize independent books, multipart books, technical books, reference material, split volumes, and structured writing conventions.

## Install

```bash
pnpm install
```

## Build

```bash
pnpm run build
```

Outputs:

- `build/html/index.html`
- `build/html/catalog.html`
- `build/html/books/<book-id>/book.html`
- `build/adoc/catalog.adoc`
- `build/adoc/books/<book-id>.adoc`

Diagram blocks render as Kroki image URLs by default, so normal builds do not depend on the Kroki service being available at build time.
To fetch diagram images into the local HTML output, run:

```bash
ADOC_BOOKS_FETCH_DIAGRAMS=1 pnpm run build
```

## Check

```bash
pnpm run check
```

This checks the current catalog, existing books, book doctypes, cross-book xrefs, anchors, and local HTML resources.

## Clean

```bash
pnpm run clean
```

This removes `build/`.

## Delete Sample Books

Delete `books/<book-id>/`, then remove the matching `xref:books/<book-id>/book.adoc[...]` entry from `catalog.adoc`. Each default sample is independent, so no other sample book needs to be edited.

Run:

```bash
pnpm run check
```

## Add A Book

Copy `books/01-starter-book` to `books/<your-book-id>`, edit `book.adoc` and chapter files, then add the new book to `catalog.adoc`.

To look at the original samples again, initialize a temporary workspace:

```bash
pnpm create asciidoc-multi-book-workspace sample-look
```
