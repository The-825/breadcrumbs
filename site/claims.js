const escClaim = (value = "") => String(value).replace(/[&<>'"]/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[character]));

function inspector(item) {
  return `<p class="eyebrow">${escClaim(item.theme)}</p><h2>${escClaim(item.readerLabel)}</h2><p>${escClaim(item.title)}</p><p class="lede">${escClaim(EvidenceTopics.text(item.claim))}</p><dl><dt>Evidence profile</dt><dd>${escClaim(EvidenceTopics.text(item.profile))}</dd><dt>Disposition</dt><dd>${escClaim(EvidenceTopics.text(item.disposition))}</dd><dt>Support</dt><dd>${escClaim(EvidenceTopics.text(item.supports))}</dd><dt>What would disprove it</dt><dd>${escClaim(EvidenceTopics.text(item.nullCase))}</dd><dt>Next test</dt><dd>${escClaim(EvidenceTopics.text(item.nextTest))}</dd></dl><details><summary>Evidence reference</summary><p>${escClaim(item.id)}</p></details>`;
}

fetch("data/claims.json").then(response => response.json()).then(claims => {
  EvidenceTopics.install(claims);
  const themes = [...new Set(claims.map(item => item.theme))];
  const nodes = themes.map(theme => `<section class="claim-cluster"><h2>${escClaim(theme)}</h2><div>${claims.filter(item => item.theme === theme).map(item => `<button class="claim-node" data-claim="${escClaim(item.id)}"><strong>${escClaim(item.readerLabel)}</strong></button>`).join("")}</div></section>`).join("");
  document.querySelector("#claims").innerHTML = `<div class="claim-graph" aria-label="Interactive landscape of seventeen collaborative-intelligence claims">${nodes}<div class="claim-core" aria-hidden="true">StaleToast<br><span>17 bounded claims</span></div></div><aside id="claim-inspector" class="detail claim-inspector">${inspector(claims[0])}</aside>`;
  const byId = Object.fromEntries(claims.map(item => [item.id, item]));
  const select = id => {
    document.querySelectorAll(".claim-node").forEach(node => node.classList.toggle("selected", node.dataset.claim === id));
    document.querySelector("#claim-inspector").innerHTML = inspector(byId[id]);
    history.replaceState(null, "", `#${id.toLowerCase()}`);
  };
  document.querySelectorAll(".claim-node").forEach(node => node.addEventListener("click", () => select(node.dataset.claim)));
  const initial = location.hash.slice(1).toUpperCase();
  select(byId[initial] ? initial : claims[0].id);
}).catch(() => { document.querySelector("#claims").textContent = "The claim landscape could not load. Use the public repository record instead."; });
