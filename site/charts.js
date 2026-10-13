"use strict";
const chartEscape = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
let chartData;
function renderChart() {
  const kind = document.querySelector("#chart-kind").value;
  const edition = chartData.history.find(row => row.edition_date === document.querySelector("#edition").value);
  const chart = edition.charts[kind];
  const query = document.querySelector("#chart-search").value.trim().toLowerCase();
  const rows = chart.entries.filter(row => JSON.stringify([row.title, row.claims, row.claims.map(id => EvidenceTopics.label(id)), row.reason, row.family]).toLowerCase().includes(query));
  document.querySelector("#chart-summary").textContent = `${rows.length} of ${chart.entries.length} chart entries shown. Edition ${edition.edition_date}. ${chart.archive_count} records in the archive.`;
  document.querySelector("#chart-boundary").textContent = `${chart.eligible_count} source-screened records were eligible. ${chart.cutoff_tied_outside_chart ? `${chart.cutoff_tied_outside_chart} records share the cutoff priority but are outside this 100-position edition. ` : ""}Candidates and review limits remain visible; a place on the chart grants no adoption authority.`;
  document.querySelector("#chart-list").innerHTML = rows.map(row => {
    const movement = row.entry_state === "new" ? "NEW" : row.entry_state === "reentry" ? "RE-ENTRY" : row.movement > 0 ? `UP ${row.movement}` : row.movement < 0 ? `DOWN ${-row.movement}` : "UNCHANGED";
    return `<li><span class="chart-position" aria-label="Position ${row.position}">${row.position}</span><div><h2><a href="${chartEscape(row.url)}">${chartEscape(row.title)}</a></h2><span class="evidence-badge">${chartEscape(row.evidence_depth.replaceAll("-", " "))}</span>${row.record_state ? `<span class="evidence-badge">${chartEscape(row.record_state.replaceAll("-", " "))}</span>` : ""}<p>${chartEscape(EvidenceTopics.text(row.reason).replace(/^Relevant to /, "Focus: "))}</p><p class="note">${row.claims.map(id => `<a href="claims.html#${id.toLowerCase()}">${chartEscape(EvidenceTopics.label(id))}</a>`).join(" · ")} · Priority group ${row.priority_group}${row.snapshot_commit ? ` · Source ${chartEscape(row.snapshot_commit.slice(0, 8))}` : ""}</p></div><aside><span class="movement">${movement}</span><span>Previous: ${row.previous_position ?? (row.entry_state === "reentry" ? "Off chart" : "First appearance")}</span><span>Peak: ${row.peak_position}</span><span>Appearances: ${row.appearances}</span></aside></li>`;
  }).join("");
}
async function loadCharts() {
  try {
    const response = await fetch("data/charts.json");
    if (!response.ok) throw new Error("Chart data is unavailable.");
    const claimsResponse = await fetch("data/claims.json");
    if (!claimsResponse.ok) throw new Error("Topic labels are unavailable.");
    EvidenceTopics.install(await claimsResponse.json());
    chartData = await response.json();
    document.querySelector("#edition").innerHTML = chartData.history.slice().reverse().map(row => `<option value="${chartEscape(row.edition_date)}">${chartEscape(row.edition_date)}</option>`).join("");
    for (const selector of ["#chart-kind", "#edition", "#chart-search"]) document.querySelector(selector).addEventListener(selector === "#chart-search" ? "input" : "change", renderChart);
    renderChart();
  } catch (error) {
    const target = document.querySelector("#chart-error"); target.hidden = false; target.textContent = error.message;
    document.querySelector("#chart-summary").textContent = "The chart could not be loaded. Try again later or read the source ledger.";
  }
}
loadCharts();
