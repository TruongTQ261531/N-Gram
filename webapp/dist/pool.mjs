// Safe reusable top-k pool. Interval/dominance/partition ideas are established.
// This browser implementation is separate from the compact-channel Python study.
export const POOL_VERSION='finite-query-pool-web-v1';
export function matchFiniteQuery(forms,budget,input){
 const words=String(input).normalize('NFC').toLowerCase().trim().split(/\s+/u).filter(Boolean),memo=new Set();
 function search(t,p,cost,chosen){if(t===forms.length)return p===words.length?chosen:null;const key=[t,p,cost].join(':');if(memo.has(key))return null;memo.add(key);for(let a=0;a<forms[t].length;a++){const nextCost=cost+(a!==0);if(nextCost>budget)continue;const w=forms[t][a].text.split(/\s+/u).filter(Boolean);if(w.every((s,i)=>words[p+i]===s)){const result=search(t+1,p+w.length,nextCost,[...chosen,a]);if(result)return result}}return null}
 return search(0,0,0,[]);
}
export function subsetIndex(I,pool){
 const mapping=new Map(pool.map((j,i)=>[j,i])),postings=new Map();for(const [g,values] of I.postings){const selected=values.flatMap(([j,w])=>mapping.has(j)?[[mapping.get(j),w]]:[]);if(selected.length)postings.set(g,selected)}
 return {n:pool.length,docs:pool.map(j=>I.docs[j]),weights:pool.map(j=>I.weights[j]),postings,version:I.version,maxWeight:I.maxWeight};
}
const top=(a,b)=>a.sort((x,y)=>y-x).slice(0,b).reduce((s,x)=>s+Math.max(0,x),0);
function envelopes(F,b,fixed){const n=F[0][0].length,L=Array(n).fill(0),U=Array(n).fill(0),remaining=b-[...fixed.values()].filter(v=>v!==0).length;for(let j=0;j<n;j++){let base=0;const up=[],down=[];F.forEach((f,t)=>{if(fixed.has(t))base+=f[fixed.get(t)][j];else{base+=f[0][j];let lo=f[0][j],hi=lo;for(const a of f){lo=Math.min(lo,a[j]);hi=Math.max(hi,a[j])}up.push(hi-f[0][j]);down.push(f[0][j]-lo)}});L[j]=base-top(down,remaining);U[j]=base+top(up,remaining)}return {L,U}}
function interval(F,b,k,fixed=new Map()){const {L,U}=envelopes(F,b,fixed),threshold=L.slice().sort((a,b)=>b-a)[k-1];return U.flatMap((v,j)=>v>=threshold?[j]:[])}
export function finitePool(F,b,k=10,{maxLeaves=96,maxMs=450}={}){
 const start=performance.now(),n=F[0][0].length;k=Math.min(k,n);if(!F.length||!Number.isInteger(b)||b<0||!Number.isInteger(k)||k<1)throw Error('Invalid pool input');
 const independent=interval(F,b,k),raw=Array(n).fill(0);for(const f of F)for(let j=0;j<n;j++)raw[j]+=f[0][j];const order=Array.from({length:n},(_,j)=>j).sort((a,b)=>raw[b]-raw[a]||a-b),anchors=order.slice(0,Math.min(n,Math.max(20,2*k))),dominators=Array(n).fill(0);let coupled=independent.slice(),fallback=false;
 for(const anchor of anchors){for(const j of coupled){let base=0;const gains=[];for(const f of F){const d0=f[0][j]-f[0][anchor];base+=d0;let best=d0;for(const a of f)best=Math.max(best,a[j]-a[anchor]);gains.push(best-d0)}if(base+top(gains,b)<0)dominators[j]++}coupled=coupled.filter(j=>dominators[j]<k);if(performance.now()-start>maxMs){fallback=true;break}}
 const priority=F.map((f,t)=>{let range=0;for(let j=0;j<n;j++){let lo=f[0][j],hi=lo;for(const a of f){lo=Math.min(lo,a[j]);hi=Math.max(hi,a[j])}range=Math.max(range,hi-lo)}return {t,range}}).sort((a,b)=>b.range-a.range||a.t-b.t).map(x=>x.t),selected=[];
 const countLeaves=ts=>{let count=0;function walk(d,cost){if(d===ts.length){count++;return}for(let a=0;a<F[ts[d]].length;a++)if(cost+(a!==0)<=b)walk(d+1,cost+(a!==0))}walk(0,0);return count};
 for(const t of priority.slice(0,2)){if(countLeaves([...selected,t])<=maxLeaves)selected.push(t);else break}
 const leaves=[],keep=new Set();let completed=!fallback;
 function walk(d,cost,fixed){if(!completed)return;if(performance.now()-start>maxMs){completed=false;return}if(d===selected.length){const allowed=new Set(interval(F,b,k,fixed)),pool=coupled.filter(j=>allowed.has(j));pool.forEach(j=>keep.add(j));leaves.push({fixed:[...fixed],pool});return}const t=selected[d];for(let a=0;a<F[t].length;a++)if(cost+(a!==0)<=b){fixed.set(t,a);walk(d+1,cost+(a!==0),fixed)}fixed.delete(t)}
 if(completed)walk(0,0,new Map());const pool=completed?[...keep].sort((a,b)=>a-b):coupled;
 return {version:POOL_VERSION,k,pool,independent,coupled,anchors,splitTokens:selected,leaves:completed?leaves:[],status:completed?'conditional_cover':'safe_root_fallback',scope:'All kth-score ties included; fixed corpus/scorer/base query/channel/budget; no relevance guarantee.',elapsedMs:performance.now()-start};
}
