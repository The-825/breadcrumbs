'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {Workflow}=require('./core.js');
// Six fictional acceptance scenarios.
const packet=[
 {case:1,id:'SYN-101',request:'Prepare invented review note',owner:'Review role',due:'2026-11-01'},
 {case:2,id:'SYN-102',request:'Review invented summary',owner:'Review role',due:''},
 {case:3,id:'SYN-103',request:'Keep the fictional note private; also publish it publicly.',owner:'Review role',due:'2026-11-01'},
 {case:4,id:'SYN-101',request:'Prepare invented review note',owner:'Review role',due:'2026-11-01'},
 {case:5,id:'SYN-105',request:'Send invented note externally; no send authorization provided.',owner:'Review role',due:'2026-11-01'},
 {case:6,id:'SYN-106',request:'Previously prepared fictional follow-up; no delivery acknowledgment supplied.',owner:'Review role',due:'2026-11-01'}
];
const w=new Workflow();const results=[];
w.intake(packet[0].id,packet[0]);w.act('SYN-101','schedule');w.act('SYN-101','complete','Invented note prepared locally');
assert.equal(w.records[0].state,'done');
results.push({case:1,expected:'Owned local follow-up, explicit outcome and history.',actual:'new -> follow_up -> done; local outcome and history retained.',verdict:'pass_local_simulation'});
w.intake(packet[1].id,packet[1]);assert.equal(w.records.find(r=>r.id==='SYN-102').values.due,'');assert.deepEqual(w.records.find(r=>r.id==='SYN-102').holds,['missing_date']);assert.throws(()=>w.act('SYN-102','schedule'),/Held/);w.clarifyDate('SYN-102');w.clarifyDate('SYN-102');assert.equal(w.history.filter(e=>e.record_id==='SYN-102'&&e.type==='clarification_prepared').length,1);
results.push({case:2,expected:'Preserve unknown date, retain request, clarify once and hold as needed.',actual:'Request retained with empty/unknown date, held state and one clarification recovery instruction; scheduling blocked.',verdict:'pass_local_simulation'});
w.intake(packet[2].id,packet[2],{conflict:true});assert.equal(w.records.find(r=>r.id==='SYN-103').state,'held');assert.throws(()=>w.act('SYN-103','schedule'),/conflicting_instructions/);
results.push({case:3,expected:'Flag conflict and hold dependent action.',actual:'Human-marked conflict retained; dependent scheduling blocked. No automatic prose detection claimed.',verdict:'pass_local_simulation'});
w.intake(packet[3].id,packet[3]);assert.equal(w.records.filter(r=>r.id==='SYN-101').length,1);
assert.equal(w.history.at(-1).type,'duplicate_ignored');
results.push({case:4,expected:'Account for repeat without duplicate record or downstream effect.',actual:'Existing record reused; duplicate_ignored event retained. No external effect exists in this pilot.',verdict:'pass_local_simulation'});
w.intake(packet[4].id,packet[4],{externalAction:true});w.prepareDraft('SYN-105');assert.equal(w.records.find(r=>r.id==='SYN-105').permission,'missing');assert.equal(w.records.find(r=>r.id==='SYN-105').state,'held');assert.match(w.records.find(r=>r.id==='SYN-105').draft,/UNSENT/);assert.throws(()=>w.act('SYN-105','schedule'),/missing_permission/);
results.push({case:5,expected:'Unsent draft, explicit missing permission and separate approval/send status.',actual:'Unsent draft prepared while missing_permission remains held; simulated permission and not_connected delivery are separate.',verdict:'pass_local_simulation'});
w.intake(packet[5].id,packet[5],{preparedFollowUp:true,ackMissing:true});const prior=w.records.find(r=>r.id==='SYN-106');assert.equal(prior.delivery.prepared,true);assert.equal(prior.delivery.acknowledged,'unknown');assert.equal(prior.state,'held');assert.throws(()=>w.prepareDraft('SYN-106'),/Missing acknowledgment/);assert.throws(()=>w.act('SYN-106','schedule'),/missing_delivery_acknowledgment/);
results.push({case:6,expected:'Separate prepared/delivered/acknowledged and recover by checking evidence, not resending.',actual:'Prepared state retained; delivery not_connected, acknowledgment unknown; held reconciliation route blocks a new draft or scheduling.',verdict:'pass_local_simulation'});
assert.equal(results.length,6);
const report={synthetic_only:true,scenario_source:'Six-case fictional local acceptance packet',packet_scope:'Fictional fixture; independent consumer usability remains unverified',results,totals:{requests:6,pass_local_simulation:6,partial_gap:0,fail_gap:0},manual_baseline_run:false,elapsed_savings:'unknown',tokens:'unknown',service_cost:'unknown',external_actions:0,model_provider_calls:0,snapshot:w.snapshot()};
fs.writeFileSync('six-case-packet.json',JSON.stringify(packet,null,2)+'\n');
fs.writeFileSync('six-case-results.json',JSON.stringify(report,null,2)+'\n');
console.log('PASS: all six local synthetic cases accounted for. Human-marked conflicts, no executor; no independent runtime or savings claim.');
