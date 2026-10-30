// Browser-local fixed-point ranker. This is NOT the frozen round3 float scorer.
export const VERSION='ngramlab-fixedpoint-v1';
export const SCALE=1_000_000;
export const LIMITS={documents:500,characters:500_000,tokens:16,tokenCodepoints:64,variants:18000,front:1200,points:20000,checks:120,candidates:80,enumStates:5000,enumCells:2_000_000};
export function normalize(s){return String(s).normalize('NFC').toLowerCase().trim().replace(/\s+/gu,' ')}
export function grams(text){const out=new Map();for(const token of normalize(text).split(' ').filter(Boolean)){const t=Array.from(' '+token+' ');for(const n of [3,4,5])for(let i=0;i+n<=t.length;i++){const g=t.slice(i,i+n).join('');out.set(g,(out.get(g)||0)+1)}}return out}
const coords=new Map();[['qwertyuiop',0],['asdfghjkl',.3],['zxcvbnm',.7]].forEach(([s,off],y)=>Array.from(s).forEach((c,x)=>coords.set(c,[x+off,y])));
const neighbors=new Map([...coords].map(([c,[a,b]])=>[c,[...coords].filter(([k,[x,y]])=>k!==c&&(x-a)**2+(y-b)**2<=1.6**2).map(([k])=>k).sort()]));
const strip=s=>s.normalize('NFD').replace(/\p{M}/gu,'').replace(/đ/gu,'d');
export function alternatives(token,channel='keyboard',dictionary={}){
 const found=new Map([[token,{op:'raw',sources:[]}]]);const add=(s,op)=>{if(s===token)return;if(!found.has(s))found.set(s,op)};
 const chars=Array.from(token),join=a=>a.join('');
 if(channel==='keyboard'||channel==='mixed')chars.forEach((c,i)=>{add(join([...chars.slice(0,i),...chars.slice(i+1)]),{op:'delete',position:i});add(join([...chars.slice(0,i),c,...chars.slice(i)]),{op:'repeat',position:i});for(const n of neighbors.get(c)||[])add(join([...chars.slice(0,i),n,...chars.slice(i+1)]),{op:'keyboard',position:i,replacement:n});if(i+1<chars.length){const z=chars.slice();[z[i],z[i+1]]=[z[i+1],z[i]];add(join(z),{op:'swap',position:i})}});
 if(channel==='accents'||channel==='mixed')add(strip(token),{op:'strip_diacritics',source:'declared deterministic token transform'});
 if(channel==='curated'||channel==='mixed')for(const s of dictionary[token]||[])add(normalize(s),{op:'curated_spelling',source:'codespell dictionary; see data-license.json'});
 return [token,...[...found.keys()].filter(s=>s!==token).sort()].map(text=>({text,...found.get(text)}));
}
export function buildIndex(documents,{allowLarge=false}={}){
 if(!Array.isArray(documents)||!documents.length)throw Error('Corpus phải có ít nhất một tài liệu.');
 if(!allowLarge&&documents.length>LIMITS.documents)throw Error('Bản web hỗ trợ tối đa '+LIMITS.documents+' tài liệu.');
 const docs=documents.map((d,i)=>({id:String(d.id??i+1),title:String(d.title||''),text:String(d.text||'')}));
 if(new Set(docs.map(d=>d.id)).size!==docs.length)throw Error('ID tài liệu bị trùng.');
 if(docs.some(d=>!(d.title+' '+d.text).trim()))throw Error('Có tài liệu rỗng.');
 if(!allowLarge&&docs.reduce((s,d)=>s+d.text.length+d.title.length,0)>LIMITS.characters)throw Error('Corpus vượt giới hạn 500.000 ký tự.');
 docs.sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 const counts=docs.map(d=>grams(d.title+' '+d.text)),lengths=counts.map(c=>[...c.values()].reduce((s,x)=>s+x,0)),avg=lengths.reduce((s,x)=>s+x,0)/docs.length,df=new Map();
 for(const c of counts)for(const g of c.keys())df.set(g,(df.get(g)||0)+1);
 const weights=counts.map((c,i)=>new Map([...c].map(([g,f])=>[g,Math.round(SCALE*Math.log1p((docs.length-df.get(g)+.5)/(df.get(g)+.5))*2.2*f/(f+1.2*(.25+.75*lengths[i]/Math.max(avg,1e-30))))])));
 const postings=new Map();let maxWeight=0;weights.forEach((w,i)=>{for(const [g,v] of w){if(v>maxWeight)maxWeight=v;if(!postings.has(g))postings.set(g,[]);postings.get(g).push([i,v])}});
 return {docs,weights,postings,maxWeight,features:df.size,n:docs.length,version:VERSION};
}
export function scores(I,text){const a=new Float64Array(I.n);for(const [g,c] of grams(text))for(const [j,w] of I.postings.get(g)||[])a[j]+=c*w;return a}
export function ranking(I,s){return Array.from({length:I.n},(_,i)=>i).sort((a,b)=>s[b]-s[a]||(I.docs[a].id<I.docs[b].id?-1:I.docs[a].id>I.docs[b].id?1:0))}
const top=(values,b)=>values.sort((x,y)=>y-x).slice(0,b).reduce((s,v)=>s+Math.max(0,v),0);
export function stateCount(forms,b){const c=Array(b+1).fill(0);c[0]=1;for(const f of forms)for(let j=b;j>0;j--)c[j]+=c[j-1]*(f.length-1);return c.reduce((s,v)=>s+v,0)}
function pareto(points){points.sort((a,b)=>b[0]-a[0]||b[1]-a[1]);const r=[];let best=-Infinity;for(const p of points)if(p[1]>best){r.push(p);best=p[1]}return r}
function pairConflict(F,r,j,k,b,caps){
 let raw=0;const gains=[],D=[];
 for(const f of F){const d=f.map(v=>[v[j]-v[r],v[k]-v[r]]);D.push(d);const z=d[0][0]+d[0][1];raw+=z;gains.push(Math.max(...d.map(p=>p[0]+p[1]))-z)}
 const support=raw+top(gains,b);if(support<0)return {incompatible:true,method:'integer_support',upper:support};
 let front=Array.from({length:b+1},(_,i)=>i?[]:[[0,0]]),peak=1;
 for(const states of D){const next=[];for(let cost=0;cost<=b;cost++){
  if(front[cost].length+(cost?front[cost-1].length*(states.length-1):0)>caps.points)return {incompatible:false,method:'resource_unknown',peak};
  const p=front[cost].map(v=>[v[0]+states[0][0],v[1]+states[0][1]]);
  if(cost)for(const v of front[cost-1])for(const s of states.slice(1))p.push([v[0]+s[0],v[1]+s[1]]);
  const keep=pareto(p);peak=Math.max(peak,keep.length);if(keep.length>caps.front)return {incompatible:false,method:'resource_unknown',peak};next.push(keep)
 }front=next}
 let upper=-Infinity;for(const a of front)for(const p of a)upper=Math.max(upper,Math.min(...p));return {incompatible:upper<0,method:'integer_pareto',upper,peak};
}
export function exactRank(F,ref,b,options={}){
 const n=F[0][0].length,forms=F.map(f=>f.length),states=stateCount(forms.map(x=>({length:x})),b);
 if(states>(options.maxStates??LIMITS.enumStates)||states*n>(options.maxCells??LIMITS.enumCells))return {status:'resource_unknown',states};
 let best=0,bestChoice=[],visited=0;const choice=Array(F.length).fill(0),score=new Float64Array(n);const records=options.collect?[]:null;
 function visit(t,cost){if(t===F.length){let rank=1;for(let j=0;j<n;j++)if(j!==ref&&score[j]>=score[ref])rank++;visited++;if(rank>best){best=rank;bestChoice=choice.slice()}if(records)records.push({choices:choice.slice(),worstTieRank:rank});return}
  for(let a=0;a<F[t].length;a++){if(a&&cost===b)continue;choice[t]=a;for(let j=0;j<n;j++)score[j]+=F[t][a][j];visit(t+1,cost+(a!==0));for(let j=0;j<n;j++)score[j]-=F[t][a][j]}
 }
 visit(0,0);return {status:'exact',states:visited,rank:best,choices:bestChoice,...(records?{records}:{})};
}
export function certify(I,input,opts={}){
 const started=performance.now(),query=normalize(input),tokens=query.split(' ').filter(Boolean),b=Number(opts.budget??2),channel=opts.channel||'keyboard',caps={...LIMITS,...opts.caps};
 if(!tokens.length)throw Error('Nhập truy vấn trước khi chạy.');if(!Number.isInteger(b)||b<0||b>2)throw Error('Ngân sách phải là 0, 1 hoặc 2 token.');
 if(tokens.length>caps.tokens||tokens.some(t=>Array.from(t).length>caps.tokenCodepoints))throw Error('Giới hạn web: 16 token, mỗi token tối đa 64 ký tự; truy vấn không bị cắt ngầm.');
 if(!['keyboard','accents','curated','mixed'].includes(channel))throw Error('Bộ lỗi không hợp lệ.');
 const forms=tokens.map(t=>alternatives(t,channel,opts.dictionary||{})),sumForms=forms.reduce((s,a)=>s+a.length,0);
 if(sumForms>caps.variants||sumForms*I.n>12_000_000)throw Error('Lattice vượt giới hạn bộ nhớ web. Giảm độ dài truy vấn hoặc corpus.');
 const worstGrams=forms.reduce((sum,fs)=>sum+Math.max(...fs.map(f=>[...grams(f.text).values()].reduce((s,v)=>s+v,0))),0);
 if(worstGrams*I.maxWeight>Number.MAX_SAFE_INTEGER/16)throw Error('Vượt miền tính số nguyên an toàn; không cấp chứng nhận.');
 const F=forms.map(fs=>fs.map(f=>scores(I,f.text))),raw=scores(I,query),order=ranking(I,raw),ref=order[0],candidates=[],pairWitnesses=[];
 for(let j=0;j<I.n;j++)if(j!==ref){let base=0;const gain=[],arg=[];for(const f of F){const d=f.map(v=>v[j]-v[ref]);base+=d[0];let a=0;for(let k=1;k<d.length;k++)if(d[k]>d[a])a=k;gain.push(d[a]-d[0]);arg.push(a)}
  if(base+top(gain.slice(),b)>=0){candidates.push(j);if(pairWitnesses.length<24){const choice=Array(tokens.length).fill(0);gain.map((g,t)=>({g,t})).sort((x,y)=>y.g-x.g).slice(0,b).forEach(({g,t})=>{if(g>0)choice[t]=arg[t]});pairWitnesses.push(choice)}}
 }
 const pairUpper=candidates.length+1;let groups=[],checks=[],graphUpper=pairUpper;
 if(candidates.length<=caps.candidates){const cache=new Map();for(const j of candidates){let placed=false;for(const group of groups){let valid=true;for(const k of group){const key=j+':'+k;if(!cache.has(key)){if(checks.length>=caps.checks){valid=false;break}const e=pairConflict(F,ref,j,k,b,caps);checks.push({left:I.docs[j].id,right:I.docs[k].id,...e});cache.set(key,e.incompatible)}if(!cache.get(key)){valid=false;break}}
   if(valid){group.push(j);placed=true;break}}
  if(!placed)groups.push([j])}graphUpper=groups.length+1;
 }else groups=candidates.map(j=>[j]);
 const exact=exactRank(F,ref,b,opts.enumeration||{}),upper=Math.min(pairUpper,graphUpper,exact.status==='exact'?exact.rank:Infinity);
 let rawTieRank=1;for(let j=0;j<I.n;j++)if(j!==ref&&raw[j]>=raw[ref])rawTieRank++;
 let witness={choices:Array(tokens.length).fill(0),rank:rawTieRank,text:query};
 for(const choice of [...pairWitnesses,...(exact.status==='exact'?[exact.choices]:[])]){const text=forms.map((f,i)=>f[choice[i]].text).join(' '),s=scores(I,text);let rank=1;for(let j=0;j<I.n;j++)if(j!==ref&&s[j]>=s[ref])rank++;if(rank>witness.rank)witness={choices:choice,rank,text}}
 if(witness.rank>upper)throw Error('Kiểm tra nội bộ thất bại: witness vượt cận. Kết quả không được cấp chứng nhận.');
 const cap=Number(opts.contextCap??10);if(!Number.isInteger(cap)||cap<1)throw Error('Giới hạn độ sâu phải là số nguyên dương.');const depth=upper<=cap?upper:null;
 const result={schema:'ngramlab.audit.v1',engine:VERSION,scorer:{kind:'integerized-character-BM25',scale:SCALE,ngram:[3,4,5],k1:1.2,b:.75,normalization:'NFC + Unicode lowercase + whitespace'},query,tokens,channel,budget:b,corpusSize:I.n,referenceId:I.docs[ref].id,
  cleanRanking:order.slice(0,Math.min(50,I.n)).map(j=>({id:I.docs[j].id,title:I.docs[j].title,text:I.docs[j].text,score:raw[j]/SCALE})),
  bounds:{pairwise:pairUpper,discrete:graphUpper,proposed:upper,exact:exact.status==='exact'?exact.rank:null},
  policy:{cap,certifiedDepth:depth,status:depth!==null?'certified':witness.rank>cap?'witness_exceeds_cap':'inconclusive',depthIsExactMinimum:exact.status==='exact'},
  lattice:{states:stateCount(forms,b),tokenStates:forms.map(a=>a.length),enumerationStatus:exact.status,enumerated:exact.status==='exact'?exact.states:0},
  proof:{candidates:candidates.map(j=>I.docs[j].id),groups:groups.map(g=>g.map(j=>I.docs[j].id)),checks,integerSafe:true,maxScoreBound:worstGrams*I.maxWeight,resourceCaps:caps},
  witness:{...witness,operations:witness.choices.flatMap((a,t)=>a?[{token:t,...forms[t][a]}]:[])},elapsedMs:performance.now()-started};
 if(opts.audit){result.forms=forms;result.referenceIndex=ref;result.factorScores=F.map(f=>f.map(v=>Array.from(v)));if(exact.records)result.exactStateRecords=exact.records}
 return result;
}
