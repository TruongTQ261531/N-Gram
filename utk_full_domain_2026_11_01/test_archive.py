import gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from utk_full_domain_2026_11_01 import archive


class TestLosslessArchive(unittest.TestCase):
    def fixture(self,root):
        result=root/'results';result.mkdir()
        value=gzip.compress(b'{"queryId":"q1"}\n{"queryId":"q2"}\n')
        chunks=[value[:len(value)//2],value[len(value)//2:]];parts=[]
        for i,chunk in enumerate(chunks):
            name=f'records.jsonl.gz.part{i:03}';(result/name).write_bytes(chunk)
            parts.append({'name':name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
        (result/'records.parts.json').write_text(json.dumps({'parts':parts,'originalGzipSha256':hashlib.sha256(value).hexdigest()}))
        return value

    def test_records_replay_without_private_monolithic_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);value=self.fixture(root)
            with patch.object(archive,'ROOT',root):
                self.assertEqual(archive.execution_bytes(),value)
                self.assertEqual(list(archive.execution_rows()),[{'queryId':'q1'},{'queryId':'q2'}])

    def test_corrupt_part_cannot_pass_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            (root/'results/records.jsonl.gz.part001').write_bytes(b'bad')
            with patch.object(archive,'ROOT',root),self.assertRaises(AssertionError):archive.execution_bytes()


if __name__=='__main__':unittest.main()
