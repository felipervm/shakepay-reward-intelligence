export const tiers=['Base','Bright','Blue'];
const direct=new Set(['payroll','pension','government_benefit']);
export function cents(value){
 const s=String(value).trim();
 if(!/^\d+(?:\.\d{1,2})?$/.test(s))throw new Error('Enter a nonnegative CAD amount with at most two decimal places.');
 const [whole,fraction='']=s.split('.');const n=Number(whole)*100+Number(fraction.padEnd(2,'0'));
 if(!Number.isSafeInteger(n)||n>100000000)throw new Error('Use an amount from CAD 0 to 1,000,000 for this demo.');
 return n;
}
function validDate(value){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(value)||Number.isNaN(Date.parse(value+'T12:00:00Z'))||new Date(value+'T12:00:00Z').toISOString().slice(0,10)!==value)throw new Error('Choose a valid calendar date.');
 return value;
}
export function evaluate(events,observed,asOf){
 validDate(asOf);if(!tiers.includes(observed))throw new Error('Choose a supported observed status.');
 const date=new Date(asOf+'T12:00:00Z');date.setUTCDate(1);date.setUTCMonth(date.getUTCMonth()-1);
 const months=[asOf.slice(0,7),date.toISOString().slice(0,7)];const totals={};let uncertain=false;
 const details=events.map(event=>{
  validDate(event.date);const amount=cents(event.amount_cad);let contribution=0,reason='Eligible',category=null;
  if(event.date>asOf)reason='After audit date';
  else if(!months.includes(event.date.slice(0,7)))reason='Outside carryover window';
  else if(event.settled!==true)reason='Not effective in this scenario';
  else if(event.kind==='unknown'||event.classification_confirmed===false){reason='Classification needs review';uncertain=true;}
  else if(direct.has(event.kind)||event.kind==='exchange'){
   category=event.kind==='exchange'?'exchange':'direct';contribution=amount;
   const month=event.date.slice(0,7);totals[month]??={direct:0,exchange:0};totals[month][category]+=amount;
  }else reason='Excluded from status qualification';
  return {...event,amount_cents:amount,contribution_cents:contribution,reason};
 });
 let level=0;for(const total of Object.values(totals))level=Math.max(level,total.direct>=200000||total.exchange>=100000?2:total.direct>=20000||total.exchange>=10000?1:0);
 const expected=tiers[level];const assessment=uncertain?'INCOMPLETE_DATA':expected!==observed?'STATUS_REVIEW':'MATCH';
 return {expected_tier:expected,assessment,mismatch:uncertain?null:expected!==observed,events:details};
}
