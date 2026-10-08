import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {evaluate} from '../site/model-utils.js';
const cases=JSON.parse(readFileSync(new URL('../data/cases.json',import.meta.url)));
for(const c of cases)test(c.title,()=>{const result=evaluate(c.events,c.observed,c.as_of);assert.equal(result.expected_tier,c.expected);assert.equal(result.assessment,c.assessment);});
test('invalid money is an input error',()=>{for(const amount of ['','-1','1.001','NaN'])assert.throws(()=>evaluate([{date:'2026-10-01',kind:'payroll',settled:true,amount_cad:amount}],'Base','2026-10-08'));});
test('December carryover',()=>assert.equal(evaluate([{date:'2025-12-31',kind:'payroll',settled:true,amount_cad:'2000'}],'Blue','2026-01-01').expected_tier,'Blue'));
test('independent qualification paths',()=>assert.equal(evaluate([{date:'2026-10-01',kind:'payroll',settled:true,amount_cad:'150'},{date:'2026-10-01',kind:'exchange',settled:true,amount_cad:'50'}],'Base','2026-10-08').expected_tier,'Base'));

test('unrecognized category needs review',()=>{const r=evaluate([{date:'2026-10-01',kind:'new_payment_channel',settled:true,amount_cad:'2000'}],'Base','2026-10-08');assert.equal(r.assessment,'INCOMPLETE_DATA');assert.equal(r.mismatch,null);});
test('confirmed Blue cannot increase even with unknown activity',()=>{const r=evaluate([{date:'2026-10-01',kind:'payroll',settled:true,amount_cad:'2000'},{date:'2026-10-01',kind:'novel',settled:true,amount_cad:'2000'}],'Blue','2026-10-08');assert.equal(r.confirmed_floor,'Blue');assert.equal(r.potential_higher_tier,false);});

test('browser threshold constants agree with published JSON snapshot',()=>{
 const rules=JSON.parse(readFileSync(new URL('../rules/reward_status_v1.json',import.meta.url)));
 const source=readFileSync(new URL('../site/model-utils.js',import.meta.url),'utf8');
 const direct=rules.thresholds_cad.eligible_direct_deposit;
 const exchange=rules.thresholds_cad.eligible_exchange;
 for(const [threshold,expected] of [[direct.Blue,200000],[direct.Bright,20000],[exchange.Blue,100000],[exchange.Bright,10000]])
  assert.equal(threshold*100,expected);
 assert.match(source,/total\.direct>=200000\|\|total\.exchange>=100000/);
 assert.match(source,/total\.direct>=20000\|\|total\.exchange>=10000/);
});

test('missing effectiveness needs review',()=>{assert.equal(evaluate([{date:'2026-10-01',kind:'payroll',amount_cad:'2000'}],'Base','2026-10-08').assessment,'INCOMPLETE_DATA');});
test('small unresolved amount cannot reach a threshold',()=>{assert.equal(evaluate([{date:'2026-10-01',kind:'unknown',settled:true,amount_cad:'1'}],'Base','2026-10-08').potential_higher_tier,false);});
test('known floor discrepancy is not masked by unknown input',()=>{const r=evaluate([{date:'2026-10-01',kind:'payroll',settled:true,amount_cad:'2000'},{date:'2026-10-01',kind:'unknown',settled:true,amount_cad:'1'}],'Base','2026-10-08');assert.equal(r.assessment,'STATUS_REVIEW');assert.equal(r.mismatch,true);});
