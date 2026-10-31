"""Two explicitly different author-hosted multiword correction proxies."""
import argparse,hashlib,json
from pathlib import Path
from reviewer_audit_2026_10_31.retention import normalize
from decision_audit_2026_10_31.typos import membership,wilson

ROOT=Path(__file__).resolve().parent


def select(source):
    panels={};counts={}
    for panel,suffix in [('human_ref0','ref0'),('enchant','spellchecked.src')]:
        pairs={};stats={'rawPairs':0,'normalizationEqual':0,'notMultiword':0,'tooLong':0,'duplicates':0}
        for split in ['dev','test']:
            src=(source/split/(split+'.src')).read_text().splitlines()
            tgt=(source/split/(split+'.'+suffix)).read_text().splitlines()
            assert len(src)==len(tgt)
            for line,(erroneous,clean) in enumerate(zip(src,tgt),1):
                stats['rawPairs']+=1;x=normalize(erroneous);y=normalize(clean)
                if x==y:stats['normalizationEqual']+=1;continue
                if min(len(x.split()),len(y.split()))<2:stats['notMultiword']+=1;continue
                if max(len(erroneous),len(clean))>2048:stats['tooLong']+=1;continue
                digest=hashlib.sha256(('argon-multiword-v1|'+panel+'|'+erroneous+'\0'+clean).encode()).hexdigest()
                if digest in pairs:stats['duplicates']+=1;continue
                pairs[digest]={'source':erroneous,'target':clean,'split':split,'line':line}
        stats['eligible']=len(pairs);counts[panel]=stats
        panels[panel]={k:pairs[k] for k in sorted(pairs)[:200]}
    return panels,counts


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    spec=json.loads((ROOT/'JFLEG_SOURCE.json').read_text())
    for f in spec['files']:assert hashlib.sha256((a.source/f['path']).read_bytes()).hexdigest()==f['sha256']
    panels,counts=select(a.source)
    selection={'source':spec,'counts':counts,'panels':{name:[{'hash':k,'split':v['split'],'line':v['line']} for k,v in pairs.items()] for name,pairs in panels.items()}}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    selection_path=a.output.with_name('multiword-selection.json')
    if selection_path.exists():raise FileExistsError(selection_path)
    selection_path.write_text(json.dumps(selection,indent=2)+'\n')
    report={'retrospective':True,'source':spec,'panels':{},'rawTextRedistributed':False}
    for panel,pairs in panels.items():
        rows=[]
        for digest,pair in pairs.items():
            result=membership(pair['target'],pair['source'],2)
            clean=normalize(pair['target']).split();err=normalize(pair['source']).split()
            rows.append({'hash':digest,'split':pair['split'],'line':pair['line'],
                'cleanTokens':len(clean),'erroneousTokens':len(err),
                'alignedChangedPositions':sum(x!=y for x,y in zip(clean,err)) if len(clean)==len(err) else None,**result})
        n=len(rows);b1=sum(r['status']=='covered' and r['minimumCostWithinBudget']<=1 for r in rows)
        b2=sum(r['status']=='covered' and r['minimumCostWithinBudget']<=2 for r in rows)
        metrics={'sample':n,'b1':b1,'b2':b2,'increment':b2-b1,'wilson95B1':wilson(b1,n),'wilson95B2':wilson(b2,n),
                 'outside32TokenScope':sum(r['status']=='outside_input_scope' for r in rows),
                 'outsideChannelOrBudget':sum(r['status']=='outside_channel_or_budget' for r in rows)}
        report['panels'][panel]={'metrics':metrics,'rows':rows}
        print(panel,metrics,flush=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
