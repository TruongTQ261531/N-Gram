"""Archived-original labeled English GTC multiword pilot, independently selected."""
import argparse,base64,gzip,hashlib,heapq,json
from pathlib import Path
from reviewer_audit_2026_10_31.retention import normalize
from decision_audit_2026_10_31.typos import membership,wilson

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    spec=json.loads((ROOT/'GTC_SOURCE.json').read_text());data=a.source.read_bytes()
    assert hashlib.sha256(data).hexdigest()==spec['sha256']
    assert base64.b32encode(hashlib.sha1(data).digest()).decode()==spec['cdxDigest']
    del data
    counts={'commits':0,'edits':0,'notLabeledEnglishTypo':0,'normalizationEqual':0,'notMultiword':0,'tooLong':0,'duplicates':0,'eligible':0}
    selected={};seen=set()
    with gzip.open(a.source,'rt',encoding='utf-8') as stream:
        for line,text in enumerate(stream,1):
            r=json.loads(text);counts['commits']+=1
            for edit,e in enumerate(r.get('edits',[])):
                counts['edits']+=1;s=e.get('src',{});t=e.get('tgt',{})
                if e.get('is_typo') is not True or s.get('lang')!='eng' or t.get('lang')!='eng':counts['notLabeledEnglishTypo']+=1;continue
                src=s['text'];tgt=t['text'];x=normalize(src);y=normalize(tgt)
                if x==y:counts['normalizationEqual']+=1;continue
                if min(len(x.split()),len(y.split()))<2:counts['notMultiword']+=1;continue
                if max(len(src),len(tgt))>2048:counts['tooLong']+=1;continue
                digest=hashlib.sha256(('argon-gtc-v1|'+src+'\0'+tgt).encode()).hexdigest()
                if digest in seen:counts['duplicates']+=1;continue
                seen.add(digest);counts['eligible']+=1
                if len(selected)<200 or digest<max(selected):
                    selected[digest]={'source':src,'target':tgt,'sourceLine':line,'editIndex':edit,'repository':r.get('repo'),'commit':r.get('commit'),
                                      'probTypo':e.get('prob_typo')}
                    if len(selected)>200:del selected[max(selected)]
    assert len(selected)==200
    selection_path=a.output.with_name('gtc-selection.json')
    if selection_path.exists():raise FileExistsError(selection_path)
    ordered=sorted(selected)
    selection={'source':spec,'counts':counts,'rows':[{'hash':h,**{k:v for k,v in selected[h].items() if k not in ['source','target']}} for h in ordered]}
    selection_path.write_text(json.dumps(selection,indent=2)+'\n')
    rows=[]
    for digest in ordered:
        pair=selected[digest];clean=normalize(pair['target']).split();err=normalize(pair['source']).split()
        result=membership(pair['target'],pair['source'],2)
        rows.append({'hash':digest,'sourceLine':pair['sourceLine'],'editIndex':pair['editIndex'],'cleanTokens':len(clean),'erroneousTokens':len(err),
                     'alignedChangedPositions':sum(x!=y for x,y in zip(clean,err)) if len(clean)==len(err) else None,**result})
    b1=sum(r['status']=='covered' and r['minimumCostWithinBudget']<=1 for r in rows)
    b2=sum(r['status']=='covered' and r['minimumCostWithinBudget']<=2 for r in rows)
    metrics={'sample':200,'b1':b1,'b2':b2,'increment':b2-b1,'wilson95B1':wilson(b1,200),'wilson95B2':wilson(b2,200),
             'outside32TokenScope':sum(r['status']=='outside_input_scope' for r in rows),'outsideChannelOrBudget':sum(r['status']=='outside_channel_or_budget' for r in rows)}
    report={'source':spec,'counts':counts,'metrics':metrics,'rows':rows,'retrospective':True,'rawTextRedistributed':False,
            'scope':'Archived original, automatically labeled English typo edits; >=2 tokens; not query traffic, semantic gold or new collected data'}
    a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'counts':counts,'metrics':metrics},indent=2))


if __name__=='__main__':main()
