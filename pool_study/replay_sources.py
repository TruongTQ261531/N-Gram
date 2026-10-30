"""Reconstruct every stored token/doc score independently from index postings.

Uses own character extraction and Python integer accumulation, not sklearn's
query vectorizer or the candidate/oracle scorer. Source index is locally built
by run.py from pinned corpus bytes. This checks all original-corpus documents.
"""
from collections import Counter
from pathlib import Path
import argparse,gzip,json,pickle,time,unicodedata
import numpy as np

ROOT=Path(__file__).resolve().parent

def independent_grams(text):
    normalized=' '.join(unicodedata.normalize('NFC',text).lower().split());counts=Counter()
    for word in normalized.split():
        chars=[' ']+list(word)+[' ']
        for width in (3,4,5):
            for pos in range(len(chars)-width+1):counts[''.join(chars[pos:pos+width])]+=1
    return counts

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--dataset',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    start=time.perf_counter()
    # core is loaded only to deserialize the original index, not to calculate query scores.
    with (a.data/(a.dataset+'-index.pkl')).open('rb') as f:I=pickle.load(f)
    W=I.weights.tocsc();vocabulary=I.vectorizer.vocabulary_;checked=forms=queries=0
    with gzip.open(ROOT/'results'/a.dataset/'records.jsonl.gz','rt') as f:
        for line in f:
            row=json.loads(line);assert row['modelHash']==I.model_hash
            with np.load(ROOT/'results'/a.dataset/row['factorFile']) as z:
                for t,fs in enumerate(row['forms']):
                    for s,form in enumerate(fs):
                        score=[0]*I.n
                        for g,c in independent_grams(form['text']).items():
                            column=vocabulary.get(g)
                            if column is None:continue
                            left,right=W.indptr[column:column+2]
                            for doc,w in zip(W.indices[left:right],W.data[left:right]):score[int(doc)]+=c*int(w)
                        assert score==z['f'+str(t)][s].tolist(),(row['queryId'],t,s)
                        checked+=I.n;forms+=1
            queries+=1
    result={'dataset':a.dataset,'queries':queries,'forms':forms,'independentTokenDocumentScores':checked,'allOriginalCorpusDocuments':I.n,'mismatches':0,'pythonArbitraryPrecisionAccumulation':True,'seconds':time.perf_counter()-start,'modelHash':I.model_hash}
    a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
