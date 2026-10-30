import {buildIndex,certify} from './engine.mjs';
let index,dictionary,modelHash,corpusHash;
async function hash(x){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(x)));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}
function attach(result){return {...result,modelHash,corpusHash,computedAt:new Date().toISOString()}}
self.onmessage=async({data:m})=>{try{
 if(m.type==='init'){index=buildIndex(m.documents);dictionary=m.dictionary||{};corpusHash=await hash(index.docs);modelHash=await hash({version:index.version,weights:index.weights.map(w=>[...w])});postMessage({type:'ready',documents:index.n,features:index.features,modelHash,corpusHash})}
 else if(m.type==='query'){if(!index)throw Error('Chỉ mục chưa sẵn sàng.');const result=attach(certify(index,m.query,{...m.options,dictionary,audit:true,enumeration:{collect:true}}));postMessage({type:'result',result})}
 else if(m.type==='batch'){if(!index)throw Error('Chỉ mục chưa sẵn sàng.');const results=[];for(let i=0;i<m.queries.length;i++){const result=attach(certify(index,m.queries[i],{...m.options,dictionary,audit:true,enumeration:{collect:true}}));results.push(result);postMessage({type:'progress',done:i+1,total:m.queries.length});await new Promise(r=>setTimeout(r,0))}postMessage({type:'batch',results})}
 else if(m.type==='bundle')postMessage({type:'bundle',kind:m.kind,requestId:m.requestId,corpus:index.docs,weights:index.weights.map(w=>[...w]),corpusHash,modelHash});
}catch(e){postMessage({type:'error',message:e.message||String(e)})}};
