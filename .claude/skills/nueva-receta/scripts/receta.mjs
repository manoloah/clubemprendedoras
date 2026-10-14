#!/usr/bin/env node
// Helpers for the nueva-receta skill. No dependencies.
//
//   node receta.mjs next                 next number, date, hub colour, current ?v= versions
//   node receta.mjs new <slug> [--from <slug>]   copy a receta folder as the starting point
//   node receta.mjs check <slug>         check the page, the hub card and recetas.json (exit 1 on errors)

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../..");
const SITE = path.join(ROOT, "site");
const RECETAS = path.join(SITE, "recetas");
const JSON_PATH = path.join(RECETAS, "recetas.json");
const HUB = path.join(RECETAS, "index.html");
const TEMPLATE = "reel-con-claude-cowork";
const COLORS = ["pink", "lilac", "butter"];
const DOMAIN = "https://www.clubdelasemprendedoras.com";

const read = (p) => fs.readFileSync(p, "utf8");
const recetas = () => JSON.parse(read(JSON_PATH)).recetas || [];
const pagePath = (slug) => path.join(RECETAS, slug, "index.html");

// Every receta folder (has an index.html), plus the hub and the landing.
function allPages() {
  const dirs = fs.readdirSync(RECETAS, { withFileTypes: true })
    .filter((d) => d.isDirectory() && fs.existsSync(pagePath(d.name)))
    .map((d) => pagePath(d.name));
  return [path.join(SITE, "index.html"), HUB, ...dirs];
}

// Highest ?v= of each shared asset across all pages: what a new page should load.
function currentVersions() {
  const v = {};
  for (const page of allPages()) {
    for (const [, file, n] of read(page).matchAll(/assets\/([\w-]+\.(?:css|js))\?v=(\d+)/g)) {
      v[file] = Math.max(v[file] || 0, Number(n));
    }
  }
  return v;
}

function nextWednesday(after) {
  const d = new Date(`${after}T12:00:00Z`);
  do d.setUTCDate(d.getUTCDate() + 1); while (d.getUTCDay() !== 3);
  return d.toISOString().slice(0, 10);
}

function hubColors() {
  return [...read(HUB).matchAll(/receta-feature--(pink|lilac|butter)/g)].map((m) => m[1]);
}

function next() {
  const list = recetas();
  const last = list.reduce((a, b) => ((a?.fecha || "") > b.fecha ? a : b), null);
  const today = new Date().toISOString().slice(0, 10);
  let fecha = nextWednesday(last ? last.fecha : today);
  while (fecha <= today) fecha = nextWednesday(fecha);
  const top = hubColors()[0];
  const color = COLORS[(COLORS.indexOf(top) + 1) % COLORS.length]; // pink → lilac → butter → pink
  console.log(JSON.stringify({
    numero: Math.max(0, ...list.map((t) => t.numero || 0)) + 1,
    fecha,
    hub_color: color,
    hub_top_color_now: top || null,
    newest: last ? { numero: last.numero, slug: last.slug, fecha: last.fecha } : null,
    versions: currentVersions(),
  }, null, 2));
}

function create(slug, from = TEMPLATE) {
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) die(`Slug must be lowercase words joined by hyphens: "${slug}"`);
  const dest = pagePath(slug);
  if (fs.existsSync(dest)) die(`${path.relative(ROOT, dest)} already exists.`);
  if (!fs.existsSync(pagePath(from))) die(`No receta "${from}" to copy from.`);
  const numero = Math.max(0, ...recetas().map((t) => t.numero || 0)) + 1;
  const versions = currentVersions();
  let html = read(pagePath(from))
    .replaceAll(`/recetas/${from}/`, `/recetas/${slug}/`)
    .replaceAll(`receta-${from}`, `receta-${slug}`)
    .replace(/Receta #\d+/, `Receta #${numero}`)
    .replace(/assets\/([\w-]+\.(?:css|js))\?v=\d+/g, (m, file) => (versions[file] ? `assets/${file}?v=${versions[file]}` : m));
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, html);
  console.log(`Created ${path.relative(ROOT, dest)} from ${from} (Receta #${numero}).`);
  console.log("Head URLs, data-gate and ?v= are set. Now rewrite the title, meta, hero, steps and closing.");
}

// ---------- check ----------

const errors = [];
const warnings = [];
const err = (m) => errors.push(m);
const warn = (m) => warnings.push(m);

