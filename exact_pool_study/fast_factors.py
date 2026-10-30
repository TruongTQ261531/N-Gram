"""Ordinary common-subexpression reuse for repeated token/form scoring.

Engineering control/optimization, not a new scoring model or novelty claim.
"""
from method import legacy
import numpy as np

def factors(index,text):
    tokens=legacy.normalize(text).split();assert tokens
    token_cache={};unique={};forms=[];positions=[]
    for token in tokens:
        if token not in token_cache:token_cache[token]=legacy.compact_forms(token)
        fs=token_cache[token];forms.append(fs);mapping=[]
        for form in fs:
            s=form['text']
            if s not in unique:unique[s]=len(unique)
            mapping.append(unique[s])
        positions.append(mapping)
    values=(index.vectorizer.transform(list(unique))@index.transpose).toarray()
    F=[values[np.asarray(mapping,dtype=int)] for mapping in positions]
    guard=sum(int(np.abs(f).max()) for f in F);assert guard<np.iinfo(np.int64).max//32
    return forms,F,{'originalTokens':len(tokens),'usedTokens':len(tokens),'truncated':False,'maxScoreBound':guard,'uniqueFormsScored':len(unique),'positionForms':sum(len(fs) for fs in forms)}
