"""Preselected author-curated spelling-pair pilot, not query-traffic validation."""
from pathlib import Path
import argparse,hashlib,json,math
from reviewer_audit_2026_10_31.retention import normalize
from core import variants

ROOT=Path(__file__).resolve().parent

def wilson(success,n):
    if not n:return None
    z=1.959963984540054;p=success/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0.,center-half),min(1.,center+half)]

def membership(clean,erroneous,budget=2):
    source=normalize(clean).split();target=normalize(erroneous).split()
    if len(source)>32:return {'status':'outside_input_scope','minimumCostWithinBudget':None}
    if source==target:return {'status':'normalization_only','minimumCostWithinBudget':0,'operations':[]}
    current={(0,0):[]}
    for i,token in enumerate(source):
        forms,operations=variants(token);next_states={}
        for (j,cost),trace in current.items():
            for a,form in enumerate(forms):
                after=cost+int(a!=0)
                if after>budget:continue
                if form=='':position=j
                elif j<len(target) and form==target[j]:position=j+1
                else:continue
                key=(position,after)
                if key not in next_states:
                    next_states[key]=trace+([{'token':i,**operations[a]}] if a else [])
        current=next_states
    accepted=[(cost,trace) for (j,cost),trace in current.items() if j==len(target)]
    if not accepted:return {'status':'outside_channel_or_budget','minimumCostWithinBudget':None}
    cost,trace=min(accepted,key=lambda x:x[0])
    return {'status':'covered','minimumCostWithinBudget':cost,'operations':trace}

def parse(data):
    text=data.decode('utf-8');target=None;target_line=None
    for line_number,line in enumerate(text.splitlines(),1):
        if not line:continue
        if line.startswith('$'):target=line[1:].replace('_',' ');target_line=line_number
        else:
            if target is None:raise ValueError('Misspelling before any target')
            yield {'erroneous':line.replace('_',' '),'corrected':target,
                'sourceLine':line_number,'targetLine':target_line}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    freeze=json.loads((ROOT/'TYPO_FREEZE.json').read_text());data=args.source.read_bytes()
    assert hashlib.sha256(data).hexdigest()==freeze['source']['sha256']
    for file,digest in freeze['files'].items():assert hashlib.sha256((ROOT.parent/file).read_bytes()).hexdigest()==digest,file
    unique={};counts={'rawPairs':0,'excludedLength':0,'excludedEqual':0,'duplicates':0}
    for pair in parse(data):
        counts['rawPairs']+=1;src=pair['erroneous'];tgt=pair['corrected']
        if src==tgt:counts['excludedEqual']+=1;continue
        if max(len(src),len(tgt))>512:counts['excludedLength']+=1;continue
        digest=hashlib.sha256(('20261031|'+src+'\0'+tgt).encode()).hexdigest()
        if digest in unique:counts['duplicates']+=1;continue
        unique[digest]=pair
    counts['eligibleUniquePairs']=len(unique);assert len(unique)>=100
    # Freeze exactly which pairs will be evaluated before calling membership.
    chosen=sorted(unique)[:100];rows=[]
    selection={'sourceSha256':freeze['source']['sha256'],'selectionRule':'100 smallest SHA256(20261031|erroneous\\0corrected)',
        'selectedPairHashes':chosen,'counts':counts}
    selection_path=args.output.with_name(args.output.stem+'.selection.json')
    if selection_path.exists():raise FileExistsError(selection_path)
    selection_path.write_text(json.dumps(selection,indent=2)+'\n')
    for digest in chosen:
        pair=unique[digest];result=membership(pair['corrected'],pair['erroneous'])
        rows.append({'pairHash':digest,'sourceLine':pair['sourceLine'],'targetLine':pair['targetLine'],
            'cleanTokens':len(normalize(pair['corrected']).split()),
            'erroneousTokens':len(normalize(pair['erroneous']).split()),**result})
    categories={name:sum(r['status']==name for r in rows) for name in ['covered','normalization_only','outside_input_scope','outside_channel_or_budget']}
    coverage={}
    for budget in [1,2]:
        covered=sum(r['status']=='covered' and r['minimumCostWithinBudget']<=budget for r in rows)
        nontrivial=100-categories['normalization_only']
        coverage[str(budget)]={'coveredNontrivialPairs':covered,'allSampledPairs':100,
            'fractionOfAllSampledPairs':covered/100,'wilson95AllSampled':wilson(covered,100),
            'effectiveChangePairs':nontrivial,'fractionOfEffectiveChanges':covered/nontrivial if nontrivial else None,
            'wilson95EffectiveChanges':wilson(covered,nontrivial)}
    report={'status':'COMPLETE','retrospective':True,'source':freeze['source'],'samplePairs':100,
        'categories':categories,'coverage':coverage,'rows':rows,
        'limits':'Curated type-level Wikipedia misspellings with source lexicon filtering; not frequency-weighted query logs, semantic-equivalence labels or RAG evaluation. Most targets are single words; B2 need not add coverage.',
        'rawTextsRedistributed':False,'encoding':'UTF-8; underscore decoded as space per author documentation'}
    args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))

if __name__=='__main__':main()
