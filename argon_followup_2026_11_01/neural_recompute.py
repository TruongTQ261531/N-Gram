"""Fresh full128-query reproduction of the final primary FP32 configuration."""
import json
from pathlib import Path
import onnxruntime as ort
from argon_followup_2026_11_01 import neural
from argon_followup_2026_11_01.neural_bucket import BucketPredictor


if __name__=='__main__':
    neural.Predictor=BucketPredictor
    neural.RUNTIME_METADATA={'backend':'ONNX Runtime FP32 length-bucketed','onnxruntime':ort.__version__,
        'attention':'ONNX optimized graph','padding':'dynamic within length-sorted batches; max256',
        'wrapperSha256':neural.digest(Path(__file__)),'costRepeats':1,
        'onnxSource':json.loads((neural.ROOT/'ONNX_SOURCE.json').read_text())}
    neural.main()
