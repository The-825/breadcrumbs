const esc = (value = "") => String(value).replace(/[&<>'"]/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[character]));
const params = new URLSearchParams(location.search);
const type = params.get("type");
const id = params.get("id");
const pills = values => values.map(value => `<span class="pill">${esc(value)}</span>`).join("");
const bar = (label, value, total, tone = "visible") => `<div class="bar-row"><span>${esc(label)}</span><div class="bar-track" aria-hidden="true"><i class="${tone}" style="width:${Math.round((value / total) * 100)}%"></i></div><strong>${value} / ${total}</strong></div>`;
const sentence = value => value ? value.charAt(0).toUpperCase() + value.slice(1) : "";
const relatedByClaims = (candidates, item, name) => candidates.filter(candidate => candidate.id !== item.id && candidate.claims.some(claim => item.claims.includes(claim))).map(candidate => ({candidate, overlap: candidate.claims.filter(claim => item.claims.includes(claim)).length})).sort((a, b) => b.overlap - a.overlap || name(a.candidate).localeCompare(name(b.candidate))).slice(0, 5).map(result => result.candidate);
const claimLinks = (values, claimsById) => values.map(value => `<a class="claim-link" href="claims.html#${value.toLowerCase()}"><small>${esc(value)}</small><strong>${esc(claimsById[value]?.title || value)}</strong></a>`).join("");

function research(item, all, repositories, claimsById) {
  const related = relatedByClaims(all, item, candidate => candidate.title);
  const linked = relatedByClaims(repositories, item, candidate => candidate.repository);
  return `<p class="eyebrow">Research profile</p><h1>${esc(item.title)}</h1><p class="lede">${esc(item.finding)}</p>
    <div class="profile"><div class="meter"><small>Evidence order</small><strong>${item.evidenceOrder} / 100</strong></div><div class="meter"><small>Directness</small><strong>${item.directnessValue} / 3</strong><span>${esc(item.directness)}</span></div><div class="meter"><small>Horizon</small><strong>${item.horizonValue} / 3</strong><span>${esc(item.horizon)}</span></div><div class="meter"><small>Citation signal</small><strong>${esc(item.citationSignal)}</strong></div></div>
    <section class="detail split-detail"><div><p class="eyebrow">Our reading</p><h2>What this changes</h2><p>${esc(sentence(item.impact))}</p><h3>Boundary and next question</h3><p>${esc(sentence(item.boundary))}</p></div><div class="signal-panel"><h3>Evidence profile</h3>${bar("Directness", item.directnessValue, 3)}${bar("Horizon", item.horizonValue, 3, "partial")}<p><strong>Evidence family:</strong> ${esc(item.familyLabel)}</p><p><strong>Study design:</strong> ${esc(sentence(item.design))}</p></div></section>
    <section class="section related"><div class="card"><h2>Visible risks</h2><p>${esc(sentence(item.flags))}</p><h3>Linked claims</h3><div class="claim-links">${claimLinks(item.claims, claimsById)}</div></div><div class="card"><h2>Source</h2><p>The original source remains authoritative. This profile is a bounded interpretation.</p><a class="button" href="${esc(item.url)}">Open original source</a></div></section>
    <section class="section related"><div class="card"><h2>Related research</h2>${related.map(candidate => `<a href="detail.html?type=research&id=${candidate.id}">${esc(candidate.title)}</a>`).join("") || "<p>No related records.</p>"}</div><div class="card"><h2>Related repositories</h2>${linked.map(candidate => `<a href="detail.html?type=repositories&id=${candidate.id}">${esc(candidate.repository)}</a>`).join("") || "<p>No related records.</p>"}</div></section>`;
}

function repository(item, all, researchItems, claimsById) {
  const related = relatedByClaims(all, item, candidate => candidate.repository);
  const linked = relatedByClaims(researchItems, item, candidate => candidate.title);
  const visible = Object.entries(item.mechanisms).filter(([, value]) => value === "V").map(([key]) => key.replaceAll("_", " "));
  const partial = Object.entries(item.mechanisms).filter(([, value]) => value === "P").map(([key]) => key.replaceAll("_", " "));
  const notObserved = item.mechanismTotal - visible.length - partial.length;
  return `<p class="eyebrow">Repository profile</p><h1>${esc(item.repository)}</h1><p class="lede">${esc(item.evidence_note)}</p>
    <div class="profile"><div class="meter"><small>Global popularity</small><strong>${item.popularityOrder} / 100</strong></div><div class="meter"><small>Within category</small><strong>${item.categoryPopularityOrder} / ${item.categoryRepositoryCount}</strong><span>${esc(item.category.replaceAll("-", " "))}</span></div><div class="meter"><small>Stars observed</small><strong>${Number(item.stars_observed).toLocaleString()}</strong><span>on ${esc(item.starsObservedDate)}</span></div><div class="meter"><small>Last reviewed</small><strong>${esc(item.lastReviewed)}</strong><span>${esc(item.evidence_depth.replaceAll("-", " "))}</span></div></div>
    <section class="detail split-detail"><div><p class="eyebrow">Our reading</p><h2>What is visible</h2><p>${esc(sentence(item.evidence_note))}</p><h3>Classification</h3><p><strong>Category:</strong> ${esc(item.category.replaceAll("-", " "))}<br><strong>Selection lens:</strong> ${esc(item.selection_aspect.replaceAll("-", " "))}</p><h3>Linked claims</h3><div class="claim-links">${claimLinks(item.claims, claimsById)}</div></div><div class="signal-panel"><h3>Mechanism profile</h3>${bar("Visible", visible.length, item.mechanismTotal)}${bar("Partial", partial.length, item.mechanismTotal, "partial")}${bar("Not observed or out of scope", notObserved, item.mechanismTotal, "quiet")}<p><strong>Visible</strong> means the pinned evidence directly exposed the mechanism. <strong>Partial</strong> means only part of the mechanism was exposed or the evidence was incomplete.</p><p class="note">This chart reports what the pinned review found. It is not a performance score.</p></div></section>
    <section class="section related"><div class="card"><h2>Visible mechanisms</h2>${pills(visible) || "<p>None observed.</p>"}</div><div class="card"><h2>Partial mechanisms</h2>${pills(partial) || "<p>None observed.</p>"}</div></section>
    <section class="section related"><div class="card"><h2>Related repositories</h2>${related.map(candidate => `<a href="detail.html?type=repositories&id=${candidate.id}">${esc(candidate.repository)}</a>`).join("")}</div><div class="card"><h2>Related research</h2>${linked.map(candidate => `<a href="detail.html?type=research&id=${candidate.id}">${esc(candidate.title)}</a>`).join("") || "<p>No related records.</p>"}</div></section>
    <section class="section"><p class="note">Stars are a dated audience signal. Evidence depth describes the review performed. Neither proves quality.</p><a class="button" href="${esc(item.url)}">Open GitHub repository</a></section>`;
}

async function init() {
  if (!["research", "repositories"].includes(type) || !id) throw Error();
  const [current, researchItems, repositories, claims] = await Promise.all([fetch(`data/${type}.json`).then(response => response.json()), fetch("data/research.json").then(response => response.json()), fetch("data/repositories.json").then(response => response.json()), fetch("data/claims.json").then(response => response.json())]);
  const claimsById = Object.fromEntries(claims.map(claim => [claim.id, claim]));
  const item = current.find(candidate => candidate.id === id);
  if (!item) throw Error();
  document.title = `${item.title || item.repository} | Breadcrumbs`;
  document.querySelector("main").innerHTML = type === "research" ? research(item, researchItems, repositories, claimsById) : repository(item, repositories, researchItems, claimsById);
}

init().catch(() => { document.querySelector("main").innerHTML = '<p class="eyebrow">Not found</p><h1>This breadcrumb is missing.</h1><p><a href="index.html">Return to the Trail Map</a></p>'; });
