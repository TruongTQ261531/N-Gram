"""Author-distributed INT8 scorer; deliberately separate from FP32 reference."""
import json
from pathlib import Path
import onnxruntime as ort
from argon_followup_2026_11_01 import neural
from argon_followup_2026_11_01.neural_onnx import OnnxPredictor


class Int8Predictor(OnnxPredictor):
    SOURCE_FILE='ONNX_INT8_SOURCE.json'
    MODEL_FILE='model.int8.onnx'


if __name__=='__main__':
    neural.Predictor=Int8Predictor
    neural.RUNTIME_METADATA={'backend':'ONNX Runtime dynamic INT8','onnxruntime':ort.__version__,
        'dtype':'dynamic INT8; FP32 logits','attention':'ONNX CPU optimized graph',
        'wrapperSha256':neural.digest(Path(__file__)),
        'sharedOnnxWrapperSha256':neural.digest(neural.ROOT/'neural_onnx.py'),
        'onnxSource':json.loads((neural.ROOT/'ONNX_INT8_SOURCE.json').read_text())}
    neural.main()
