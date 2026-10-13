"use strict";
const workflowEscape = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
let workflowData = [];
function workflowList(values) { return `<ul>${values.map(value => `<li>${workflowEscape(value)}</li>`).join("")}</ul>`; }
function renderWorkflowArticle() {
  const article = document.querySelector("#workflow-article");
  const id = new URLSearchParams(location.hash.slice(1)).get("workflow");
  const row = workflowData.find(item => item.id === id);
  article.hidden = !row;
  if (!row) { article.innerHTML = ""; return; }
  const guide = row.guide;
  article.innerHTML = `<p class="eyebrow">${workflowEscape(row.id)} · ${workflowEscape(row.adoption_state)}</p><h2>${workflowEscape(row.title)}</h2><p class="lede">${workflowEscape(row.problem)}</p><h3>When it helps</h3><p>${workflowEscape(guide.when_to_use)}</p><h3>When to skip it</h3><p>${workflowEscape(guide.when_to_skip)}</p><h3>What you need</h3>${workflowList(guide.requirements)}<h3>How to do it</h3><ol>${guide.steps.map(step => `<li>${workflowEscape(step)}</li>`).join("")}</ol><h3>A small example</h3><p class="workflow-example">${workflowEscape(guide.example)}</p><h3>How to check the result</h3><p>${workflowEscape(guide.completion_check)}</p><h3>Where it can fail</h3>${workflowList(guide.failure_modes)}<h3>Sources and evidence</h3><p><a href="${workflowEscape(row.source_url)}">Original workflow source</a> · ${workflowEscape(row.evidence_level.replaceAll("-", " "))}</p>${row.reproduction ? `<p>Recorded ${workflowEscape(row.reproduction.date)} local check: <code>${workflowEscape(row.reproduction.command)}</code>. ${workflowEscape(row.reproduction.claim_boundary)}.</p>` : ""}${workflowList(row.limitations)}<p>${guide.artifacts.map(item => `<a href="${workflowEscape(item.url)}">${workflowEscape(item.label)}</a>`).join(" · ")}</p><p><a href="https://github.com/The-825/breadcrumbs/issues/new?title=${encodeURIComponent(`Workflow correction: ${row.id}`)}">Suggest a correction</a> · <a href="#">Back to the guide</a></p>`;
  article.focus({ preventScroll: true });
  article.scrollIntoView({ block: "start" });
}
function renderWorkflows() {
  const query = document.querySelector("#workflow-search").value.trim().toLowerCase();
  const topic = document.querySelector("#workflow-topic").value;
  const rows = workflowData.filter(row => (!topic || row.categories.includes(topic)) && JSON.stringify([row.title, row.problem, row.pattern, row.categories, row.guide.when_to_use]).toLowerCase().includes(query));
  document.querySelector("#workflow-summary").textContent = `${rows.length} of ${workflowData.length} source-backed workflow articles.`;
  document.querySelector("#workflow-cards").innerHTML = rows.map(row => `<article class="card workflow-card"><span class="evidence-badge">${workflowEscape(row.adoption_state)}</span><h2>${workflowEscape(row.title)}</h2><p>${workflowEscape(row.problem)}</p><p class="note">${workflowEscape(row.categories.join(" · "))}</p><a class="button secondary" href="#workflow=${encodeURIComponent(row.id)}">Read the workflow</a></article>`).join("");
}
async function loadWorkflows() {
  try {
    const response = await fetch("data/workflows.json");
    if (!response.ok) throw new Error("Workflow articles are unavailable.");
    workflowData = await response.json();
    const topics = [...new Set(workflowData.flatMap(row => row.categories))].sort();
    document.querySelector("#workflow-topic").innerHTML += topics.map(topic => `<option value="${workflowEscape(topic)}">${workflowEscape(topic)}</option>`).join("");
    document.querySelector("#workflow-search").addEventListener("input", renderWorkflows);
    document.querySelector("#workflow-topic").addEventListener("change", renderWorkflows);
    window.addEventListener("hashchange", renderWorkflowArticle);
    renderWorkflows(); renderWorkflowArticle();
  } catch (error) {
    const target = document.querySelector("#workflow-error"); target.hidden = false; target.textContent = error.message;
    document.querySelector("#workflow-summary").textContent = "The guide could not be loaded. Use the evidence registry while it is unavailable.";
  }
}
loadWorkflows();
