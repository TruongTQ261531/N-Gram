"""Same checkpoint's pinned FP32 ONNX export, with explicit runtime amendment."""
import time,json,hashlib
from pathlib import Path
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from argon_followup_2026_11_01 import neural


class OnnxPredictor:
    SOURCE_FILE='ONNX_SOURCE.json'
    MODEL_FILE='model.onnx'
    def __init__(self,path,texts):
        spec=json.loads((neural.ROOT/self.SOURCE_FILE).read_text())
        assert hashlib.sha256((path/self.MODEL_FILE).read_bytes()).hexdigest()==spec['sha256']
        self.texts=texts;self.tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True)
        opts=ort.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
        opts.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
        opts.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session=ort.InferenceSession(str(path/self.MODEL_FILE),opts,providers=['CPUExecutionProvider'])
        self.names={i.name for i in self.session.get_inputs()};self.calls=0
    def score(self,query,documents):
        started=time.perf_counter();result=[];limit=0
        for offset in range(0,len(documents),32):
            ds=documents[offset:offset+32]
            batch=self.tokenizer([query]*len(ds),[self.texts[int(d)] for d in ds],
                                 padding='max_length',truncation=True,max_length=256,return_tensors='np')
            limit+=int((batch['attention_mask'].sum(1)==256).sum())
            batch={k:np.asarray(v,dtype=np.int64) for k,v in batch.items() if k in self.names}
            result.extend(self.session.run(None,batch)[0][:,0].tolist());self.calls+=1
        return np.asarray(result),{'seconds':time.perf_counter()-started,'pairs':len(documents),
                                  'atTokenLimit':limit,'tokenLimitCountIsUpperBoundOnTruncated':True}


if __name__=='__main__':
    neural.Predictor=OnnxPredictor
    neural.RUNTIME_METADATA={'backend':'ONNX Runtime FP32','onnxruntime':ort.__version__,
                             'attention':'ONNX optimized graph','wrapperSha256':neural.digest(Path(__file__)),
                             'onnxSource':json.loads((neural.ROOT/'ONNX_SOURCE.json').read_text())}
    neural.main()
