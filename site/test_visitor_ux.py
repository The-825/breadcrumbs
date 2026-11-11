"""Visitor UX checks for the Breadcrumbs site: story, navigation, routes, filters.

Behavior tests run the real workflows.js and prompts.js in a Node VM against a small
fake DOM and the real data files. They need `node` and are skipped without it. No test
here runs a browser; keyboard, layout and touch checks stay with the browser pass.
"""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

SITE = Path(__file__).resolve().parent
NAV = ["Home", "Start here", "Workflows", "Prompts", "Book and essays", "StaleToast", "The 825"]
CURRENT = {"index.html": "Home", "start.html": "Start here", "workflows.html": "Workflows",
           "prompts.html": "Prompts", "papers.html": "Book and essays"}
PRIMARY = ("index.html", "start.html", "papers.html", "jarvis.html", "workflows.html", "prompts.html")
BOOK = "https://the825.co/archivist-to-architect/"
HARNESS = r'''
const fs = require("fs"), vm = require("vm"), path = require("path");
const site = process.argv[1];
const read = f => fs.readFileSync(path.join(site, f), "utf8");
const data = n => JSON.parse(read("data/" + n + ".json"));

function makeDom(pageFile) {
  const html = read(pageFile);
  const els = {};
  const state = {focus: null};
  function make(sel) {
    if (!html.includes('id="' + sel.slice(1) + '"')) throw new Error("missing element " + sel);
    const tag = new RegExp('<[^>]*id="' + sel.slice(1) + '"[^>]*>').exec(html)[0];
    const el = {
      sel, value: "", hidden: /\shidden[\s>]/.test(tag), textContent: "", _html: "", listeners: {},
      addEventListener(t, f) { (this.listeners[t] = this.listeners[t] || []).push(f); },
      focus() { state.focus = sel; }, scrollIntoView() {},
      get innerHTML() { return this._html; }, set innerHTML(v) { this._html = String(v); }
    };
    const select = new RegExp('<select id="' + sel.slice(1) + '">([\\s\\S]*?)</select>').exec(html);
    if (select) el._html = select[1];
    return el;
  }
  const get = sel => els[sel] || (els[sel] = make(sel));
  const fire = (sel, type) => { for (const f of (get(sel).listeners[type] || [])) f({}); };
  return {get, fire, state, document: {querySelector: get}};
}
function context(dom, file, script) {
  const window = {addEventListener() {}};
  const sandbox = {
    document: dom.document, window, URLSearchParams, setTimeout, console, encodeURIComponent, location: {hash: ""}, navigator: {},
    fetch: async url => ({ok: true, json: async () => JSON.parse(fs.readFileSync(path.join(site, url), "utf8"))})
  };
  const ctx = vm.createContext(sandbox);
  vm.runInContext(read(script), ctx, {filename: script});
  return ctx;
}
async function until(fn) { for (let i = 0; i < 300; i++) { if (fn()) return true; await new Promise(r => setTimeout(r, 10)); } return false; }

async function filters(page, script, prefix, options) {
  const dom = makeDom(page);
  const ctx = context(dom, page, script);
  const get = dom.get;
  await until(() => get("#" + prefix + "-cards").innerHTML.length > 0);
  const snap = () => ({summary: get("#" + prefix + "-summary").textContent, filters: get("#" + prefix + "-filters").textContent,
    filtersHidden: get("#" + prefix + "-filters").hidden, emptyHidden: get("#" + prefix + "-empty").hidden,
    cards: (get("#" + prefix + "-cards").innerHTML.match(/<article/g) || []).length, focus: dom.state.focus});
  const out = {initial: snap()};
  get("#" + prefix + "-search").value = "zzzzqqqq"; dom.fire("#" + prefix + "-search", "input"); out.noMatch = snap();
  dom.fire("#" + prefix + "-empty-reset", "click"); out.afterEmptyReset = snap(); out.searchValue = get("#" + prefix + "-search").value;
  get("#" + options.select).value = options.value; dom.fire("#" + options.select, "change"); out.selected = snap();
  dom.fire("#" + prefix + "-reset", "click"); out.afterReset = snap(); out.selectValue = get("#" + options.select).value;
  out.ctx = ctx; out.dom = dom;
  return out;
}

(async () => {
  const workflows = data("workflows"), prompts = data("prompts");
  const topic = workflows[0].categories[0];
  const w = await filters("workflows.html", "workflows.js", "workflow", {select: "workflow-topic", value: topic});
  const p = await filters("prompts.html", "prompts.js", "prompt", {select: "prompt-category", value: prompts[0].category});
  const labels = {};
  for (const state of [...new Set(workflows.map(r => r.adoption_state))]) labels[state] = w.ctx.workflowStatusLabel(state);
  const row = workflows.find(r => r.reproduction) || workflows[0];
  w.ctx.location.hash = "#workflow=" + encodeURIComponent(row.id);
  w.ctx.renderWorkflowArticle();
  const article = w.dom.get("#workflow-article");
  const result = {
    workflows: {initial: w.initial, noMatch: w.noMatch, afterEmptyReset: w.afterEmptyReset, searchValue: w.searchValue, selected: w.selected,
      afterReset: w.afterReset, selectValue: w.selectValue, total: workflows.length, topic,
      topicCount: workflows.filter(r => r.categories.includes(topic)).length, labels,
      unknownLabel: w.ctx.workflowStatusLabel("weird"), cardsHtml: w.dom.get("#workflow-cards").innerHTML,
      articleHtml: article.innerHTML, articleHidden: article.hidden, row: {id: row.id, state: row.adoption_state, command: row.reproduction ? row.reproduction.command : null, evidence: row.evidence_level, source: row.source_url}},
    prompts: {initial: p.initial, noMatch: p.noMatch, afterEmptyReset: p.afterEmptyReset, searchValue: p.searchValue, selected: p.selected,
      afterReset: p.afterReset, selectValue: p.selectValue, total: prompts.length, category: prompts[0].category,
      categoryCount: prompts.filter(r => r.category === prompts[0].category).length}
  };
  console.log(JSON.stringify(result));
})().catch(error => { console.error(error); process.exit(1); });
'''


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.nav, self.scripts, self.current = [], [], [], []
        self.title, self.description, self._in_nav, self._in_title, self._href, self._text = "", "", False, False, None, ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
        if tag == "nav" and attrs.get("aria-label") == "Primary":
            self._in_nav = True
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
            if self._in_nav:
                self._href, self._text = attrs["href"], ""
                if attrs.get("aria-current") == "page":
                    self.current.append(attrs["href"])
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._href is not None:
            self._text += data

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._href is not None:
            self.nav.append((self._text.strip(), self._href))
            self._href = None
        if tag == "nav":
            self._in_nav = False


