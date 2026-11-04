"use strict";
const workflowEscape = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const workflowStatusLabels = {
  discovered: "Found, not yet checked",
  screened: "Source screened, not reproduced",
  reproduced: "Reproduced on a synthetic example",
  adopted: "Marked adopted in the registry",
  rejected: "Reviewed and rejected"
};
let workflowData = [];
const workflowTitle = row => row.id === "WF-004" ? "Finish one piece and explain what comes next" : row.title;
const workflowWording = value => String(value).replaceAll("handoff", "progress note");
const workflowTopic = value => value === "handoff" ? "Picking up the work" : value.replaceAll("-", " ");
function workflowStatusLabel(state) { return workflowStatusLabels[state] || "Status not recorded"; }
function workflowList(values) { return `<ul>${values.map(value => `<li>${workflowEscape(workflowWording(value))}</li>`).join("")}</ul>`; }
function filterWorkflows(rows, query, topic) {
  const needle = String(query || "").trim().toLowerCase();
  return rows.filter(row => (!topic || row.categories.includes(topic)) && JSON.stringify([row.title, workflowTitle(row), row.problem, row.pattern, row.categories, row.guide.when_to_use]).toLowerCase().includes(needle));
}
function describeWorkflowFilters(query, topic) {
  const parts = [];
  const needle = String(query || "").trim();
  if (needle) parts.push(`words "${needle}"`);
  if (topic) parts.push(`topic "${workflowTopic(topic)}"`);
  return parts.length ? `Filtered by ${parts.join(" and ")}.` : "";
}
function renderWorkflowArticle() {
  const article = document.querySelector("#workflow-article");
  const id = new URLSearchParams(location.hash.slice(1)).get("workflow");
  const row = workflowData.find(item => item.id === id);
  article.hidden = !row;
  if (!row) { article.innerHTML = ""; return; }
  const guide = row.guide;
  const reproduction = row.reproduction
    ? `<p>Recorded ${workflowEscape(row.reproduction.date)} local check. ${workflowEscape(row.reproduction.claim_boundary)}.</p>`
    : "";
  const reproductionCommand = row.reproduction
    ? `<p>Reproduction command, recorded ${workflowEscape(row.reproduction.date)}: <code>${workflowEscape(row.reproduction.command)}</code></p>`
    : "";
  article.innerHTML = `<p class="eyebrow">${workflowEscape(workflowStatusLabel(row.adoption_state))}</p><h2>${workflowEscape(workflowTitle(row))}</h2><p class="lede">${workflowEscape(row.problem)}</p><h3>When it helps</h3><p>${workflowEscape(workflowWording(guide.when_to_use))}</p><h3>When to skip it</h3><p>${workflowEscape(workflowWording(guide.when_to_skip))}</p><h3>What you need</h3>${workflowList(guide.requirements)}<h3>How to do it</h3><ol>${guide.steps.map(step => `<li>${workflowEscape(workflowWording(step))}</li>`).join("")}</ol><h3>A small example</h3><p class="workflow-example">${workflowEscape(workflowWording(guide.example))}</p><h3>How to check the result</h3><p>${workflowEscape(workflowWording(guide.completion_check))}</p><h3>Where it can fail</h3>${workflowList(guide.failure_modes)}<h3>Sources and evidence</h3><p><a href="${workflowEscape(row.source_url)}">Original workflow source</a> · ${workflowEscape(row.evidence_level.replaceAll("-", " "))}</p>${reproduction}${workflowList(row.limitations)}<p>${guide.artifacts.map(item => `<a href="${workflowEscape(item.url)}">${workflowEscape(workflowWording(item.label))}</a>`).join(" · ")}</p><details class="reference"><summary>Technical reference</summary><p>Record ID: <code>${workflowEscape(row.id)}</code></p><p>Original catalog title: ${workflowEscape(row.title)}</p><p>Registry adoption state: <code>${workflowEscape(row.adoption_state)}</code></p><p>Evidence level: <code>${workflowEscape(row.evidence_level)}</code></p>${reproductionCommand}</details><p><a href="https://github.com/The-825/breadcrumbs/issues/new?title=${encodeURIComponent(`Workflow correction: ${row.id}`)}">Suggest a correction</a> · <a href="#">Back to the guide</a></p>`;
  article.focus({ preventScroll: true });
  article.scrollIntoView({ block: "start" });
}
function renderWorkflows() {
  const query = document.querySelector("#workflow-search").value;
  const topic = document.querySelector("#workflow-topic").value;
  const rows = filterWorkflows(workflowData, query, topic);
  const active = describeWorkflowFilters(query, topic);
  document.querySelector("#workflow-summary").textContent = `${rows.length} of ${workflowData.length} source-backed workflow articles.`;
  const filters = document.querySelector("#workflow-filters");
  filters.textContent = active;
  filters.hidden = !active;
  document.querySelector("#workflow-empty").hidden = rows.length > 0;
  document.querySelector("#workflow-cards").innerHTML = rows.map(row => `<article class="card workflow-card"><span class="evidence-badge">${workflowEscape(workflowStatusLabel(row.adoption_state))}</span><h2>${workflowEscape(workflowTitle(row))}</h2><p>${workflowEscape(row.problem)}</p><p class="note">${workflowEscape(row.categories.map(workflowTopic).join(" · "))}</p><a class="button secondary" href="#workflow=${encodeURIComponent(row.id)}">Read the workflow</a></article>`).join("");
}
function resetWorkflowFilters() {
  const search = document.querySelector("#workflow-search");
  search.value = "";
  document.querySelector("#workflow-topic").value = "";
  renderWorkflows();
  search.focus();
}
async function loadWorkflows() {
  try {
    const response = await fetch("data/workflows.json");
    if (!response.ok) throw new Error("Workflow articles are unavailable.");
    workflowData = await response.json();
    const topics = [...new Set(workflowData.flatMap(row => row.categories))].sort();
    document.querySelector("#workflow-topic").innerHTML += topics.map(topic => `<option value="${workflowEscape(topic)}">${workflowEscape(workflowTopic(topic))}</option>`).join("");
    document.querySelector("#workflow-search").addEventListener("input", renderWorkflows);
    document.querySelector("#workflow-topic").addEventListener("change", renderWorkflows);
    document.querySelector("#workflow-reset").addEventListener("click", resetWorkflowFilters);
    document.querySelector("#workflow-empty-reset").addEventListener("click", resetWorkflowFilters);
    window.addEventListener("hashchange", renderWorkflowArticle);
    renderWorkflows(); renderWorkflowArticle();
  } catch (error) {
    const target = document.querySelector("#workflow-error"); target.hidden = false; target.textContent = error.message;
    document.querySelector("#workflow-summary").textContent = "The guide could not be loaded. Use the evidence registry while it is unavailable.";
  }
}
loadWorkflows();
