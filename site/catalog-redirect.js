"use strict";
const catalogPages = new Set(["charts.html", "research.html", "repositories.html", "claims.html", "detail.html", "methodology.html", "synthesis.html"]);
const catalogPage = window.location.pathname.split("/").pop();
if (catalogPages.has(catalogPage)) {
  window.location.replace(`https://the-825.github.io/staletoast/${catalogPage}${window.location.search}${window.location.hash}`);
}
