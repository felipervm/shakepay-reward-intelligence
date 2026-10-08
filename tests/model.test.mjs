import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {evaluate} from '../site/model-utils.js';
const cases=JSON.parse(readFileSync(new URL('../data/cases.json',import.meta.url)));
for(const c of cases)test(c.title,()=>{const result=evaluate(c.events,c.observed,c.as_of);assert.equal(result.expected_tier,c.expected);assert.equal(result.assessment,c.assessment);});
test('invalid money is an input error',()=>{for(const amount of ['','-1','1.001','NaN'])assert.throws(()=>evaluate([{date:'2026-10-01',kind:'payroll',settled:true,amount_cad:amount}],'Base','2026-10-08'));});
test('December carryover',()=>assert.equal(evaluate([{date:'2025-12-31',kind:'payroll',settled:true,amount_cad:'2000'}],'Blue','2026-01-01').expected_tier,'Blue'));
test('independent qualification paths',()=>assert.equal(evaluate([{date:'2026-10-01',kind:'payroll',settled:true,amount_cad:'150'},{date:'2026-10-01',kind:'exchange',settled:true,amount_cad:'50'}],'Base','2026-10-08').expected_tier,'Base'));
