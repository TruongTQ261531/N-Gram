"""Own grams/Python integers reconstruct every unique full-corpus form row."""
from collections import Counter
from pathlib import Path
import argparse,gzip,json,pickle,sys,time,unicodedata
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'pool_study'))
def grams(text):
    c=Counter()
    for word in ' '.join(unicodedata.normalize('NFC',text).lower().split()).split():
        s=' '+word+' '
        for width in (3,4,5):
            for i in range(len(s)-width+1):c[s[i:i+width]]+=1
    return c
def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();start=time.perf_counter()
    with (a.data/(a.dataset+'-index.pkl')).open('rb') as f:I=pickle.load(f)
    W=I.weights.tocsc();vocab=I.vectorizer.vocabulary_;checked=forms=queries=0
    with gzip.open(ROOT/'results'/a.dataset/'records.jsonl.gz','rt') as f:
        for line in f:
            row=json.loads(line);assert row['modelHash']==I.model_hash
            with np.load(ROOT/'results'/a.dataset/row['factorFile']) as z:
                for text,saved in zip(row['uniqueFormTexts'],z['scores']):
                    score=[0]*I.n
                    for g,c in grams(text).items():
                        index=vocab.get(g)
                        if index is None:continue
                        left,right=W.indptr[index:index+2]
                        for j,w in zip(W.indices[left:right],W.data[left:right]):score[int(j)]+=c*int(w)
                    assert score==saved.tolist();checked+=I.n;forms+=1
            queries+=1
    result={'dataset':a.dataset,'queries':queries,'uniqueQueryForms':forms,'integerTokenDocumentScores':checked,'mismatches':0,'pythonIntegerAccumulation':True,'modelHash':I.model_hash,'seconds':time.perf_counter()-start};a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
