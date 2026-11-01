"""Lossless storage of a large execution gzip in ordinary Git-sized parts."""
import gzip,hashlib,io,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def execution_bytes():
    path=ROOT/'results/records.jsonl.gz'
    if path.exists():return path.read_bytes()
    spec=json.loads((ROOT/'results/records.parts.json').read_text());chunks=[]
    for item in spec['parts']:
        value=(ROOT/'results'/item['name']).read_bytes()
        assert len(value)==item['bytes'] and hashlib.sha256(value).hexdigest()==item['sha256']
        chunks.append(value)
    value=b''.join(chunks)
    assert hashlib.sha256(value).hexdigest()==spec['originalGzipSha256']
    return value


def execution_rows():
    with gzip.open(io.BytesIO(execution_bytes()),'rt') as f:
        for line in f:yield json.loads(line)


def shard():
    path=ROOT/'results/records.jsonl.gz';value=path.read_bytes();parts=[]
    for number,start in enumerate(range(0,len(value),8*1024**2)):
        chunk=value[start:start+8*1024**2];name=f'records.jsonl.gz.part{number:03}'
        (ROOT/'results'/name).write_bytes(chunk)
        parts.append({'name':name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
    (ROOT/'results/records.parts.json').write_text(json.dumps({'originalGzipSha256':hashlib.sha256(value).hexdigest(),
        'originalBytes':len(value),'parts':parts,'encoding':'Concatenate exact bytes in order; then gzip decompress. No numerical data changed.'},indent=2)+'\n')
    print('Lossless gzip parts:',len(parts),'total bytes:',len(value))


if __name__=='__main__':shard()
