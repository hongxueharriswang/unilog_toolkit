
import subprocess, tempfile, os
from typing import Tuple
from .env import which, NotAvailable

class ClingoAdapter:
    def __init__(self, binary: str='clingo'): self.binary=binary
    def is_available(self)->bool: return which(self.binary) is not None
    def run_asp(self, program: str)->Tuple[bool,str]:
        if not self.is_available(): raise NotAvailable('clingo not found in PATH')
        with tempfile.NamedTemporaryFile('w+', suffix='.lp', delete=False) as f:
            f.write(program); f.flush(); path=f.name
        try:
            res = subprocess.run([self.binary, path, '--quiet=1'], capture_output=True, text=True, timeout=30)
            out = (res.stdout or '') + (("
"+res.stderr) if res.stderr else '')
            return res.returncode==0, out.strip()
        finally:
            try: os.remove(path)
            except OSError: pass