def parse(name):
    refs = Refs()
    refs.feed((SITE / name).read_text(encoding="utf-8"))
    return refs


def text(name):
    return (SITE / name).read_text(encoding="utf-8")


class StaticTests(unittest.TestCase):
    def test_every_page_has_the_same_short_navigation(self):
        for page in sorted(SITE.glob("*.html")):
            refs = parse(page.name)
            self.assertEqual(NAV, [label for label, _ in refs.nav], page.name)
            hrefs = dict(refs.nav)
            self.assertEqual("https://the-825.github.io/staletoast/", hrefs["StaleToast"])
            self.assertEqual("https://the825.co/", hrefs["The 825"])
            if page.name in CURRENT:
                self.assertEqual([CURRENT[page.name]], [label for label, href in refs.nav if href in refs.current], page.name)
            else:
                self.assertEqual([], refs.current, page.name)

    def test_home_tells_the_book_and_companion_story(self):
        refs = parse("index.html")
        page = text("index.html")
        for needed in (BOOK, BOOK + "#companion", "start.html", "workflows.html", "prompts.html",
                       "https://the825.co/improve-my-workflow/", "https://the825.co/resources/breadcrumbs/",
                       "https://the-825.github.io/staletoast/"):
            self.assertIn(needed, refs.links)
        for phrase in ("From Archivist to Architect", "A Practitioner's Field Guide to Building Better Information Systems",
                       "Mr. Jovan Smith", "free companion", "You do not need to buy the book",
                       "does not create automatic memory", "fresh session", "Cue-placement memory",
                       "I am reading the book", "I want the memory method", "Governing Agents That Act"):
            self.assertIn(phrase, page)
        self.assertIn("not the whole companion", page)
        self.assertNotIn("$", page)
        self.assertNotRegex(page.lower(), r"\bprice\b|\bonly \d")

    def test_home_drops_stale_counts_and_the_staletoast_diagram(self):
        page = text("index.html")
        self.assertEqual([], parse("index.html").scripts)
        for stale in ("research-total", "repository-total", "trail-map", "123", "335", "Trail Map", "home.js"):
            self.assertNotIn(stale, page)
        self.assertTrue((SITE / "home.js").is_file())

    def test_titles_and_descriptions_no_longer_call_breadcrumbs_staletoast(self):
        for name in PRIMARY:
            refs = parse(name)
            self.assertNotIn("StaleToast", refs.title, name)
            self.assertNotIn("StaleToast", refs.description, name)
        for name in ("research.html", "repositories.html", "charts.html", "claims.html", "detail.html", "methodology.html", "synthesis.html"):
            self.assertNotIn("| StaleToast", parse(name).title, name)

    def test_jarvis_is_a_historical_case_study_with_its_evidence_limits(self):
        page = text("jarvis.html")
        self.assertIn("historical case study", page)
        self.assertIn("not a currently operating service", page)
        self.assertIn("does not expose private work or certify runtime performance", page)
        self.assertIn('class="system-map"', page)
        self.assertIn(BOOK, parse("jarvis.html").links)

    def test_papers_keeps_publication_types_distinct_and_names_the_book(self):
        page = text("papers.html")
        self.assertIn(BOOK, parse("papers.html").links)
        self.assertIn(BOOK + "#companion", parse("papers.html").links)
        for kind in ("Working paper", "Pattern essay and research agenda", "Operational essay"):
            self.assertIn(kind, page)
        self.assertIn("not the whole companion", page)
        self.assertIn("breadcrumbs-whitepaper.md", page)

    def test_start_page_keeps_cta_and_explains_filenames(self):
        page = text("start.html")
        self.assertIn(BOOK, parse("start.html").links)
        self.assertIn("SESSION_STATE.md", page)
        self.assertIn("plain text files", page)
        self.assertIn("copying it does not create automatic memory", page)

    def test_every_local_link_and_script_resolves(self):
        for page in SITE.glob("*.html"):
            refs = parse(page.name)
            for url in refs.links + refs.scripts:
                if url.startswith(("#", "https://", "http://", "mailto:")):
                    continue
                target = url.split("#", 1)[0].split("?", 1)[0]
                self.assertTrue((SITE / target).is_file(), (page.name, url))

    def test_legacy_reference_routes_still_exist(self):
        for name in ("charts.html", "research.html", "repositories.html", "claims.html", "detail.html", "methodology.html",
                     "synthesis.html", "catalog-redirect.js", "home.js"):
            self.assertTrue((SITE / name).is_file(), name)

    def test_css_defines_cream_and_adds_focus_and_touch_targets(self):
        css = text("app.css")
        self.assertRegex(css, r"--cream:\s*#")
        self.assertIn(":focus-visible", css)
        self.assertIn("min-height: 44px", css)
        self.assertIn("th { position: static;", css)

    def test_no_em_dashes_in_site_files(self):
        for pattern in ("*.html", "*.js", "*.css", "test_visitor_ux.py"):
            for path in SITE.glob(pattern):
                self.assertNotIn(chr(0x2014), path.read_text(encoding="utf-8"), path.name)

    def test_workflow_article_moves_technical_labels_out_of_the_eyebrow(self):
        script = text("workflows.js")
        self.assertNotIn("workflowEscape(row.id)} ·", script)
        self.assertIn('<details class="reference"><summary>Technical reference</summary>', script)


