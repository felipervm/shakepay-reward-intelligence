import {evaluate} from './model-utils.js?v=20261008-audit4';
const scenario=document.getElementById('scenario'),asOf=document.getElementById('asOf'),observed=document.getElementById('observed'),eventsEl=document.getElementById('events');
const kinds={payroll:'Payroll',pension:'Pension',government_benefit:'Supported government benefit',exchange:'Exchange activity',etransfer:'e-Transfer',internal_transfer:'Internal transfer',crypto_deposit:'Crypto deposit',unknown:'Unconfirmed classification'};
let cases=[],events=[];let original='';
const money=n=>new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD'}).format(n/100);
function snapshot(){return JSON.stringify({events,as_of:asOf.value,observed:observed.value});}
function renderEvents(){eventsEl.replaceChildren();events.forEach((event,i)=>{
 const block=document.createElement('div');block.className='event';
 const top=document.createElement('div');top.className='eventTop';top.textContent='EVENT '+(i+1);
 const remove=document.createElement('button');remove.type='button';remove.className='remove';remove.textContent='Remove';remove.setAttribute('aria-label','Remove event '+(i+1));remove.addEventListener('click',()=>{events.splice(i,1);renderEvents();update();document.getElementById('addEvent').focus();});top.append(remove);block.append(top);
 const fields=document.createElement('div');fields.className='eventFields';
 for(const [key,label,type] of [['date','Effective date','date'],['amount_cad','Amount (CAD)','text'],['kind','Activity','select']]){
  const group=document.createElement('div');const lab=document.createElement('label');lab.htmlFor=key+'-'+i;lab.textContent=label+' — event '+(i+1);
  const input=document.createElement(type==='select'?'select':'input');input.id=lab.htmlFor;
  if(type==='select'){for(const [value,text] of Object.entries(kinds)){const opt=document.createElement('option');opt.value=value;opt.textContent=text;input.append(opt);}}
  else{input.type=type;input.required=true;if(key==='amount_cad')input.inputMode='decimal';}
  input.value=event[key];input.addEventListener('input',()=>{event[key]=input.value;if(key==='kind')event.classification_confirmed=input.value!=='unknown';update();});group.append(lab,input);fields.append(group);
 }
 block.append(fields);eventsEl.append(block);
});}
function update(){const error=document.getElementById('inputError');try{
 const result=evaluate(events,observed.value,asOf.value);error.hidden=true;
 document.getElementById('statusName').textContent=result.assessment==='INCOMPLETE_DATA'?'Needs information review':result.expected_tier;
 document.getElementById('assessment').textContent={MATCH:'MATCH IN THIS SCENARIO',STATUS_REVIEW:'STATUS DIFFERENCE — REVIEW',INCOMPLETE_DATA:'INSUFFICIENT INFORMATION'}[result.assessment];
 const selected=cases.find(c=>c.id===scenario.value);const unchanged=snapshot()===original;
 document.getElementById('explanation').textContent=unchanged?selected.explanation:result.assessment==='INCOMPLETE_DATA'?'The tier from confirmed events is '+result.confirmed_floor+'. '+(result.potential_higher_tier?'Unresolved information could increase that tier.':'The confirmed tier cannot increase, but the incomplete input still requires review.'):result.assessment==='STATUS_REVIEW'?'The simulated status '+observed.value+' falls outside the supported tier range ('+result.confirmed_floor+' to '+result.possible_ceiling+'). Review the inputs and status history; this is not a production diagnosis.':'Confirmed effective events and one-month carryover indicate '+result.expected_tier+'. The simulated observed status agrees.';
 document.getElementById('nextStep').textContent=unchanged?selected.next_step:result.assessment==='INCOMPLETE_DATA'?'Confirm missing effectiveness or payment classification before closing the review.':result.assessment==='STATUS_REVIEW'?'Review effective dates, policy and status history before deciding on a correction.':'Explain the listed contributions and qualification window. No difference in this scenario.';
 const tbody=document.getElementById('contributions');tbody.replaceChildren();for(const event of result.events){const tr=document.createElement('tr');for(const value of [event.date,kinds[event.kind],money(event.amount_cents),money(event.contribution_cents),event.reason]){const td=document.createElement('td');td.textContent=value;tr.append(td);}tbody.append(tr);}
 }catch(e){error.textContent=e.message;error.hidden=false;document.getElementById('statusName').textContent='Check the inputs';document.getElementById('assessment').textContent='NO RESULT CALCULATED';document.getElementById('explanation').textContent='Correct the highlighted input message to continue.';document.getElementById('nextStep').textContent='No eligibility conclusion is shown for invalid input.';document.getElementById('contributions').replaceChildren();}}
function loadCase(){const c=cases.find(c=>c.id===scenario.value);events=structuredClone(c.events);asOf.value=c.as_of;observed.value=c.observed;original=snapshot();renderEvents();update();}
scenario.addEventListener('change',loadCase);asOf.addEventListener('input',update);observed.addEventListener('change',update);
document.getElementById('addEvent').addEventListener('click',()=>{if(events.length>=10){const err=document.getElementById('inputError');err.textContent='Use up to ten events in this demo.';err.hidden=false;return;}events.push({kind:'payroll',amount_cad:'0.00',date:asOf.value,settled:true,classification_confirmed:true});renderEvents();update();document.getElementById('date-'+(events.length-1)).focus();});
try{const response=await fetch('data/cases.json?v=20261008-audit4');if(!response.ok)throw new Error('Scenario data could not load.');cases=await response.json();for(const c of cases){const opt=document.createElement('option');opt.value=c.id;opt.textContent=c.title;scenario.append(opt);}loadCase();}catch(e){document.getElementById('statusName').textContent='Demo unavailable';document.getElementById('explanation').textContent='The scenario file could not load. Open the method report for all examples.';}
