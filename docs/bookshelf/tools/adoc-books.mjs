#!/usr/bin/env node
import { createRequire } from "node:module";
import { cp, mkdir, readdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
const require = createRequire(import.meta.url);
const DIAGRAM_BLOCK_PATTERN = /^\[(?:actdiag|blockdiag|bpmn|bytefield|c4plantuml|d2|dbml|ditaa|erd|excalidraw|graphviz|mermaid|nomnoml|nwdiag|packetdiag|pikchr|plantuml|rackdiag|seqdiag|svgbob|symbolator|umlet|vega|vegalite|wavedrom|structurizr|diagramsnet|wireviz)(?:,|\])/m;
const CATALOG_BOOK_XREF_PATTERN = /xref:books\/([^/\]]+)\/book\.adoc(?:#[^\[]+)?\[/g;
const XREF_PATTERN = /xref:([^\[#]+)(?:#([A-Za-z0-9_-]+))?\[/g;
const ANCHOR_PATTERN = /^\[#([A-Za-z0-9_-]+)(?:[.,][^\]]*)?\]$/gm;
const LOCAL_TARGET_PATTERN = /\b(?:href|src)="([^"]+)"/g;
const SCHEME_PATTERN = /^[a-zA-Z][a-zA-Z0-9+.-]*:/;
const HOME_MARKER = "data-multi-book-home";
const CONTROLS_MARKER = "data-multi-book-controls";
const FETCH_DIAGRAMS_ENV = "ADOC_BOOKS_FETCH_DIAGRAMS";
const CONFIG_FILE = "adoc-books.config.mjs";
const DEFAULT_CONFIG = {
    rootIndex: {
        redirectTo: "catalog.html",
        title: "AsciiDoc Multi-Book Workspace"
    },
    homeLink: {
        label: "Back to catalog",
        subtitle: "AsciiDoc multi-book workspace"
    }
};
function objectValue(value) {
    return typeof value === "object" && value !== null ? value : {};
}
function stringValue(value, fallback) {
    return typeof value === "string" && value.trim() !== "" ? value : fallback;
}
async function loadRuntimeConfig(rootDir) {
    const configPath = path.join(rootDir, CONFIG_FILE);
    if (!await existsFile(configPath))
        return DEFAULT_CONFIG;
    const configUrl = pathToFileURL(configPath);
    configUrl.search = `mtime=${(await stat(configPath)).mtimeMs}`;
    const module = await import(configUrl.href);
    const rawConfig = objectValue(module.default ?? module);
    const rawRootIndex = objectValue(rawConfig.rootIndex);
    const rawHomeLink = objectValue(rawConfig.homeLink);
    return {
        rootIndex: {
            redirectTo: stringValue(rawRootIndex.redirectTo, DEFAULT_CONFIG.rootIndex.redirectTo),
            title: stringValue(rawRootIndex.title, DEFAULT_CONFIG.rootIndex.title)
        },
        homeLink: {
            label: stringValue(rawHomeLink.label, DEFAULT_CONFIG.homeLink.label),
            subtitle: stringValue(rawHomeLink.subtitle, DEFAULT_CONFIG.homeLink.subtitle)
        }
    };
}
async function existsFile(filePath) {
    try {
        const stats = await stat(filePath);
        return stats.isFile();
    }
    catch {
        return false;
    }
}
async function existsDir(dir) {
    try {
        const stats = await stat(dir);
        return stats.isDirectory();
    }
    catch {
        return false;
    }
}
async function collectFiles(dir, predicate) {
    const entries = await readdir(dir, { withFileTypes: true });
    const files = [];
    for (const entry of entries) {
        const entryPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            files.push(...await collectFiles(entryPath, predicate));
        }
        else if (entry.isFile() && predicate(entryPath)) {
            files.push(entryPath);
        }
    }
    return files.sort();
}
async function discoverBooks(rootDir) {
    const booksDir = path.join(rootDir, "books");
    const entries = await readdir(booksDir, { withFileTypes: true });
    const books = [];
    for (const entry of entries) {
        if (!entry.isDirectory())
            continue;
        const bookDir = path.join(booksDir, entry.name);
        const input = path.join(bookDir, "book.adoc");
        if (await existsFile(input)) {
            books.push({
                bookId: entry.name,
                bookDir,
                input,
                htmlOutputDir: path.join(rootDir, "build", "html", "books", entry.name)
            });
        }
    }
    return books.sort((a, b) => a.bookId.localeCompare(b.bookId));
}
async function readIfExists(filePath) {
    return await existsFile(filePath) ? readFile(filePath, "utf8") : "";
}
async function combinedBookSource(bookDir) {
    const files = await collectFiles(bookDir, (filePath) => filePath.endsWith(".adoc"));
    const sources = [];
    for (const file of files)
        sources.push(await readFile(file, "utf8"));
    return sources.join("\n");
}
async function workspaceUsesDiagrams(rootDir, books) {
    const sources = [await readIfExists(path.join(rootDir, "catalog.adoc"))];
    for (const book of books)
        sources.push(await combinedBookSource(book.bookDir));
    return sources.some((source) => DIAGRAM_BLOCK_PATTERN.test(source));
}
function createAsciidoctor(loadKroki) {
    const asciidoctor = require("asciidoctor")();
    require("@asciidoctor/reducer").register();
    if (loadKroki) {
        try {
            require("asciidoctor-kroki").register(asciidoctor.Extensions);
        }
        catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            throw new Error(`current workspace contains diagram blocks, but asciidoctor-kroki could not be loaded: ${message}`);
        }
    }
    return asciidoctor;
}
function shouldFetchDiagrams() {
    const value = process.env[FETCH_DIAGRAMS_ENV];
    return value === "1" || value === "true";
}
function reduceAdocSource(asciidoctor, input) {
    const doc = asciidoctor.loadFile(input, { safe: "unsafe" });
    const source = doc.getSource();
    if (/^[ \t]*include::/m.test(source)) {
        throw new Error(`reducer left unresolved include directives in ${input}`);
    }
    return source;
}
async function buildReducedAdoc(rootDir, books, asciidoctor) {
    const adocDir = path.join(rootDir, "build", "adoc");
    await rm(adocDir, { force: true, recursive: true });
    await mkdir(path.join(adocDir, "books"), { recursive: true });
    const catalogSource = reduceAdocSource(asciidoctor, path.join(rootDir, "catalog.adoc"));
    await writeFile(path.join(adocDir, "catalog.adoc"), catalogSource, "utf8");
    for (const book of books) {
        const source = reduceAdocSource(asciidoctor, book.input);
        await writeFile(path.join(adocDir, "books", `${book.bookId}.adoc`), source, "utf8");
    }
}
async function pruneStaleBookHtmlDirs(rootDir, books) {
    const htmlBooksDir = path.join(rootDir, "build", "html", "books");
    if (!await existsDir(htmlBooksDir))
        return;
    const current = new Set(books.map((book) => book.bookId));
    const entries = await readdir(htmlBooksDir, { withFileTypes: true });
    for (const entry of entries) {
        if (entry.isDirectory() && !current.has(entry.name)) {
            await rm(path.join(htmlBooksDir, entry.name), { force: true, recursive: true });
        }
    }
}
function convertFile(asciidoctor, input, outputFile, baseDir, attributes = {}) {
    asciidoctor.convertFile(input, {
        safe: "unsafe",
        base_dir: baseDir,
        to_file: outputFile,
        mkdirs: true,
        attributes
    });
}
async function buildHtml(rootDir, books, asciidoctor, useKroki, fetchDiagrams) {
    await mkdir(path.join(rootDir, "build", "html"), { recursive: true });
    convertFile(asciidoctor, path.join(rootDir, "catalog.adoc"), path.join(rootDir, "build", "html", "catalog.html"), rootDir);
    await pruneStaleBookHtmlDirs(rootDir, books);
    for (const book of books) {
        await mkdir(book.htmlOutputDir, { recursive: true });
        convertFile(asciidoctor, book.input, path.join(book.htmlOutputDir, "book.html"), book.bookDir, {
            ...(useKroki && fetchDiagrams ? { "kroki-fetch-diagram": "", "kroki-http-method": "post" } : {})
        });
    }
}
async function copyAssets(rootDir, books) {
    const sharedImages = path.join(rootDir, "shared", "images");
    if (await existsDir(sharedImages)) {
        await rm(path.join(rootDir, "build", "html", "shared", "images"), { force: true, recursive: true });
        await cp(sharedImages, path.join(rootDir, "build", "html", "shared", "images"), { recursive: true });
    }
    for (const book of books) {
        const assetsDir = path.join(book.bookDir, "assets");
        if (await existsDir(assetsDir)) {
            await rm(path.join(book.htmlOutputDir, "assets"), { force: true, recursive: true });
            await cp(assetsDir, path.join(book.htmlOutputDir, "assets"), { recursive: true });
        }
    }
}
function escapeHtmlAttribute(value) {
    return value
        .replaceAll("&", "&amp;")
        .replaceAll('"', "&quot;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
}
function escapeJsonScript(value) {
    return JSON.stringify(value)
        .replaceAll("<", "\\u003c")
        .replaceAll("\u2028", "\\u2028")
        .replaceAll("\u2029", "\\u2029");
}
function addBookControlsToBookHtml(html, href, homeLink, bookSource) {
    if (html.includes(CONTROLS_MARKER))
        return html;
    const marker = '<div id="toc" class="toc2">';
    const index = html.indexOf(marker);
    if (index === -1)
        throw new Error("book HTML is missing the left TOC container");
    const insertAt = index + marker.length;
    const controlsBlock = `
<style>
.multi-book-controls {
  margin: 0 0 1rem;
  padding-bottom: .75rem;
  border-bottom: 1px solid #e5e7eb;
}
.multi-book-home {
  color: #1f2937;
  display: block;
  font-weight: 600;
  line-height: 1.35;
  text-decoration: none;
}
.multi-book-home:hover {
  color: #0f766e;
  text-decoration: underline;
}
.multi-book-home span {
  color: #64748b;
  display: block;
  font-size: .78rem;
  font-weight: 400;
  margin-top: .15rem;
}
.multi-book-copy-source {
  appearance: none;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  color: #1f2937;
  cursor: pointer;
  display: block;
  font-size: .82rem;
  font-weight: 600;
  line-height: 1.2;
  margin-top: .75rem;
  padding: .42rem .5rem;
  text-align: center;
  width: 100%;
}
.multi-book-copy-source:hover,
.multi-book-copy-source:focus {
  border-color: #0f766e;
  color: #0f766e;
}
.multi-book-copy-status {
  color: #64748b;
  display: block;
  font-size: .75rem;
  line-height: 1.35;
  margin-top: .4rem;
  min-height: 1em;
}
</style>
<div class="multi-book-controls" ${CONTROLS_MARKER}>
  <a class="multi-book-home" ${HOME_MARKER} href="${escapeHtmlAttribute(href)}">${escapeHtmlAttribute(homeLink.label)}<span>${escapeHtmlAttribute(homeLink.subtitle)}</span></a>
  <button type="button" class="multi-book-copy-source" data-multi-book-source-copy>复制本书为纯文本</button>
  <span class="multi-book-copy-status" data-multi-book-source-status aria-live="polite"></span>
</div>
<script type="application/json" id="multi-book-source-data">${escapeJsonScript(bookSource)}</script>
<script>
(function () {
  var sourceElement = document.getElementById("multi-book-source-data");
  var button = document.querySelector("[data-multi-book-source-copy]");
  var status = document.querySelector("[data-multi-book-source-status]");
  if (!sourceElement || !button) return;

  var source = "";
  var fallbackMode = false;
  try {
    source = JSON.parse(sourceElement.textContent || '""');
  } catch (error) {
    if (status) status.textContent = "纯文本数据读取失败";
    button.disabled = true;
    return;
  }

  function setStatus(message) {
    if (status) status.textContent = message;
  }

  function openSourcePage() {
    var blob = new Blob([source], { type: "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    window.open(url, "_blank", "noopener");
    setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
    setStatus("已尝试打开纯文本页；如果没有出现，请允许弹出窗口后再试");
  }

  button.addEventListener("click", async function () {
    if (fallbackMode) {
      openSourcePage();
      return;
    }

    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(source);
      button.textContent = "已复制";
      setStatus("");
      setTimeout(function () { button.textContent = "复制本书为纯文本"; }, 1800);
    } catch (error) {
      fallbackMode = true;
      button.textContent = "打开纯文本页";
      openSourcePage();
    }
  });
}());
</script>`;
    return `${html.slice(0, insertAt)}${controlsBlock}${html.slice(insertAt)}`;
}
async function addHomeLinks(rootDir, books, homeLink) {
    const catalog = path.join(rootDir, "build", "html", "catalog.html");
    for (const book of books) {
        const htmlFile = path.join(book.htmlOutputDir, "book.html");
        const html = await readFile(htmlFile, "utf8");
        const href = path.relative(path.dirname(htmlFile), catalog);
        const source = await readFile(path.join(rootDir, "build", "adoc", "books", `${book.bookId}.adoc`), "utf8");
        await writeFile(htmlFile, addBookControlsToBookHtml(html, href, homeLink, source), "utf8");
    }
}
async function writeRootIndex(rootDir, rootIndex) {
    const outputDir = path.join(rootDir, "build", "html");
    await mkdir(outputDir, { recursive: true });
    const redirectTo = rootIndex.redirectTo;
    await writeFile(path.join(outputDir, "index.html"), `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=${escapeHtmlAttribute(redirectTo)}">
  <title>${escapeHtmlAttribute(rootIndex.title)}</title>
</head>
<body>
  <p><a href="${escapeHtmlAttribute(redirectTo)}">${escapeHtmlAttribute(redirectTo)}</a></p>
</body>
</html>
`, "utf8");
}
function extractCatalogBookIds(catalogSource) {
    const ids = new Set();
    for (const match of catalogSource.matchAll(CATALOG_BOOK_XREF_PATTERN))
        ids.add(match[1]);
    return [...ids].sort((a, b) => a.localeCompare(b));
}
function explicitAnchors(source) {
    const anchors = new Set();
    for (const match of source.matchAll(ANCHOR_PATTERN))
        anchors.add(match[1]);
    return anchors;
}
function attributesFromBookSource(bookSource) {
    const attributes = new Map();
    for (const line of bookSource.split(/\r?\n/)) {
        const match = line.match(/^:([A-Za-z0-9_-]+):\s+(.+)$/);
        if (match)
            attributes.set(match[1], match[2]);
    }
    return attributes;
}
function expandXrefTarget(target, attributes) {
    return target.replaceAll(/\{([A-Za-z0-9_-]+)\}/g, (_, name) => attributes.get(name) ?? `{${name}}`);
}
function issue(code, detail) {
    return { code, detail };
}
async function workspaceContractIssues(rootDir, books) {
    const issues = [];
    const catalogSource = await readIfExists(path.join(rootDir, "catalog.adoc"));
    const catalogBookIds = extractCatalogBookIds(catalogSource);
    const bookSet = new Set(books.map((book) => book.bookId));
    const catalogBookSet = new Set(catalogBookIds);
    for (const bookId of catalogBookIds) {
        if (!bookSet.has(bookId))
            issues.push(issue("CATALOG_TARGET_MISSING", bookId));
    }
    for (const book of books) {
        if (!catalogBookSet.has(book.bookId))
            issues.push(issue("BOOK_MISSING_FROM_CATALOG", book.bookId));
    }
    for (const book of books) {
        const bookSource = await readFile(book.input, "utf8");
        const allSource = await combinedBookSource(book.bookDir);
        const attributes = attributesFromBookSource(bookSource);
        if (!/^:doctype:\s+book$/m.test(bookSource))
            issues.push(issue("MISSING_DOCTYPE", book.bookId));
        for (const match of allSource.matchAll(XREF_PATTERN)) {
            const [, target, anchor] = match;
            if (/^https?:/.test(target))
                continue;
            const expandedTarget = expandXrefTarget(target, attributes);
            if (!expandedTarget.endsWith(".adoc"))
                continue;
            const resolved = path.resolve(book.bookDir, expandedTarget);
            if (!await existsFile(resolved)) {
                issues.push(issue("XREF_TARGET_MISSING", `${book.bookId} -> ${expandedTarget}`));
                if (anchor)
                    issues.push(issue("MISSING_ANCHOR", `${book.bookId} -> ${expandedTarget}#${anchor}`));
                continue;
            }
            if (anchor) {
                const targetSource = await combinedBookSource(path.dirname(resolved));
                if (!explicitAnchors(targetSource).has(anchor)) {
                    issues.push(issue("MISSING_ANCHOR", `${book.bookId} -> ${expandedTarget}#${anchor}`));
                }
            }
        }
    }
    return issues;
}
async function collectHtmlFiles(dir) {
    return collectFiles(dir, (filePath) => filePath.endsWith(".html"));
}
function extractLocalTargets(html) {
    const targets = [];
    for (const match of html.matchAll(LOCAL_TARGET_PATTERN)) {
        const rawTarget = match[1];
        if (rawTarget === "" || rawTarget.startsWith("#") || rawTarget.startsWith("//") || SCHEME_PATTERN.test(rawTarget)) {
            continue;
        }
        const targetWithoutFragment = rawTarget.split("#", 1)[0].split("?", 1)[0];
        if (targetWithoutFragment !== "")
            targets.push(rawTarget);
    }
    return targets;
}
async function missingLocalResources(rootDir) {
    const htmlDir = path.join(rootDir, "build", "html");
    const htmlFiles = await collectHtmlFiles(htmlDir);
    const issues = [];
    for (const htmlFile of htmlFiles) {
        const html = await readFile(htmlFile, "utf8");
        for (const target of extractLocalTargets(html)) {
            const targetPath = target.split("#", 1)[0].split("?", 1)[0];
            const resolved = path.resolve(path.dirname(htmlFile), targetPath);
            if (!await existsFile(resolved)) {
                issues.push(issue("HTML_RESOURCE_MISSING", `${path.relative(htmlDir, htmlFile)} -> ${target}`));
            }
        }
    }
    return issues;
}
async function assertNoIssues(label, issues) {
    if (issues.length === 0)
        return;
    for (const entry of issues)
        console.error(`${entry.code}: ${entry.detail}`);
    throw new Error(`${label} failed with ${issues.length} issue(s)`);
}
export async function buildWorkspace(rootDir = process.cwd()) {
    const catalog = path.join(rootDir, "catalog.adoc");
    if (!await existsFile(catalog))
        throw new Error(`missing catalog.adoc in ${rootDir}`);
    const books = await discoverBooks(rootDir);
    if (books.length === 0)
        throw new Error(`missing book.adoc entries in ${path.join(rootDir, "books")}`);
    const config = await loadRuntimeConfig(rootDir);
    const useKroki = await workspaceUsesDiagrams(rootDir, books);
    const fetchDiagrams = shouldFetchDiagrams();
    const asciidoctor = createAsciidoctor(useKroki);
    await buildReducedAdoc(rootDir, books, asciidoctor);
    await buildHtml(rootDir, books, asciidoctor, useKroki, fetchDiagrams);
    await copyAssets(rootDir, books);
    await addHomeLinks(rootDir, books, config.homeLink);
    await writeRootIndex(rootDir, config.rootIndex);
    await assertNoIssues("HTML local resource check", await missingLocalResources(rootDir));
    await assertNoIssues("workspace contract check", await workspaceContractIssues(rootDir, books));
}
export async function checkWorkspace(rootDir = process.cwd()) {
    await buildWorkspace(rootDir);
}
export async function cleanWorkspace(rootDir = process.cwd()) {
    await rm(path.join(rootDir, "build"), { force: true, recursive: true });
}
async function main() {
    const command = process.argv[2];
    if (command === "build") {
        await buildWorkspace();
        return;
    }
    if (command === "check") {
        await checkWorkspace();
        return;
    }
    if (command === "clean") {
        await cleanWorkspace();
        return;
    }
    console.error("Usage: node tools/adoc-books.mjs <build|check|clean>");
    process.exitCode = 1;
}
const executedPath = process.argv[1] ? path.resolve(process.argv[1]) : "";
const modulePath = fileURLToPath(import.meta.url);
if (executedPath === modulePath) {
    main().catch((error) => {
        console.error(error instanceof Error ? error.message : error);
        process.exitCode = 1;
    });
}