@unittest.skipUnless(shutil.which("node"), "node is required for behavior tests")
class BehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        completed = subprocess.run(["node", "-e", HARNESS, str(SITE)], capture_output=True, text=True, timeout=120)
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)
        cls.result = json.loads(completed.stdout.strip().splitlines()[-1])

    def check_filters(self, key, total, selected_count):
        data = self.result[key]
        self.assertEqual(f"{total} of {total}", data["initial"]["summary"].split(" source-backed")[0].split(" reviewed")[0])
        self.assertTrue(data["initial"]["filtersHidden"])
        self.assertTrue(data["initial"]["emptyHidden"])
        self.assertEqual("", data["initial"]["filters"])
        self.assertFalse(data["noMatch"]["emptyHidden"])
        self.assertEqual(0, data["noMatch"]["cards"])
        self.assertTrue(data["noMatch"]["summary"].startswith("0 of"))
        self.assertIn("zzzzqqqq", data["noMatch"]["filters"])
        self.assertFalse(data["noMatch"]["filtersHidden"])
        self.assertTrue(data["afterEmptyReset"]["emptyHidden"])
        self.assertEqual("", data["searchValue"])
        self.assertEqual(total, data["afterEmptyReset"]["cards"])
        self.assertEqual(selected_count, data["selected"]["cards"])
        self.assertTrue(data["selected"]["summary"].startswith(f"{selected_count} of {total}"))
        self.assertTrue(data["selected"]["filters"].startswith("Filtered by"))
        self.assertEqual(total, data["afterReset"]["cards"])
        self.assertEqual("", data["selectValue"])
        self.assertTrue(data["afterReset"]["filtersHidden"])

    def test_workflow_filters_count_empty_state_and_reset(self):
        data = self.result["workflows"]
        self.check_filters("workflows", data["total"], data["topicCount"])
        self.assertIn(data["topic"].replace("-", " "), data["selected"]["filters"])
        self.assertEqual("#workflow-search", data["afterEmptyReset"]["focus"])

    def test_prompt_filters_count_empty_state_and_reset(self):
        data = self.result["prompts"]
        self.check_filters("prompts", data["total"], data["categoryCount"])

    def test_status_labels_are_human_and_unknown_is_honest(self):
        data = self.result["workflows"]
        for raw, label in data["labels"].items():
            self.assertNotEqual(raw, label)
            self.assertNotEqual("Status not recorded", label)
            self.assertIn(label, data["cardsHtml"])
            self.assertNotIn(f">{raw}<", data["cardsHtml"])
        self.assertEqual("Status not recorded", data["unknownLabel"])

    def test_article_eyebrow_is_plain_and_reference_holds_the_raw_labels(self):
        data = self.result["workflows"]
        html = data["articleHtml"]
        row = data["row"]
        self.assertFalse(data["articleHidden"])
        eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', html).group(1)
        self.assertNotIn(row["id"], eyebrow)
        self.assertNotIn(row["state"], eyebrow)
        main, _, reference = html.partition('<details class="reference">')
        self.assertNotIn(row["id"], main)
        self.assertNotIn(f"<code>{row['state']}</code>", main)
        self.assertIn(row["id"], reference)
        self.assertIn(f"<code>{row['state']}</code>", reference)
        if row["command"]:
            self.assertNotIn(row["command"], main)
            self.assertIn(row["command"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"), reference)
        self.assertIn("Original workflow source", main)
        self.assertIn(row["source"].replace("&", "&amp;"), main)
        self.assertIn(row["evidence"].replace("-", " "), main)


if __name__ == "__main__":
    unittest.main()
