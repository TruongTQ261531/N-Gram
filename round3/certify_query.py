"""Use the frozen certifier on one new query; no labels are consumed."""
import argparse,json
from replay import predict
from core import Index,normalize
from run import CACHE,native
def main():
 p=argparse.ArgumentParser();p.add_argument('--dataset',choices=['scifact','nfcorpus','fiqa'],required=True);p.add_argument('--query',required=True);p.add_argument('--budget',type=int,choices=[1,2,3],default=2);p.add_argument('--k',type=int,default=10);a=p.parse_args()
 if a.k<1:p.error('--k must be positive')
 original=normalize(a.query).split();text=' '.join(original[:32])
 if not text:p.error('Query is empty after normalization')
 index=CACHE/(a.dataset+'_char.pkl')
 if not index.exists():p.error('Build the local index with: python round3/run.py prepare --dataset '+a.dataset)
 I=Index.load(index);I.transpose();bound,detail=predict(I,text,'proposed',budget_max=a.budget,audit_details=True)
 out={'dataset':a.dataset,'corpus_documents':I.n,'budget':a.budget,'k':a.k,'used_tokens':min(32,len(original)),'truncated':len(original)>32,
  'rank_upper':bound[-1],'certified_retention':bound[-1]<=a.k,'reference_id':detail[-1]['reference_id'],
  'scope':'finite single deletion/swap/repeat/QWERTY-neighbor per original token; worst-tie rank; no relevance or semantic guarantee','certificate':detail[-1]}
 print(json.dumps(native(out),indent=2))
if __name__=='__main__':main()
