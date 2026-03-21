
import subprocess, tempfile, os
from typing import Tuple
from .env import which, NotAvailable

class PrismAdapter:
    def __init__(self, binary: str='prism'): self.binary=binary
    def is_available(self)->bool: return which(self.binary) is not None
    def run_prism(self, model_text: str, property_text: str)->Tuple[bool,str]:
        if not self.is_available(): raise NotAvailable('prism not found in PATH')
        with tempfile.NamedTemporaryFile('w+', suffix='.prism', delete=False) as mf, \
             tempfile.NamedTemporaryFile('w+', suffix='.props', delete=False) as pf:
            mf.write(model_text); mf.flush(); pf.write(property_text); pf.flush()
            mpath, ppath = mf.name, pf.name
        try:
            res = subprocess.run([self.binary, mpath, ppath, '-pf', property_text], capture_output=True, text=True, timeout=60)
            out = (res.stdout or '') + (("
"+res.stderr) if res.stderr else '')
            return res.returncode==0, out.strip()
        finally:
            for p in (mpath,ppath):
                try: os.remove(p)
                except OSError: pass