// Visible copy only: drop scripts, styles, prompts and code, then tags.
function visibleText(html) {
  return html
    .replace(/<(script|style|pre|code)\b[\s\S]*?<\/\1>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ");
}

function checkPage(slug, entry) {
  const file = pagePath(slug);
  if (!fs.existsSync(file)) return err(`Missing ${path.relative(ROOT, file)}`);
  const html = read(file);
  const url = `${DOMAIN}/recetas/${slug}/`;

  // Head
  const title = html.match(/<title>([^<]*)<\/title>/)?.[1] || "";
  if (!title.endsWith("· Recetas del Club")) err(`<title> should end with "· Recetas del Club": "${title}"`);
  for (const [label, re] of [
    ["canonical", /<link rel="canonical" href="([^"]+)"/],
    ["og:url", /<meta property="og:url" content="([^"]+)"/],
  ]) {
    const got = html.match(re)?.[1];
    if (got !== url) err(`${label} is "${got}", expected "${url}"`);
  }
  for (const m of ["description", "og:title", "og:description"]) {
    const re = m.startsWith("og:") ? new RegExp(`property="${m}" content="([^"]*)"`) : new RegExp(`name="${m}" content="([^"]*)"`);
    const val = html.match(re)?.[1];
    if (!val) err(`Missing <meta ${m}>`);
  }
  if (!html.includes('classList.add("is-gated")') || !html.includes("club_receta_ok")) {
    err("The inline gate script in <head> is missing or changed.");
  }

  // Versions
  const versions = currentVersions();
  for (const [, file2, n] of html.matchAll(/assets\/([\w-]+\.(?:css|js))\?v=(\d+)/g)) {
    if (Number(n) < versions[file2]) err(`${file2}?v=${n} is stale; the newest page loads ?v=${versions[file2]}`);
  }
  for (const needed of ["tokens.css", "styles.css", "config.js", "recetas.js", "motion.js"]) {
    if (!html.includes(`/assets/${needed}?v=`)) err(`Doesn't load /assets/${needed}?v=N`);
  }

  // Structure
  const kicker = html.match(/Receta #(\d+) · Gratis para el club/);
  if (!kicker) err('Hero kicker should read "Receta #N · Gratis para el club"');
  else if (entry && Number(kicker[1]) !== entry.numero) err(`Hero says Receta #${kicker[1]}, recetas.json says ${entry.numero}`);
  const h1 = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/)?.[1];
  if (!h1) err("No <h1> in the hero.");
  const iIngr = html.indexOf('class="ingredientes"');
  const iLocked = html.indexOf('class="receta__locked"');
  const iPaso1 = html.indexOf('id="paso-1"');
  const iGate = html.indexOf(`class="gate" data-gate="receta-${slug}"`);
  if (iIngr < 0) err('Missing the public "Lo que necesitas" block (.ingredientes).');
  if (iLocked < 0) err("Missing .receta__locked (the gated steps).");
  if (iPaso1 < 0) err('The first step must have id="paso-1" (the page scrolls there after unlocking).');
  if (iGate < 0) err(`Missing <div class="gate" data-gate="receta-${slug}">`);
  if (iIngr > iLocked && iLocked >= 0) err('"Lo que necesitas" must come before the locked steps (it is the public teaser).');
  if (iLocked >= 0 && iPaso1 >= 0 && iPaso1 < iLocked) err('id="paso-1" must be inside .receta__locked.');
  if (iGate >= 0 && iPaso1 > iGate) err("The steps must come before the gate card.");
  const pasos = [...html.matchAll(/<li class="paso" id="paso-(\d+)"/g)].map((m) => Number(m[1]));
  pasos.forEach((n, i) => { if (n !== i + 1) err(`Steps should be numbered paso-1…paso-N in order; found paso-${n} at position ${i + 1}`); });
  const nums = [...html.matchAll(/<span class="paso__num"[^>]*>(\d+)<\/span>/g)].map((m) => Number(m[1]));
  if (nums.join() !== pasos.join()) err(`.paso__num labels (${nums.join(",")}) don't match the step ids (${pasos.join(",")}).`);
  if (pasos.length > 5) warn(`${pasos.length} steps: the hub promises "cinco pasos o menos".`);
  if (!html.includes('class="receta-done"')) warn('No closing ".receta-done" block ("¿Lo hiciste?").');

  // Ids and copy buttons
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
  const dup = ids.filter((id, i) => ids.indexOf(id) !== i);
  if (dup.length) err(`Duplicate ids: ${[...new Set(dup)].join(", ")}`);
  for (const [, target] of html.matchAll(/data-copy="([^"]+)"/g)) {
    if (!new RegExp(`<pre id="${target}"`).test(html)) err(`Copy button points at "${target}" but there's no <pre id="${target}">`);
  }

  // Local files
  for (const [, ref] of html.matchAll(/(?:src|href)="(\/assets\/[^"?#]+)/g)) {
    if (!fs.existsSync(path.join(SITE, ref))) err(`Missing file ${ref}`);
  }
  for (const [, ref] of html.matchAll(/src="(\/assets\/img\/[^"]+)"/g)) {
    if (!/\.(webp|svg)$/.test(ref)) warn(`${ref}: images should be WebP.`);
  }
  for (const [tag] of html.matchAll(/<a\b[^>]*href="https?:[^"]*"[^>]*>/g)) {
    if (tag.includes(DOMAIN)) continue;
    if (!tag.includes('target="_blank"') || !tag.includes('rel="noopener"')) warn(`External link without target="_blank" rel="noopener": ${tag}`);
  }

  // Template leftovers
  if (slug !== TEMPLATE && fs.existsSync(pagePath(TEMPLATE))) {
    const tpl = read(pagePath(TEMPLATE));
    for (const re of [/<title>[^<]*<\/title>/, /<h1[^>]*>[\s\S]*?<\/h1>/, /<meta name="description" content="[^"]*"/]) {
      const mine = html.match(re)?.[0];
      if (mine && mine === tpl.match(re)?.[0]) err(`Same as the template (${TEMPLATE}): ${mine.slice(0, 80)}…`);
    }
    const text = visibleText(html);
    for (const leftover of ["les tengo una noticia", "Remotion", "Mi reel", "Mándanos tu reel"]) {
      if (text.includes(leftover)) warn(`Still has "${leftover}" from the template. Intended?`);
    }
  }

  lintCopy(visibleText(html), `recetas/${slug}`);
}

