"use strict";
const EvidenceTopics = {
  labels: {},
  install(claims) {
    this.labels = Object.fromEntries(claims.map(claim => [claim.id, claim.readerLabel || claim.title]));
  },
  label(id) { return this.labels[id] || "Topic awaiting a label"; },
  text(value) {
    return String(value ?? "").replace(/\bCI-\d{3}\b/g, id => this.label(id));
  }
};
