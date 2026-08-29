const type = document.body.dataset.catalog;
const escapeHtml = (value = "") => String(value).replace(/[&<>'"]/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
}[char]));
let items = [];
let claimsById = {};

const detailLink = (kind, id, label) =>
  `<a href="detail.html?type=${kind}&id=${encodeURIComponent(id)}">${escapeHtml(label)}</a>`;
const claimLinks = claims => claims.map(claim => `<a class="pill" href="claims.html#${claim.toLowerCase()}">${escapeHtml(claimsById[claim]?.title || claim)}</a>`).join("");
const label = value => value.replaceAll("-", " ").replace(/\b\w/g, letter => letter.toUpperCase());

function researchRow(item) {
  return `<tr>
    <td class="rank">${escapeHtml(item.id)}</td>
    <td class="rank">${item.evidenceOrder}<small> / 100</small></td>
    <td><strong>${detailLink("research", item.id, item.title)}</strong><br><a href="${escapeHtml(item.url)}">Original source</a></td>
    <td><strong>${item.directnessValue} / 3</strong><br><span class="pill">${escapeHtml(item.directness)}</span></td>
    <td><strong>${item.horizonValue} / 3</strong><br><span class="pill">${escapeHtml(item.horizon)}</span></td>
    <td><strong>${item.claimCount}</strong><br>${claimLinks(item.claims)}</td>
    <td>${escapeHtml(item.citationSignal)}</td>
    <td>${escapeHtml(item.finding)}</td>
    <td>${escapeHtml(item.impact)}</td>
    <td>${escapeHtml(item.flags)}</td>
  </tr>`;
}

function repositoryRow(item) {
  const popularity = item.popularityOrder ? `${item.popularityOrder}<small> / ${item.detailedReviewCount}</small>` : "Not collected";
  const categoryRank = item.categoryPopularityOrder ? `${item.categoryPopularityOrder} / ${item.categoryRepositoryCount}` : "Not collected";
  const stars = item.stars_observed === null ? "Not collected" : `<strong>${Number(item.stars_observed).toLocaleString()}</strong><br><small>observed ${escapeHtml(item.snapshot_date)}</small>`;
  return `<tr>
    <td class="rank">${popularity}</td>
    <td><strong>${detailLink("repositories", item.id, item.repository)}</strong><br><a href="${escapeHtml(item.url)}">GitHub repository</a></td>
    <td><strong>${categoryRank}</strong></td>
    <td><span class="pill">${escapeHtml(label(item.category))}</span></td>
    <td>${escapeHtml(label(item.selection_aspect))}</td>
    <td>${stars}</td>
    <td><strong>${item.visibleMechanisms} / ${item.mechanismTotal}</strong> visible<br><strong>${item.partialMechanisms} / ${item.mechanismTotal}</strong> partial<br><strong>${item.unknownMechanisms} / ${item.mechanismTotal}</strong> unknown</td>
    <td><strong>${item.claimCount}</strong><br>${claimLinks(item.claims)}</td>
    <td><strong>Reviewed ${escapeHtml(item.lastReviewed)}</strong><br><span class="pill">${escapeHtml(label(item.evidence_depth))}</span></td>
    <td>${escapeHtml(item.evidence_note)}</td>
  </tr>`;
}

function render() {
  const query = document.querySelector("#search").value.trim().toLowerCase();
  const filter = document.querySelector("#filter").value;
  const theme = document.querySelector("#theme").value;
  const claim = document.querySelector("#claim").value;
  const sort = document.querySelector("#sort").value;
  let output = items.filter(item => JSON.stringify(item).toLowerCase().includes(query));
  if (filter) output = output.filter(item => type === "research" ? item.directness.startsWith(filter) : item.category === filter);
  if (theme) output = output.filter(item => type === "research" ? item.family === theme : item.lifecycle === theme);
  if (claim) output = output.filter(item => item.claims.includes(claim));
  if (sort === "alpha") output.sort((a, b) => (a.title || a.repository).localeCompare(b.title || b.repository));
  else output.sort((a, b) => (a.evidenceOrder || a.catalogOrder) - (b.evidenceOrder || b.catalogOrder));
  document.querySelector("tbody").innerHTML = output.map(type === "research" ? researchRow : repositoryRow).join("");
  document.querySelector("#count").textContent = `${output.length} of ${items.length}`;
  document.querySelector(".empty").style.display = output.length ? "none" : "block";
}

function addOptions(control, values) {
  control.innerHTML += values.map(value => `<option value="${escapeHtml(value)}">${escapeHtml(label(value))}</option>`).join("");
}

async function catalog() {
  if (!type) return;
  const response = await fetch(`data/${type}.json`);
  if (!response.ok) throw new Error("Catalog data unavailable");
  items = await response.json();
  const claims = await fetch("data/claims.json").then(result => result.json());
  claimsById = Object.fromEntries(claims.map(item => [item.id, item]));
  addOptions(document.querySelector("#filter"), type === "research"
    ? ["D3", "D2", "D1", "D0"]
    : [...new Set(items.map(item => item.category))].sort());
  addOptions(document.querySelector("#theme"), type === "research"
    ? [...new Set(items.map(item => item.family))].sort()
    : [...new Set(items.map(item => item.lifecycle))].sort());
  const claimControl = document.querySelector("#claim");
  claimControl.innerHTML += [...new Set(items.flatMap(item => item.claims))].sort().map(value => `<option value="${escapeHtml(value)}">${escapeHtml(`${value}: ${claimsById[value]?.title || value}`)}</option>`).join("");
  document.querySelectorAll("input, select").forEach(control => control.addEventListener("input", render));
  render();
}

catalog().catch(() => {
  const empty = document.querySelector(".empty");
  if (empty) {
    empty.textContent = "The catalog could not load. Use the repository source files instead.";
    empty.style.display = "block";
  }
});
