

# UniLog Toolkit
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Alpha%200.1.0-orange.svg)](#roadmap)
[![Tests](https://img.shields.io/badge/tests-coming%20soon-lightgrey.svg)](#contributing)

**UniLog Toolkit** is a standalone Python library for **formal logical specification and evaluation** using **UniLang**—a concrete syntax for UniLog that integrates **classical, modal, temporal, probabilistic, fuzzy, non‑monotonic**, and **description logic** constructs in a single framework.

*   **Full UniLang parser** (ANTLR‑based) → **AST** → **modular inference engine**
*   Built‑in solvers for **classical**, **modal**, **temporal (simplified)**, and **fuzzy** logic
*   Clean, minimal **Model** interface (Kripke structures, probability measures, fuzzy sets, etc.)
*   Extensible via **custom solvers** and **custom models**
*   Completely independent of COH/GISMOL and CZOA/CZOI frameworks

> **Version:** 0.1.0 · **Date:** March 2026  
> **Author:** Harris (Harris) Wang · **Affiliation:** Athabasca University, Canada  
> **Contact:** <harrisw@athabascau.ca>

***

## Table of Contents

*   why-unilog-toolkit
*   features
*   installation
*   quick-start
*   unilang-at-a-glance
*   examples
    *   classical-fol--family-relationships
    *   modal--knowledge-and-belief
    *   temporal--mutual-exclusion-simplified
    *   probabilistic--weather-probability
    *   fuzzy--graded-truth-threshold
*   architecture
*   extending-unilog
    *   custom-solvers
    *   custom-models
*   roadmap
*   contributing
*   citing
*   license
*   repository
*   acknowledgements

***

## Why UniLog Toolkit?

Complex systems rarely fit into a single logical paradigm. UniLog lets you **mix and match**: quantify over domains, reason about **knowledge and belief**, specify **temporal** properties, evaluate **probabilistic** events, and handle **vagueness** with fuzzy semantics—all using one language and one engine. This toolkit gives you:

*   A **single parser & AST** across logics → easier tooling and interoperability
*   A **pluggable inference engine** → add your own semantics where needed
*   A lightweight **model abstraction** → bring your own Kripke structure, probability measure, or fuzzy membership functions

***

## Features

*   **Full UniLang support** for operators described in UniLog papers
*   **ANTLR‑based parser** with clear syntax errors (line/column)
*   **AST with Visitor pattern** for transformation and analysis
*   **Inference engine** that dispatches to logic‑specific solvers
*   **Built‑in solvers:** Classical, Modal, Temporal (simplified), Fuzzy
*   **Utilities**: pretty‑printing, substitution
*   **Standalone**: no dependency on COH/GISMOL or CZOA/CZOI

***

## Installation

> Python **3.7+** is required.

### From PyPI (recommended once published)

```bash
pip install unilog-toolkit
```

### From source

```bash
git clone https://github.com/hongxueharriswang/unilog_toolkit.git
cd unilog_toolkit
pip install -e .
```

### Dependencies

*   `antlr4-python3-runtime>=4.9`
*   `numpy>=1.19` (for fuzzy logic operators)

***

## Quick Start

Parse a UniLang formula and evaluate it against a minimal model:

```python
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World

class OneWorldModel(Model):
    def __init__(self):
        self.w = World(0)
    def worlds(self): return {self.w}
    def valuation(self, world, atom, args):  # p() is true, everything else false
        return atom == 'p' and args == ()
    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()
    def interpret(self, term, assignment): return None
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

parser = UniLangParser()
engine = InferenceEngine.get_instance()

phi = parser.parse_string("p -> p")     # classical tautology over our model
print(engine.evaluate(phi, OneWorldModel()))
```

***

## UniLang at a Glance

Some representative syntax (selection):

```unilog
-- Classical
forall x. (P(x) -> Q(x))      -- quantifiers, connectives
not (p and q) or r

-- Modal / Epistemic / Deontic
K[agent] p                     -- agent knows p
B[agent] p                     -- agent believes p
O p                            -- it is obligatory that p
<modal> p, [modal] p           -- diamond / box forms

-- Temporal (LTL/CTL fragments)
G (phi -> F psi)               -- globally ... eventually ...
X phi                          -- next
A G phi                        -- for all paths, globally phi

-- Probabilistic
P_>= 0.3 (rain)                -- probability of rain is at least 0.3
E[value(term)]                 -- expected value (placeholder)

-- Fuzzy (Łukasiewicz/Gödel/Product norms)
T_>= 0.7 (high(temp))          -- graded truth threshold
high(30) &G warm(30)           -- Gödel t-norm

-- Non-monotonic / Defaults
phi => psi                     -- default implication
```

***

## Examples

Below are condensed examples aligned with the technical report. They are minimal but runnable, and you can find longer versions under `examples/` (recommended directory layout: `examples/classical/…`, `examples/modal/…`, etc.).

### Classical FOL – Family Relationships

```python
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog.ast import Variable, Constant

class FamilyModel(Model):
    def __init__(self):
        self.w = World(0)
        self.facts = {
            ("parent", "alice", "bob"): True,
            ("parent", "bob", "charlie"): True,
            ("parent", "alice", "diana"): True,
            # derived/transitive closure for this example:
            ("ancestor", "alice", "bob"): True,
            ("ancestor", "bob", "charlie"): True,
            ("ancestor", "alice", "charlie"): True,
        }
        self._domain = {"alice", "bob", "charlie", "diana"}
    def worlds(self): return {self.w}
    def valuation(self, world, atom, args):
        return self.facts.get((atom,) + tuple(args), False)
    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return self._domain
    def interpret(self, term, assignment):
        if isinstance(term, Variable): return assignment.get(term.name)
        if isinstance(term, Constant): return term.value
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

parser = UniLangParser()
engine = InferenceEngine.get_instance()

q = parser.parse_string("ancestor(alice, charlie)")
print(engine.evaluate(q, FamilyModel()))   # -> True
```

### Modal – Knowledge and Belief

```python
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World

class EpistemicModel(Model):
    def __init__(self):
        self.w0, self.w1 = World(0), World(1)
        self._acc = {
            (self.w0, 'K', 'agent'): {self.w0, self.w1},
            (self.w1, 'K', 'agent'): {self.w0, self.w1},
        }
    def worlds(self): return {self.w0, self.w1}
    def valuation(self, w, atom, args):
        return (w == self.w0 and atom == 'p') or (w == self.w1 and atom == 'q')
    def accessibility(self, world, modality, agent=None):
        return self._acc.get((world, modality, agent), set())
    def domain(self): return set()
    def interpret(self, term, assignment): return None
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

parser = UniLangParser(); engine = InferenceEngine.get_instance()
knows_p = parser.parse_string("K[agent] p")
knows_q = parser.parse_string("K[agent] q")
print(engine.evaluate(knows_p, EpistemicModel(), world=EpistemicModel().w0))  # False
print(engine.evaluate(knows_q, EpistemicModel(), world=EpistemicModel().w0))  # False
```

### Temporal – Mutual Exclusion (simplified)

> The built‑in temporal solver is a **placeholder**. Use it for scaffolding and replace with a model checker (e.g., NuSMV) for real verification.

```python
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog.ast import Variable, Constant

class MutualExclusionModel(Model):
    def __init__(self):
        self.s0, self.s1, self.s2 = World('s0'), World('s1'), World('s2')
        self._trans = {self.s0:[self.s1, self.s2], self.s1:[self.s0], self.s2:[self.s0]}
    def worlds(self): return {self.s0, self.s1, self.s2}
    def valuation(self, w, atom, args):
        if atom == 'in_cs':
            return (w == self.s1 and args == ('A',)) or (w == self.s2 and args == ('B',))
        return False
    def accessibility(self, w, modality, agent=None):
        return set(self._trans.get(w, [])) if modality == 'X' else set()
    def domain(self): return {'A', 'B'}
    def interpret(self, term, assignment):
        if isinstance(term, Variable): return assignment.get(term.name)
        if isinstance(term, Constant): return term.value
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

parser = UniLangParser(); engine = InferenceEngine.get_instance()
phi = parser.parse_string("G (in_cs(A) -> not in_cs(B))")
print(engine.evaluate(phi, MutualExclusionModel(), world=MutualExclusionModel().s0))  # True (placeholder)
```

### Probabilistic – Weather Probability

```python
from unilog.engine.model import Model, World

class WeatherModel(Model):
    def __init__(self):
        self.w1, self.w2, self.w3 = World('cloudy_rain'), World('cloudy_dry'), World('not_cloudy')
        self._worlds = {self.w1, self.w2, self.w3}
        self._probs = {self.w1: 0.32, self.w2: 0.08, self.w3: 0.60}
    def worlds(self): return self._worlds
    def valuation(self, w, atom, args):
        return (atom == 'rain' and w == self.w1) or (atom == 'cloudy' and w in (self.w1, self.w2))
    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()
    def interpret(self, term, assignment): return None
    def probability(self, world, event): return sum(self._probs[w] for w in self._worlds if w in event)
    def preference(self, world, w1, w2): return False

model = WeatherModel()
rain_event = {w for w in model.worlds() if model.valuation(w, 'rain', ())}
print("P(rain) =", model.probability(None, rain_event))   # 0.32
```

### Fuzzy – Graded Truth Threshold

```python
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog.ast import Function, Constant

class FuzzyModel(Model):
    def __init__(self): self.w = World(0)
    def worlds(self): return {self.w}
    def valuation(self, world, atom, args): return False
    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()
    def interpret(self, term, assignment):
        if isinstance(term, Function) and term.name == 'high':
            x = term.args[0].value if isinstance(term.args[0], Constant) else None
            return max(0.0, min(1.0, (x - 25) / 10))  # μ_high(x)
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

parser = UniLangParser(); engine = InferenceEngine.get_instance()
print(engine.evaluate(parser.parse_string("T_>= 0.5 (high(30))"), FuzzyModel()))  # True
```

***

## Architecture

    unilog/
      parser/           # ANTLR grammar (UniLang.g4), parser entry points
      ast/              # AST nodes (Formula, Atom, connectives, quantifiers, modal, temporal, probabilistic, fuzzy, defaults, DL, terms)
      engine/
        __init__.py     # InferenceEngine (singleton)
        model.py        # Model, World abstractions
        solvers/        # ClassicalSolver, ModalSolver, TemporalSolver (stub), FuzzySolver
      utils/            # PrettyPrinter, SubstitutionVisitor

**Key classes & contracts**

*   **`UniLangParser`** → `parse_string`, `parse_file` → returns `Formula` AST or raises `UniLangSyntaxError`.
*   **`InferenceEngine.get_instance()`** → `evaluate(formula, model, world=None, assignment=None)` → `bool` or `float`.
*   **`Model` (abstract)** requires:
    *   `worlds() -> Set[World]`
    *   `valuation(world, atom, args) -> bool`
    *   `accessibility(world, modality, agent) -> Set[World]`
    *   `domain() -> Set[Any]`
    *   `interpret(term, assignment) -> Any`
    *   `probability(world, event) -> float`
    *   `preference(world, w1, w2) -> bool`

***

## Extending UniLog

### Custom Solvers

Add a new logic fragment by implementing `Solver`:

```python
from unilog.engine import InferenceEngine
from unilog.engine.solvers import Solver

class MySolver(Solver):
    def supports(self, formula) -> bool:
        # return True if this solver handles 'formula' type
        ...
    def evaluate(self, formula, model, world, assignment):
        # compute truth/grade of 'formula' under 'model'
        return ...

engine = InferenceEngine.get_instance()
engine.register_solver(MySolver())
```

### Custom Models

Define semantics of your domain by implementing `Model`:

```python
from unilog.engine.model import Model, World

class MyModel(Model):
    def __init__(self, ...):
        self._worlds = {...}
        ...
    def worlds(self): ...
    def valuation(self, world, atom, args): ...
    def accessibility(self, world, modality, agent=None): ...
    def domain(self): ...
    def interpret(self, term, assignment): ...
    def probability(self, world, event): ...
    def preference(self, world, w1, w2): ...
```

***

## Roadmap

Planned work (contributions welcome):

*   **Temporal solver**: full LTL/CTL with external model checkers (NuSMV, SPIN)
*   **Probabilistic solver**: PRISM/Storm integration
*   **Default/non‑monotonic**: ASP (clingo) backend
*   **Automated theorem proving** for first‑order fragments
*   **Web demo** & interactive docs
*   **Performance**: large‑model optimizations

See ./ROADMAP.md (create this file to track progress).

***

## Contributing

We welcome issues and PRs!

1.  **Fork** and create a feature branch.
2.  Add tests (pytest) under `tests/` mirroring `unilog/*` layout.
3.  Run `ruff`/`black` formatting (if adopted) and ensure CI passes.
4.  Submit a PR with a descriptive summary and examples.

Suggested checks (add a GitHub Action later):

```bash
pytest
python -m pip install ruff black
ruff check unilog
black --check unilog
```

***

## Citing

If you use UniLog Toolkit in academic work, please cite the technical report:

    @techreport{unilog_toolkit_2026,
      title   = {UniLog Toolkit: A Unified Toolkit for Multi-Paradigm Logic in Python},
      author  = {Harris Wang},
      year    = {2026},
      month   = {March},
      institution = {Athabasca University},
      url     = {https://github.com/hongxueharriswang/unilog_toolkit}
    }

***

## License

./LICENSE

***

## Repository

*   **Repo:** <https://github.com/hongxueharriswang/unilog_toolkit>
*   **Issues:** <https://github.com/hongxueharriswang/unilog_toolkit/issues>
*   **Releases:** (to be published)
*   **PyPI:** (to be published as `unilog-toolkit`)

***

## Acknowledgements

*   ANTLR runtime for Python
*   Inspiration from standard semantics of modal, temporal, probabilistic, and fuzzy logics
*   Community feedback and contributors (add list once PRs land)

***

### Want me to also:

*   add a `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and a minimal GitHub Actions workflow (pytest + ruff/black)?
*   scaffold an `examples/` folder and `tests/` with the above cases?
*   generate API docs via `pdoc`/`Sphinx` with autodoc from the AST & engine?

If yes, tell me your preferred repo slug and style tools (ruff/black/mypy), and I’ll prepare the files.
