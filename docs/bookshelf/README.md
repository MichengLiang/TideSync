# TideSync Bookshelf

This directory maintains the TideSync realtime omnimodal video-call experience specification.

## Books

- `books/08-realtime-omnimodal-call-experience-spec/book.adoc` is the main specification. It defines the experience object, constitutive conditions, user journeys, public projections, black-box assertions, governance boundaries, and conformance statements for realtime omnimodal AI video and voice calls.
- `books/07-structured-writing-conventions/book.adoc` records the structured writing conventions used by the main specification, including stable heading IDs, `role`, `rel`, additional fields, and cross-reference practices.

`catalog.adoc` is the bookshelf entry point. It should route readers by role, judgment question, and maintained book.

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

## Maintain Books

Each book lives in `books/<book-id>/` and exposes `book.adoc` as its entry file. Add a book to `catalog.adoc` only when it belongs to this bookshelf's maintained specification surface.

When removing a book, delete `books/<book-id>/`, remove every matching `xref:books/<book-id>/book.adoc[...]` entry from `catalog.adoc`, and run:

```bash
pnpm run check
```

The check command is the local contract for catalog entries, discovered books, cross-book anchors, and generated HTML resources.
