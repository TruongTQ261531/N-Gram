"""Original FP32 model with standard length bucketing and dynamic padding."""
import time,json
from pathlib import Path
import numpy as np
import onnxruntime as ort
from argon_followup_2026_11_01 import neural
from argon_followup_2026_11_01.neural_onnx import OnnxPredictor


class BucketPredictor(OnnxPredictor):
    def score(self,query,documents):
        started=time.perf_counter()
        if not len(documents):return np.array([]),{'seconds':time.perf_counter()-started,'pairs':0,'atTokenLimit':0,'tokenLimitCountIsUpperBoundOnTruncated':True}
        encoded=self.tokenizer([query]*len(documents),[self.texts[int(d)] for d in documents],
                               padding=False,truncation=True,max_length=256)
        lengths=np.array([len(x) for x in encoded['input_ids']]);order=np.argsort(lengths,kind='stable')
        scores=np.empty(len(documents),dtype=np.float32);padded_tokens=0
        for offset in range(0,len(documents),32):
            selected=order[offset:offset+32]
            examples=[{k:encoded[k][int(i)] for k in encoded} for i in selected]
            batch=self.tokenizer.pad(examples,padding=True,return_tensors='np')
            batch={k:np.asarray(v,dtype=np.int64) for k,v in batch.items() if k in self.names}
            padded_tokens+=int(batch['input_ids'].size)
            scores[selected]=self.session.run(None,batch)[0][:,0];self.calls+=1
        return scores.astype(float),{'seconds':time.perf_counter()-started,'pairs':len(documents),
              'atTokenLimit':int((lengths==256).sum()),'tokenLimitCountIsUpperBoundOnTruncated':True,
              'paddedTokenCells':padded_tokens,'fixed256TokenCells':256*len(documents)}


if __name__=='__main__':
    neural.Predictor=BucketPredictor
    neural.RUNTIME_METADATA={'backend':'ONNX Runtime FP32 length-bucketed','onnxruntime':ort.__version__,
        'attention':'ONNX optimized graph','padding':'dynamic within length-sorted batches; max256',
        'wrapperSha256':neural.digest(Path(__file__)),
        'sharedOnnxWrapperSha256':neural.digest(neural.ROOT/'neural_onnx.py'),
        'onnxSource':json.loads((neural.ROOT/'ONNX_SOURCE.json').read_text())}
    neural.main()
