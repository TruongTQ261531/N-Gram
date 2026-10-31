"""Resume all unfinished fixed queries using the SAME FP32 pipeline."""
import json
from pathlib import Path
import onnxruntime as ort
from argon_followup_2026_11_01 import neural
from argon_followup_2026_11_01.neural_bucket import BucketPredictor


if __name__=='__main__':
    receipt=json.loads((neural.ROOT/'results/neural-fp32-bucket-phase1/completion.json').read_text())
    neural.Predictor=BucketPredictor
    neural.RUNTIME_METADATA={'backend':'ONNX Runtime FP32 length-bucketed','onnxruntime':ort.__version__,
        'attention':'ONNX optimized graph','padding':'dynamic within length-sorted batches; max256',
        'wrapperSha256':neural.digest(Path(__file__)),'bucketWrapperSha256':neural.digest(neural.ROOT/'neural_bucket.py'),
        'sharedOnnxWrapperSha256':neural.digest(neural.ROOT/'neural_onnx.py'),
        'onnxSource':json.loads((neural.ROOT/'ONNX_SOURCE.json').read_text()),
        'completedQueryIds':receipt['completedQueryIds'],'costRepeats':1,
        'continuationReceiptSha256':neural.digest(neural.ROOT/'results/neural-fp32-bucket-phase1/completion.json')}
    neural.main()
