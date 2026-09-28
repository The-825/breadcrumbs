async function readCatalog(name) {
  const response = await fetch(`data/${name}.json`);
  if (!response.ok) throw new Error("Catalog data unavailable");
  const records = await response.json();
  if (!Array.isArray(records)) throw new Error("Invalid catalog data");
  return records;
}

async function showTotals() {
  const [research, repositories] = await Promise.all([
    readCatalog("research"), readCatalog("repositories"),
  ]);
  const detailed = repositories.filter(item => item.evidence_depth === "readme-screened").length;
  const portable = repositories.filter(item => item.evidence_depth === "source-assessment").length;
  if (detailed + portable !== repositories.length) throw new Error("Unknown repository evidence depth");
  document.querySelector("#research-total").textContent = research.length;
  document.querySelector("#repository-total").textContent = repositories.length;
  document.querySelector("#repository-depth-summary").textContent =
    `${detailed} pinned mechanism reviews plus ${portable} portable-only public assessment records queued for deeper review.`;
}

showTotals().catch(() => {
  document.querySelector("#research-total").textContent = "Unavailable";
  document.querySelector("#repository-total").textContent = "Unavailable";
  document.querySelector("#repository-depth-summary").textContent =
    "Catalog totals are unavailable. Open the trails for source records.";
});
