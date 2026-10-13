"use strict";
const promptEscape = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const promptCategories = {workflows:"Workflows", "data-stacks":"Data stacks", systems:"Systems"};
let promptData = [];
const promptList = values => `<ul>${values.map(value => `<li>${promptEscape(value)}</li>`).join("")}</ul>`;
function renderPromptArticle() {
  const article = document.querySelector("#prompt-article");
  const id = new URLSearchParams(location.hash.slice(1)).get("prompt");
  const row = promptData.find(item => item.id === id);
  article.hidden = !row;
  if (!row) { article.innerHTML = ""; return; }
  article.innerHTML = `<p class="eyebrow">${promptCategories[row.category]} · Reviewed template</p><h2>${promptEscape(row.title)}</h2><p class="lede">${promptEscape(row.purpose)}</p><h3>What to provide</h3>${promptList(row.required_inputs.map(field => field.toLowerCase().replaceAll("_", " ")))}<h3>The prompt</h3><p>Use public or synthetic inputs first. Fill every named field before using the prompt in an approved tool.</p><textarea id="prompt-text" class="prompt-text" aria-label="Prompt text" readonly>${promptEscape(row.template)}</textarea><div class="actions"><button class="button" id="copy-prompt" type="button">Copy prompt</button><button class="button secondary" id="example-prompt" type="button">Fill with synthetic example</button><button class="button secondary" id="reset-prompt" type="button">Show template</button></div><p id="copy-status" role="status"></p><h3>Check the result</h3>${promptList(row.output_checks)}<h3>Limits and evidence</h3>${promptList(row.limitations)}<p>Version ${promptEscape(row.version)}, reviewed ${promptEscape(row.reviewed_date)}. Model outputs have not been benchmarked.</p><p>${row.source_urls.map((url, index) => `<a href="${promptEscape(url)}">Source reference ${index + 1}</a>`).join(" · ")}</p><details><summary>Catalog reference</summary><p>${promptEscape(row.id)}</p></details><p><a href="https://github.com/The-825/breadcrumbs/issues/new?title=${encodeURIComponent(`Prompt correction: ${row.id}`)}">Suggest a correction</a> · <a href="#">Back to the library</a></p>`;
  const text = document.querySelector("#prompt-text");
  const status = document.querySelector("#copy-status");
  document.querySelector("#example-prompt").addEventListener("click", () => {
    text.value = row.template.replace(/\{\{([A-Z_]+)\}\}/g, (_match, field) => row.sample_inputs[field]);
    status.textContent = "Synthetic example filled. No model call has been made.";
  });
  document.querySelector("#reset-prompt").addEventListener("click", () => { text.value = row.template; status.textContent = "Template restored."; });
  document.querySelector("#copy-prompt").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(text.value); status.textContent = "Prompt copied."; }
    catch { text.focus(); text.select(); status.textContent = "Copy was unavailable. The prompt is selected for manual copying."; }
  });
  article.focus({preventScroll:true}); article.scrollIntoView({block:"start"});
}
function renderPrompts() {
  const query = document.querySelector("#prompt-search").value.trim().toLowerCase();
  const category = document.querySelector("#prompt-category").value;
  const rows = promptData.filter(row => (!category || row.category === category) && JSON.stringify([row.title, row.purpose, row.category, row.template]).toLowerCase().includes(query));
  document.querySelector("#prompt-summary").textContent = `${rows.length} of ${promptData.length} reviewed prompt templates.`;
  document.querySelector("#prompt-cards").innerHTML = rows.map(row => `<article class="card workflow-card"><p class="eyebrow">${promptCategories[row.category]}</p><h2>${promptEscape(row.title)}</h2><p>${promptEscape(row.purpose)}</p><a class="button secondary" href="#prompt=${encodeURIComponent(row.id)}">Open prompt</a></article>`).join("");
}
async function loadPrompts() {
  try {
    const response = await fetch("data/prompts.json");
    if (!response.ok) throw new Error("Prompt data is unavailable.");
    promptData = await response.json();
    document.querySelector("#prompt-search").addEventListener("input", renderPrompts);
    document.querySelector("#prompt-category").addEventListener("change", renderPrompts);
    window.addEventListener("hashchange", renderPromptArticle);
    renderPrompts(); renderPromptArticle();
  } catch (error) {
    const target = document.querySelector("#prompt-error"); target.hidden = false; target.textContent = error.message;
    document.querySelector("#prompt-summary").textContent = "The prompt library could not load. Read the source catalog in the repository.";
  }
}
loadPrompts();
