export const tiers=['Base','Bright','Blue'];
const direct=new Set(['payroll','pension','government_benefit']);
const excluded=new Set(['etransfer','internal_transfer','crypto_deposit']);
const known=new Set([...direct,...excluded,'exchange']);
export function cents(value){
 const s=String(value).trim();
 if(!/^\d+(?:\.\d{1,2})?$/.test(s))throw new Error('Enter a nonnegative CAD amount with at most two decimal places.');
 const [whole,fraction='']=s.split('.');const n=Number(whole)*100+Number(fraction.padEnd(2,'0'));
 if(!Number.isSafeInteger(n)||n>100000000)throw new Error('Use an amount from CAD 0 to 1,000,000 for this demo.');
 return n;
}
function validDate(value){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(value)||Number(value.slice(0,4))<1||Number.isNaN(Date.parse(value+'T12:00:00Z'))||new Date(value+'T12:00:00Z').toISOString().slice(0,10)!==value)throw new Error('Choose a valid calendar date.');
 return value;
}
export function evaluate(events,observed,asOf,computeBounds=true){
 if(!Array.isArray(events))throw new Error('Events must be an array.');
 validDate(asOf);if(!tiers.includes(observed))throw new Error('Choose a supported observed status.');
 const date=new Date(asOf+'T12:00:00Z');date.setUTCDate(1);date.setUTCMonth(date.getUTCMonth()-1);
 const months=[asOf.slice(0,7),date.toISOString().slice(0,7)];const totals={};let uncertain=false;
 const details=events.map(event=>{
  if(!event||typeof event.kind!=='string')throw new Error('Every event requires an activity.');
  for(const field of ['settled','classification_confirmed'])if(event[field]!=null&&typeof event[field]!=='boolean')throw new Error(field+' must be boolean or null; normalize CSV values first.');
  validDate(event.date);const amount=cents(event.amount_cad);let contribution=0,reason='Eligible',category=null;
  if(event.date>asOf)reason='After audit date';
  else if(!months.includes(event.date.slice(0,7)))reason='Outside carryover window';
  else if(event.settled==null){reason='Effectiveness needs review';uncertain=true;}
  else if(event.settled!==true)reason='Not effective in this scenario';
  else if(!known.has(event.kind)||(event.classification_confirmed!==undefined&&event.classification_confirmed!==true)){reason='Classification needs review';uncertain=true;}
  else if(direct.has(event.kind)||event.kind==='exchange'){
   category=event.kind==='exchange'?'exchange':'direct';contribution=amount;
   const month=event.date.slice(0,7);totals[month]??={direct:0,exchange:0};totals[month][category]+=amount;
  }else reason='Excluded from status qualification';
  return {...event,amount_cents:amount,contribution_cents:contribution,reason};
 });
 let level=0;for(const total of Object.values(totals))level=Math.max(level,total.direct>=200000||total.exchange>=100000?2:total.direct>=20000||total.exchange>=10000?1:0);
 const expected=tiers[level];let upper=expected;
 if(uncertain&&computeBounds)for(const kind of ['payroll','exchange']){
  const optimistic=events.map(e=>({...e,settled:e.settled==null?true:e.settled,...(!known.has(e.kind)||(e.classification_confirmed!==undefined&&e.classification_confirmed!==true)?{kind,classification_confirmed:true}:{})}));
  const candidate=evaluate(optimistic,observed,asOf,false).expected_tier;
  if(tiers.indexOf(candidate)>tiers.indexOf(upper))upper=candidate;
 }
 const different=tiers.indexOf(observed)<level||tiers.indexOf(observed)>tiers.indexOf(upper);
 const assessment=different?'STATUS_REVIEW':uncertain?'INCOMPLETE_DATA':'MATCH';
 return {expected_tier:expected,confirmed_floor:expected,possible_ceiling:upper,has_unresolved_events:uncertain,potential_higher_tier:tiers.indexOf(upper)>level,assessment,mismatch:different?true:uncertain&&upper!==expected?null:false,events:details};
}