function lintCopy(text, where) {
  const banned = [
    [/\bingredientes?\b/i, "kitchen pun (use \"Lo que necesitas\")"],
    [/\bhorne(ar|a|amos|ado)\b|\bal horno\b/i, "kitchen pun"],
    [/\bprobadit/i, "kitchen pun"],
    [/\bcocin(a|ar|amos|ado)\b|\bchef\b|\bsazón\b/i, "kitchen pun"],
    [/\btutorial(es)?\b/i, "call it a receta"],
    [/\bhazte rica\b|\bdinero fácil\b|\béxito garantizado\b/i, "hype"],
  ];
  for (const [re, why] of banned) {
    const m = text.match(re);
    if (m) err(`${where}: "${m[0]}" (${why})`);
  }
  const jargon = text.match(/\b(API|backend|frontend|deploy|stack|framework|repo|CLI|SDK)\b/g);
  if (jargon) warn(`${where}: jargon ${[...new Set(jargon)].join(", ")}: explain it in one line or drop it.`);
  if (/\bcurso\b/i.test(text)) warn(`${where}: "curso": what we offer is a taller.`);
  const bangs = (text.match(/¡/g) || []).length;
  if (bangs > 2) warn(`${where}: ${bangs} "¡". At most one per screen.`);
  if (/!!|¡¡/.test(text)) err(`${where}: doubled exclamation marks.`);
  if (/—/.test(text)) warn(`${where}: em dash (—). The site's copy uses commas, colons or periods.`);
}

