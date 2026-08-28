const type = document.body.dataset.catalog;
const escapeHtml = (value = "") => String(value).replace(/[&<>'"]/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
}[char]));
let items = [];

const detailLink = (kind, id, label) =>
  `<a href="detail.html?type=${kind}&id=${encodeURIComponent(id)}">${escapeHtml(label)}</a>`;
const claimLinks = claims => claims.map(claim => `<a class="pill" href="claims.html#${claim.toLowerCase()}">${escapeHtml(claim)}</a>`).join("");
const label = value => value.replaceAll("-", " ").replace(/\b\w/g, letter => letter.toUpperCase());

function researchRow(item) {
  return `<tr>
    <td class="rank">${item.evidenceOrder}<small> / 100</small></td>
    <td><strong>${detailLink("research", item.id, `${item.id}. ${item.title}`)}</strong><br><a href="${escapeHtml(item.url)}">Original source</a></td>
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
  return `<tr>
    <td class="rank">${item.popularityOrder}<small> / 100</small></td>
    <td><strong>${detailLink("repositories", item.id, item.repository)}</strong><br><a href="${escapeHtml(item.url)}">GitHub repository</a></td>
    <td><strong>${item.aspectPopularityOrder} / ${item.aspectRepositoryCount}</strong><br><span class="pill">${escapeHtml(item.selection_aspect)}</span></td>
    <td><strong>${Number(item.stars_observed).toLocaleString()}</strong><br><small>observed ${escapeHtml(item.snapshot_date)}</small></td>
    <td><strong>${item.visibleMechanisms} / ${item.mechanismTotal}</strong> visible<br><strong>${item.partialMechanisms} / ${item.mechanismTotal}</strong> partial</td>
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
  if (filter) output = output.filter(item => type === "research" ? item.directness.startsWith(filter) : item.selection_aspect === filter);
  if (theme) output = output.filter(item => type === "research" ? item.family === theme : item.lifecycle === theme);
  if (claim) output = output.filter(item => item.claims.includes(claim));
  if (sort === "alpha") output.sort((a, b) => (a.title || a.repository).localeCompare(b.title || b.repository));
  else output.sort((a, b) => (a.evidenceOrder || a.popularityOrder) - (b.evidenceOrder || b.popularityOrder));
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
  addOptions(document.querySelector("#filter"), type === "research"
    ? ["D3", "D2", "D1", "D0"]
    : [...new Set(items.map(item => item.selection_aspect))].sort());
  addOptions(document.querySelector("#theme"), type === "research"
    ? [...new Set(items.map(item => item.family))].sort()
    : [...new Set(items.map(item => item.lifecycle))].sort());
  addOptions(document.querySelector("#claim"), [...new Set(items.flatMap(item => item.claims))].sort());
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
