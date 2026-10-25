/* Local synthetic simulation. No network or persistent storage. */
(function (root) {
  'use strict';
  const defaultFields = [
    {key:'request', label:'What needs doing?', required:true},
    {key:'owner', label:'Responsible role', required:true},
    {key:'due', label:'Follow-up date', required:true}
  ];
  function validateFields(fields) {
    if (!Array.isArray(fields) || !fields.length) throw Error('Provide at least one field.');
    const keys = new Set();
    for (const f of fields) {
      if (!f || !/^[a-z][a-z0-9_]{0,39}$/.test(f.key) || keys.has(f.key) ||
          typeof f.label !== 'string' || !f.label.trim() || typeof f.required !== 'boolean' ||
          ['__proto__','constructor','prototype'].includes(f.key)) throw Error('Invalid or duplicate field definition.');
      keys.add(f.key);
    }
    return structuredClone(fields);
  }
  class Workflow {
    constructor(fields=defaultFields) { this.fields=validateFields(fields); this.records=[]; this.history=[]; }
    event(id, type, detail) { this.history.push({sequence:this.history.length+1,record_id:id,type,detail,time:new Date().toISOString()}); }
    intake(id, values, review={}) {
      if (!/^SYN-[A-Z0-9-]{1,32}$/.test(id)) throw Error('Use a synthetic ID beginning SYN-.');
      if (!values || typeof values !== 'object' || Array.isArray(values)) throw Error('Provide field values.');
      const clean=Object.fromEntries(this.fields.map(f=>[f.key,String(values[f.key]??'').trim()]));
      const missing=this.fields.filter(f=>f.required&&!clean[f.key]&&f.key!=='due').map(f=>f.label);
      if (missing.length) throw Error('Missing: '+missing.join(', '));
      const flags={conflict:review.conflict===true,externalAction:review.externalAction===true,permission:review.permission==='simulated_approved'?'simulated_approved':'missing',preparedFollowUp:review.preparedFollowUp===true,ackMissing:review.ackMissing===true};
      const old=this.records.find(r=>r.id===id);
      if (old) {
        if (JSON.stringify(old.values)!==JSON.stringify(clean)||JSON.stringify(old.review)!==JSON.stringify(flags)) throw Error('Repeated ID has different input. Inspect the existing record; do not overwrite it.');
        this.event(id,'duplicate_ignored','Identical intake reused the existing record.'); return old;
      }
      const holds=[];
      if(this.fields.some(f=>f.key==='due'&&f.required)&&!clean.due)holds.push('missing_date');
      if(flags.conflict)holds.push('conflicting_instructions');
      if(flags.externalAction&&flags.permission!=='simulated_approved')holds.push('missing_permission');
      if(flags.ackMissing)holds.push('missing_delivery_acknowledgment');
      const row={id,values:clean,review:flags,state:holds.length?'held':'new',holds,outcome:'',draft:'',permission:flags.externalAction?flags.permission:'not_requested',delivery:{prepared:flags.preparedFollowUp,sent:'not_connected',acknowledged:flags.ackMissing?'unknown':'not_connected'},recovery:holds.map(h=>({missing_date:'Ask for the date once; retain unknown until supplied.',conflicting_instructions:'Ask the requester to resolve the conflict before the dependent action.',missing_permission:'Keep an unsent draft; obtain permission through the real owning system.',missing_delivery_acknowledgment:'Inspect delivery evidence through the authorized owner. Do not infer delivery or resend.'})[h])};
      this.records.push(row); this.event(id,'intake','Synthetic record accepted.');
      if(holds.length)this.event(id,'held',JSON.stringify({holds,recovery:row.recovery}));
      return row;
    }
    prepareDraft(id) {
      const r=this.records.find(x=>x.id===id);if(!r)throw Error('Unknown record.');
      if(r.holds.includes('conflicting_instructions'))throw Error('Resolve the conflicting instructions before drafting.');
      if(r.holds.includes('missing_delivery_acknowledgment')||r.delivery.acknowledged==='unknown')throw Error('Missing acknowledgment: inspect the prior delivery evidence; do not prepare another send.');
      if(r.draft){this.event(id,'draft_reused','Existing local draft retained; no second action.');return r;}
      r.draft='UNSENT SYNTHETIC DRAFT: '+Object.entries(r.values).map(([k,v])=>k+': '+(v||'unknown')).join('; ');
      r.delivery.prepared=true;this.event(id,'draft_prepared','Local draft only. Permission declarations are simulated; nothing sent.');return r;
    }
    clarifyDate(id) {
      const r=this.records.find(x=>x.id===id);if(!r||!r.holds.includes('missing_date'))throw Error('No missing date to clarify.');
      if(r.dateClarification){return r.dateClarification;}
      r.dateClarification='UNSENT: What follow-up date should be recorded? The date is currently unknown.';
      this.event(id,'clarification_prepared',r.dateClarification);return r.dateClarification;
    }
    resolve(id, values, review, note, acknowledgmentReference='') {
      const row=this.records.find(x=>x.id===id);
      if(!row||row.state!=='held')throw Error('Only a held request can be resolved here.');
      if(typeof note!=='string'||!note.trim())throw Error('Record what changed and why.');
      const priorAckUnknown=row.holds.includes('missing_delivery_acknowledgment')||row.delivery.acknowledged==='unknown';
      if(priorAckUnknown && !review.ackMissing && !/^SYN-EVIDENCE-[A-Z0-9-]+$/.test(acknowledgmentReference))throw Error('Missing acknowledgment needs an explicit synthetic evidence reference; otherwise keep the hold.');
      const trial=new Workflow(this.fields);const replacement=trial.intake(id,values,review);
      const previous=structuredClone(row);
      row.values=replacement.values;row.review=replacement.review;row.holds=replacement.holds;row.recovery=replacement.recovery;row.permission=replacement.permission;row.state=replacement.state;
      // An existing prepared draft is stale after any reviewed edit.
      row.draft='';row.delivery.prepared=previous.delivery.prepared||replacement.delivery.prepared;
      if(replacement.holds.includes('missing_delivery_acknowledgment'))row.delivery.acknowledged='unknown';
      if(priorAckUnknown&&!review.ackMissing){row.delivery.acknowledged='synthetic_evidence_recorded';row.acknowledgmentReference=acknowledgmentReference;}
      this.event(id,'review_resolved',JSON.stringify({previous,updated:structuredClone(row),note:note.trim(),authority:'local simulation only; no authenticated approval or delivery verification'}));
      return row;
    }
    act(id, action, outcome='', fail=false) {
      const r=this.records.find(x=>x.id===id); if(!r) throw Error('Unknown record.');
      if(r.holds.length)throw Error('Held: '+r.holds.join(', ')+'. '+r.recovery.join(' '));
      const transitions={schedule:{from:'new',to:'follow_up'},complete:{from:'follow_up',to:'done'}};
      const t=transitions[action];
      if (!t || r.state!==t.from) throw Error('Action does not match current state.');
      if (action==='complete' && !outcome.trim()) throw Error('Record an outcome before completion.');
      if (fail) {this.event(id,'action_failed',action+' failed in simulation; state unchanged.');return r;}
      r.state=t.to; if(action==='complete') r.outcome=outcome.trim(); this.event(id,action,action==='complete'?r.outcome:'Follow-up prepared locally. No message sent.'); return r;
    }
    snapshot() { return structuredClone({schema_version:1,synthetic_only:true,fields:this.fields,records:this.records,history:this.history}); }
    csv() {
      const cell=v=>{let s=String(v??'');if(/^[\s]*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
      const headers=['id',...this.fields.map(f=>f.key),'state','outcome','holds','permission','delivery_sent','acknowledged','draft'];
      return [headers,...this.records.map(r=>[r.id,...this.fields.map(f=>r.values[f.key]),r.state,r.outcome,r.holds.join(';'),r.permission,r.delivery.sent,r.delivery.acknowledged,r.draft])].map(row=>row.map(cell).join(',')).join('\r\n');
    }
  }
  const api={Workflow,defaultFields,validateFields};
  if(typeof module!=='undefined')module.exports=api; else root.WorkflowPilot=api;
})(globalThis);
