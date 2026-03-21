
import subprocess, tempfile, os
from typing import Tuple
from .env import which, NotAvailable

class SMTLibEncoder:
    def __init__(self):
        self.lines=[]; self.symbols=set()
    def declare_pred(self, name: str, arity: int):
        if name not in self.symbols:
            if arity==0: self.lines.append(f"(declare-const {name} Bool)")
            else: self.lines.append(f"(declare-fun {name} ({' '.join(['Int']*arity)}) Bool)")
            self.symbols.add(name)
    def assert_clause(self, clause: str): self.lines.append(f"(assert {clause})")
    def check_sat(self)->str: return "
".join(self.lines+["(check-sat)","(exit)"])

class Z3Adapter:
    def __init__(self, binary: str='z3'): self.binary=binary
    def is_available(self)->bool: return which(self.binary) is not None
    def run_smt(self, smt2: str):
        if not self.is_available(): raise NotAvailable('z3 not found in PATH')
        with tempfile.NamedTemporaryFile('w+', suffix='.smt2', delete=False) as f:
            f.write(smt2); f.flush(); path=f.name
        try:
            res = subprocess.run([self.binary, path], capture_output=True, text=True, timeout=30)
            out = (res.stdout or '') + (("
"+res.stderr) if res.stderr else '')
            ok = 'sat' in res.stdout or 'unsat' in res.stdout
            return ok, out.strip()
        finally:
            try: os.remove(path)
            except OSError: pass
