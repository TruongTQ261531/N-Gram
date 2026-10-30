import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import {gzipSync} from 'node:zlib';
import {buildIndex,certify,exactRank,normalize,VERSION,LIMITS} from '../webapp/dist/engine.mjs';
const ROOT=path.resolve(import.meta.dirname,'..'),D=path.join(ROOT,'webapp/dist/data'),R=path.join(ROOT,'application_study/results');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=b=>createHash('sha256').update(b).digest('hex');
fs.mkdirSync(R,{recursive:true});const freeze=read(path.join(ROOT,'application_study/freeze.json'));
for(const [p,h] of Object.entries(freeze.files))if(sha(fs.readFileSync(path.join(ROOT,p)))!==h)throw Error('Frozen source changed: '+p);
if(fs.existsSync(path.join(R,'audit-set.jsonl.gz')))throw Error('Refuse to overwrite original audit records.');
const data=read(path.join(D,'demo-corpus.json')),queries=read(path.join(D,'query-seeds.json')),dictionary=read(path.join(D,'typos.json')),license=read(path.join(D,'data-license.json')),I=buildIndex(data.documents),weights=I.weights.map(w=>[...w]);
const modelHash=sha(JSON.stringify({version:VERSION,weights})),corpusHash=sha(JSON.stringify(I.docs));const lines=[];let totalStates=0;
lines.push(JSON.stringify({recordType:'manifest',schema:'ngramlab.auditset.v0.1',engine:VERSION,corpus:I.docs,weights,modelHash,corpusHash,sourceFreeze:freeze,provenance:license,synthetic:true,humanRelevanceLabels:0,splitRule:'SHA256 family modulo5; language, query siblings, channels and budgets share family split.'}));
const summaries=[];
for(const seed of queries){const channels=seed.language==='en'?['keyboard','curated','mixed']:['keyboard','accents','mixed'];const split=parseInt(sha(seed.family).slice(0,8),16)%5===0?'evaluation':'development';
for(const channel of channels)for(const budget of [1,2]){
 const r=certify(I,seed.text,{budget,channel,dictionary,audit:true,enumeration:{maxStates:0}}),F=r.factorScores,ref=r.referenceIndex;
 const oracle=exactRank(F,ref,budget,{maxStates:200000,maxCells:10000000,collect:true});
 if(oracle.status==='exact'&&oracle.rank>r.bounds.proposed)throw Error('Certificate contradicted by exhaustive oracle');
 const productionEnumerates=oracle.status==='exact'&&oracle.states<=LIMITS.enumStates&&oracle.states*I.n<=LIMITS.enumCells;
 const deployedDepth=Math.min(r.bounds.proposed,productionEnumerates?oracle.rank:Infinity);totalStates+=oracle.status==='exact'?oracle.states:0;
 const row={...r,recordType:'case',id:seed.id+'|'+channel+'|B'+budget,family:seed.family,split,language:seed.language,sourceQueryId:seed.id,sourceAnchor:seed.source_anchor,semanticRelevanceLabel:null,synthetic:true,modelHash,corpusHash,
  oracle,productionEnumerates,deployedDepth,sourceSeed:seed,corpusType:'authored-synthetic'};
 lines.push(JSON.stringify(row));summaries.push({id:row.id,family:row.family,split,language:row.language,channel,budget,states:row.lattice.states,oracleStatus:oracle.status,gold:oracle.rank??null,pair:r.bounds.pairwise,cover:r.bounds.discrete,certificate:r.bounds.proposed,deployed:deployedDepth,productionEnumerates,graphChecks:r.proof.checks.length,graphUnknown:r.proof.checks.filter(x=>x.method==='resource_unknown').length,elapsedMs:r.elapsedMs,identityLattice:row.lattice.states===1});
 console.log(summaries.length,seed.id,channel,budget,'states',row.lattice.states,'upper',r.bounds.proposed,'gold',oracle.rank??oracle.status);
}}
const text=lines.join('\n')+'\n',gz=gzipSync(text,{level:6});fs.writeFileSync(path.join(R,'audit-set.jsonl.gz'),gz);fs.writeFileSync(path.join(D,'audit-set.jsonl.gz'),gz);
fs.writeFileSync(path.join(R,'query-results.json'),JSON.stringify(summaries,null,2));
const manifest={cases:summaries.length,documents:I.n,querySeeds:queries.length,families:new Set(queries.map(q=>q.family)).size,exactCases:summaries.filter(x=>x.oracleStatus==='exact').length,totalEnumeratedStates:totalStates,modelHash,corpusHash,uncompressedSha256:sha(text),gzipSha256:sha(gz),bytes:gz.length,synthetic:true,noNewHumanLabels:true};
fs.writeFileSync(path.join(R,'dataset-manifest.json'),JSON.stringify(manifest,null,2));fs.writeFileSync(path.join(D,'audit-summary.json'),JSON.stringify(manifest,null,2));console.log('COMPLETE',JSON.stringify(manifest));
