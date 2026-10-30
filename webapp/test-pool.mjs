import assert from 'node:assert/strict';
import {finitePool,matchFiniteQuery,subsetIndex} from './dist/pool.mjs';
import {buildIndex,certify,scores} from './dist/engine.mjs';
let seed=30731;const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n};
let checked=0;
for(let trial=0;trial<100;trial++){
 const F=Array.from({length:4},()=>Array.from({length:1+rand(4)},()=>Array.from({length:9},()=>rand(25))));
 for(const b of [0,1,2])for(const k of [1,3]){
  const p=finitePool(F,b,k,{maxMs:10000});const truth=new Set();
  function visit(t,cost,z){if(t===F.length){const cut=z.slice().sort((a,b)=>b-a)[k-1];z.forEach((s,j)=>{if(s>=cut)truth.add(j)});return}F[t].forEach((f,a)=>{if(cost+(a!==0)<=b)visit(t+1,cost+(a!==0),z.map((v,j)=>v+f[j]))})}visit(0,0,Array(9).fill(0));for(const j of truth)assert(p.pool.includes(j));for(const j of p.pool)assert(p.coupled.includes(j));checked++;
 }
}
const zero=finitePool([Array.from({length:4},()=>Array(12).fill(0))],2,5);assert.equal(zero.pool.length,12);
const fallback=finitePool([[[1,0,2],[0,2,0]],[[1,0,2],[0,2,0]]],2,1,{maxMs:-1});assert.equal(fallback.status,'safe_root_fallback');
const I=buildIndex([{id:'a',text:'retrieval cache search'},{id:'b',text:'query correction certificate'},{id:'c',text:'tìm kiếm'}]);
const r=certify(I,'retrieval cache',{audit:true,budget:1,enumeration:{collect:true}}),p=finitePool(r.factorScores,1,2,{maxMs:10000});
const cache=subsetIndex(I,p.pool);
for(const state of r.exactStateRecords){const q=r.forms.map((f,t)=>f[state.choices[t]].text).join(' '),z=Array.from(scores(I,q)),cut=z.slice().sort((a,b)=>b-a)[1],gold=z.flatMap((v,j)=>v>=cut?[I.docs[j].id]:[]);for(let j=0;j<z.length;j++)if(z[j]>=cut)assert(p.pool.includes(j));assert(matchFiniteQuery(r.forms,1,q));const local=Array.from(scores(cache,q)),threshold=local.slice().sort((a,b)=>b-a)[1];assert.deepEqual(local.flatMap((v,j)=>v>=threshold?[cache.docs[j].id]:[]),gold)}
assert.equal(matchFiniteQuery(r.forms,1,'totally outside the channel'),null);
assert.deepEqual(matchFiniteQuery([[{text:'a'},{text:''}],[{text:'search'}]],1,'search'),[1,0]);
console.log(JSON.stringify({randomCorpusBudgetKCases:checked,ties:true,safeResourceFallback:true,allStateFullQueryReencoding:true,cachedFullTopKEqual:true,outOfLatticeRejected:true,emptyTokenDeletion:true}));
