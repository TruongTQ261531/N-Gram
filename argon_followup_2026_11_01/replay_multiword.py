"""Replay all600 source pairs and independently check accepted edit witnesses."""
import argparse,gzip,hashlib,json
from pathlib import Path
from reviewer_audit_2026_10_31.retention import normalize
from decision_audit_2026_10_31.typos import membership

ROOT=Path(__file__).resolve().parent
COORD={c:(j+off,i) for i,(letters,off) in enumerate([('qwertyuiop',0.),('asdfghjkl',.3),('zxcvbnm',.7)]) for j,c in enumerate(letters)}


def neighbors(char):
    if char not in COORD:return []
    x,y=COORD[char]
    return [c for c,(a,b) in COORD.items() if c!=char and (a-x)**2+(b-y)**2<=1.6**2]


def one_edits(word):
    for i,c in enumerate(word):
        yield word[:i]+word[i+1:]
        yield word[:i]+c+word[i:]
        for z in neighbors(c):yield word[:i]+z+word[i+1:]
        if i+1<len(word):yield word[:i]+word[i+1]+c+word[i+2:]


def check_pair(clean,erroneous,row):
    result=membership(clean,erroneous,2)
    assert result['status']==row['status'] and result['minimumCostWithinBudget']==row['minimumCostWithinBudget']
    if row['status']!='covered':return
    words=normalize(clean).split();changed=set()
    assert len(row['operations'])==row['minimumCostWithinBudget']<=2
    for op in row['operations']:
        token=op['token'];assert token not in changed;changed.add(token)
        word=words[token];pos=op['pos'];assert 0<=pos<len(word)
        if op['op']=='delete':modified=word[:pos]+word[pos+1:]
        elif op['op']=='repeat':modified=word[:pos]+word[pos]+word[pos:]
        elif op['op']=='keyboard':
            assert op['char'] in neighbors(word[pos]);modified=word[:pos]+op['char']+word[pos+1:]
        elif op['op']=='swap':
            assert pos+1<len(word);modified=word[:pos]+word[pos+1]+word[pos]+word[pos+2:]
        else:raise AssertionError(op)
        assert modified!=word;words[token]=modified
    assert normalize(' '.join(words))==normalize(erroneous)
    if row['minimumCostWithinBudget']==2:
        original=normalize(clean).split();target=normalize(erroneous)
        for i,word in enumerate(original):
            for alternative in one_edits(word):
                assert normalize(' '.join(original[:i]+[alternative]+original[i+1:]))!=target


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    multi=json.loads((ROOT/'results/multiword.json').read_text());selection=json.loads((ROOT/'results/multiword-selection.json').read_text())
    counts={};accepted_two=0
    for panel,body in multi['panels'].items():
        suffix='ref0' if panel=='human_ref0' else 'spellchecked.src';by_id={r['hash']:r for r in selection['panels'][panel]};cache={}
        for split in ['dev','test']:
            cache[split]=((a.data/'jfleg'/split/(split+'.src')).read_text().splitlines(),(a.data/'jfleg'/split/(split+'.'+suffix)).read_text().splitlines())
        for row in body['rows']:
            item=by_id[row['hash']];srcs,tgts=cache[item['split']];src=srcs[item['line']-1];tgt=tgts[item['line']-1]
            assert hashlib.sha256(('argon-multiword-v1|'+panel+'|'+src+'\0'+tgt).encode()).hexdigest()==row['hash']
            check_pair(tgt,src,row);accepted_two+=row.get('minimumCostWithinBudget')==2
        counts[panel]=len(body['rows'])
    gtc=json.loads((ROOT/'results/gtc.json').read_text());sel=json.loads((ROOT/'results/gtc-selection.json').read_text())
    by_key={(r['sourceLine'],r['editIndex']):r for r in sel['rows']};result={(r['sourceLine'],r['editIndex']):r for r in gtc['rows']}
    assert hashlib.sha256((a.data/'github-typo-corpus.archived.jsonl.gz').read_bytes()).hexdigest()==gtc['source']['sha256']
    found=0
    with gzip.open(a.data/'github-typo-corpus.archived.jsonl.gz','rt') as f:
        wanted={k[0] for k in by_key}
        for line,text in enumerate(f,1):
            if line not in wanted:continue
            commit=json.loads(text)
            for edit,e in enumerate(commit['edits']):
                key=(line,edit)
                if key not in by_key:continue
                item=by_key[key];row=result[key];src=e['src']['text'];tgt=e['tgt']['text']
                assert e['is_typo'] is True and e['src']['lang']==e['tgt']['lang']=='eng'
                assert item['repository']==commit['repo'] and item['commit']==commit['commit']
                assert hashlib.sha256(('argon-gtc-v1|'+src+'\0'+tgt).encode()).hexdigest()==row['hash']
                check_pair(tgt,src,row);found+=1;accepted_two+=row.get('minimumCostWithinBudget')==2
    assert found==200;counts['gtc']=found
    receipt={'status':'PASS','sourcePairsReplayed':counts,'independentWitnessAndNoB1CheckForAcceptedCost2':accepted_two,
             'rawTextsRedistributed':False,'scope':'Source identities and exact channel membership, not human semantic labeling'}
    a.output.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