function checkHub(slug, entry) {
  const html = read(HUB);
  const list = html.match(/<ul class="receta-list">([\s\S]*?)<\/ul>/)?.[1] || "";
  const cards = [...list.matchAll(/<a class="receta-feature receta-feature--(\w+)" href="([^"]+)"/g)].map((m) => ({ color: m[1], href: m[2] }));
  const i = cards.findIndex((c) => c.href === `/recetas/${slug}/`);
  if (i < 0) return err(`Hub: no card links to /recetas/${slug}/`);
  if (i !== 0) err(`Hub: the card for ${slug} should be the first in .receta-list (newest first); it's #${i + 1}.`);
  cards.forEach((c, k) => {
    if (k && c.color === cards[k - 1].color) err(`Hub: cards ${k} and ${k + 1} are both ${c.color}; alternate pink/lilac/butter.`);
  });
  const block = list.split(/<li>/).find((b) => b.includes(`href="/recetas/${slug}/"`)) || "";
  if (!block.includes("receta-cover__screen")) err("Hub: the card has no .receta-cover phone cover.");
  for (const [, ref] of block.matchAll(/src="(\/assets\/[^"]+)"/g)) {
    if (!fs.existsSync(path.join(SITE, ref))) err(`Hub: missing file ${ref}`);
  }
  if (entry) {
    if (!new RegExp(`Receta #${entry.numero} · \\d+ pasos?`).test(block)) err(`Hub: kicker should read "Receta #${entry.numero} · N pasos".`);
    const pasos = [...read(pagePath(slug)).matchAll(/<li class="paso" id="paso-\d+"/g)].length;
    const said = block.match(/Receta #\d+ · (\d+) pasos?/)?.[1];
    if (said && Number(said) !== pasos) err(`Hub says ${said} pasos, the page has ${pasos}.`);
    const max = Math.max(...recetas().map((t) => t.numero));
    const note = html.match(/La receta #(\d+) llega/)?.[1];
    if (Number(note) !== max + 1) err(`Hub note says "La receta #${note} llega…"; it should be #${max + 1}.`);
  }
  lintCopy(visibleText(block), "hub card");
}

function checkJson(slug) {
  let list;
  try { list = recetas(); } catch (e) { err(`recetas.json is not valid JSON: ${e.message}`); return null; }
  const entry = list.find((t) => t.slug === slug);
  if (!entry) { err(`recetas.json has no entry with slug "${slug}"`); return null; }
  for (const k of ["numero", "slug", "titulo", "resumen", "fecha", "url"]) if (!entry[k]) err(`recetas.json: "${k}" is empty`);
  if (entry.url !== `/recetas/${slug}/`) err(`recetas.json: url should be "/recetas/${slug}/", is "${entry.url}"`);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(entry.fecha || "")) err(`recetas.json: fecha must be YYYY-MM-DD`);
  else if (new Date(`${entry.fecha}T12:00:00Z`).getUTCDay() !== 3) warn(`recetas.json: fecha ${entry.fecha} isn't a Wednesday.`);
  const numeros = list.map((t) => t.numero);
  if (new Set(numeros).size !== numeros.length) err("recetas.json: two entries share a numero.");
  if (list[list.length - 1] !== entry) warn("recetas.json: append new recetas at the end (newest last).");
  if (list.some((t) => t !== entry && t.fecha >= entry.fecha)) warn(`recetas.json: another receta has a fecha on or after ${entry.fecha}; the newsletter picks the newest unsent one.`);
  const page = fs.existsSync(pagePath(slug)) ? read(pagePath(slug)) : "";
  const h1 = visibleText(page.match(/<h1[^>]*>([\s\S]*?)<\/h1>/)?.[1] || "").trim();
  if (h1 && h1 !== entry.titulo) warn(`recetas.json titulo differs from the page's h1:\n    json: ${entry.titulo}\n    h1:   ${h1}`);
  lintCopy(`${entry.titulo} ${entry.resumen}`, "recetas.json");
  return entry;
}

function check(slug) {
  const entry = checkJson(slug);
  checkPage(slug, entry);
  checkHub(slug, entry);
  // Every other page must load the same shared versions too.
  const versions = currentVersions();
  for (const page of allPages()) {
    if (page === pagePath(slug)) continue;
    for (const [, file, n] of read(page).matchAll(/assets\/([\w-]+\.(?:css|js))\?v=(\d+)/g)) {
      if (Number(n) < versions[file]) warn(`${path.relative(ROOT, page)} loads ${file}?v=${n}; newest is ${versions[file]}.`);
    }
  }
  for (const w of warnings) console.log(`warn  ${w}`);
  for (const e of errors) console.log(`ERROR ${e}`);
  console.log(errors.length ? `\n${errors.length} error(s), ${warnings.length} warning(s).` : `\nOK (${warnings.length} warning(s)).`);
  process.exit(errors.length ? 1 : 0);
}

function die(msg) { console.error(msg); process.exit(1); }

const [cmd, slug, ...rest] = process.argv.slice(2);
if (cmd === "next") next();
else if (cmd === "new" && slug) create(slug, rest[0] === "--from" ? rest[1] : undefined);
else if (cmd === "check" && slug) check(slug);
else die("Usage: receta.mjs next | new <slug> [--from <slug>] | check <slug>");
