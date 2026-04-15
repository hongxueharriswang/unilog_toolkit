# A Comprehensive Guide for Intelligent Systems Developers

**Version:** 0.1.0  
**Date:** March 2026  
**Author:** Harris Wang  
**Contact:** harrisw@athabascau.ca  
**Repository:** [https://github.com/hongxueharriswang/unilog_toolkit](https://github.com/hongxueharriswang/unilog_toolkit)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
    - 3.1 [UniLang Syntax](#31-unilang-syntax)
    - 3.2 [Abstract Syntax Tree (AST)](#32-abstract-syntax-tree-ast)
    - 3.3 [Inference Engine](#33-inference-engine)
    - 3.4 [Model Interface](#34-model-interface)
    - 3.5 [Built‑in Solvers](#35-built‑in-solvers)
4. [Tutorial: Step‑by‑Step Examples](#tutorial-step‑by‑step-examples)
    - 4.1 [Hello World: Parsing a Formula](#41-hello-world-parsing-a-formula)
    - 4.2 [Defining a Custom Model](#42-defining-a-custom-model)
    - 4.3 [Classical Logic: Family Relationships](#43-classical-logic-family-relationships)
    - 4.4 [Modal Logic: Knowledge and Belief](#44-modal-logic-knowledge-and-belief)
    - 4.5 [Fuzzy Logic: Temperature Control](#45-fuzzy-logic-temperature-control)
    - 4.6 [Temporal Logic: Mutual Exclusion (Simplified)](#46-temporal-logic-mutual-exclusion-simplified)
    - 4.7 [Probabilistic Logic: Weather Prediction](#47-probabilistic-logic-weather-prediction)
    - 4.8 [Quantifiers and Domains](#48-quantifiers-and-domains)
5. [Advanced Topics](#advanced-topics)
    - 5.1 [Writing Custom Solvers](#51-writing-custom-solvers)
    - 5.2 [Integrating External Model Checkers](#52-integrating-external-model-checkers)
    - 5.3 [Using the Visitor Pattern for Transformations](#53-using-the-visitor-pattern-for-transformations)
    - 5.4 [Performance Considerations](#54-performance-considerations)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Conclusion](#conclusion)

---

## 1. Introduction

The UniLog Toolkit is a Python library for working with the UniLang language, a unified logical syntax for expressing UniLog. UniLog integrates classical, modal, temporal, probabilistic, fuzzy, and non‑monotonic reasoning within a single formal framework. The toolkit provides a parser, an abstract syntax tree (AST) representation, and a modular inference engine capable of evaluating formulas against user‑supplied models. It is framework‑agnostic—independent of systems such as COH/GISMOL or CZOA/CZOI—and is designed for general use by researchers and practitioners who need to specify, analyze, and reason about logical constraints in intelligent systems.

This tutorial will guide you through the toolkit's features, from basic parsing to advanced customisation. By the end, you will be able to:

- Parse UniLang formulas into an AST.
- Implement your own models (Kripke structures, probabilistic distributions, fuzzy sets, etc.).
- Use the inference engine to evaluate formulas.
- Extend the toolkit with custom solvers and transformations.

---

## 2. Installation


For the latest development version, clone the repository and install with pip:

```bash
git clone https://github.com/hongxueharriswang/unilog_toolkit.git
cd unilog_toolkit
pip install .
```

**Dependencies:**
- Python 3.7+
- `antlr4-python3-runtime>=4.9`
- `numpy>=1.19` (used for fuzzy logic and embeddings)

**Optional:** For integration with external solvers (e.g., NuSMV, PRISM), you will need to install those tools separately.

---

## 3. Core Concepts

### 3.1 UniLang Syntax

UniLang is a concrete syntax for UniLog. It supports a wide range of operators. Here are some examples:

```unilog
% Classical logic
forall x:Person . (parent(x,alice) -> ancestor(x,alice))

% Modal logic
K[agent] (p -> q)           % agent knows that p implies q

% Temporal logic
G (request -> F response)   % globally, if request occurs, eventually response

% Probabilistic
P_>= 0.8 (rain)              % probability of rain at least 0.8

% Fuzzy
T_>= 0.5 (high(temperature)) % truth value of 'high(temperature)' ≥ 0.5

% Non‑monotonic
bird(X) => flies(X)          % default: birds typically fly

% Description logic
some hasChild Human(bob)     % bob has a child who is Human
```

The full grammar is defined in the `UniLang.g4` file. The parser accepts a signature declaration (optional) followed by formulas.

### 3.2 Abstract Syntax Tree (AST)

Every UniLang formula is parsed into an AST node. All nodes inherit from the abstract base class `Formula`. The AST is defined in `unilog.ast.nodes`. Key node types:

- `Atom(name, args)` – atomic predicate, e.g., `parent(alice,bob)`.
- Connectives: `AndFormula`, `OrFormula`, `ImpliesFormula`, `IffFormula`, `NotFormula`.
- Quantifiers: `ForallFormula(var, sort, body)`, `ExistsFormula`.
- Modal: `BoxModal(modality, agent, sub)`, `DiamondModal`, `KFormula`, `BFormula`, `OFormula`, `PFormula`, `FModal`.
- Temporal: `GFormula(sub, bound)`, `FFormula`, `XFormula`, `UntilFormula`, `ReleaseFormula`, `AFormula`, `EFormula`.
- Dynamic: `BoxAction(action, sub)`, `DiamondAction`, `AtomicAction`, `SequenceAction`, `ChoiceAction`, `StarAction`, `TestAction`.
- Probabilistic: `ProbGeq(threshold, sub)`, `ProbLeq`, `ProbEq`, `ExpectedValue(term)`.
- Fuzzy: `FuzzyAnd(left, right, norm)`, `FuzzyOr`, `FuzzyNot`, `GradedTruth(threshold, sub)`.
- Non‑monotonic: `DefaultImplies(ante, cons)`, `Preference(left, right)`, `Optimal(sub)`.
- Description Logic: `ConceptApplication(concept, term)`, plus concept constructors.
- Terms: `Variable(name)`, `Constant(value)`, `Function(name, args)`.

All nodes implement `accept(visitor)` to support the visitor pattern.

### 3.3 Inference Engine

The inference engine (`InferenceEngine`) is a singleton that evaluates formulas against a model. It maintains a registry of solvers, each responsible for a specific type of formula. The evaluation workflow:

1. Obtain the current world (state) from the model (or use the provided one).
2. Find a solver that supports the formula type.
3. The solver evaluates the formula recursively, calling back to the engine for sub‑formulas if needed.
4. Returns a result (boolean for classical/modal, float for fuzzy/probabilistic).

### 3.4 Model Interface

To evaluate formulas, you must provide a model that implements the abstract class `Model`. The required methods are:

```python
class Model(ABC):
    @abstractmethod
    def worlds(self) -> Set[World]:
        """Return the set of all possible worlds."""
        pass

    @abstractmethod
    def valuation(self, world: World, atom: str, args: Tuple[Any, ...]) -> bool:
        """Truth of an atomic predicate in a given world."""
        pass

    @abstractmethod
    def accessibility(self, world: World, modality: str, agent: Optional[str] = None) -> Set[World]:
        """Worlds accessible from 'world' via a given modality (e.g., 'K', 'box')."""
        pass

    @abstractmethod
    def domain(self) -> Set[Any]:
        """Domain of individuals (for quantifiers)."""
        pass

    @abstractmethod
    def interpret(self, term: Term, assignment: Dict[str, Any]) -> Any:
        """Evaluate a term under a variable assignment."""
        pass

    @abstractmethod
    def probability(self, world: World, event: Set[World]) -> float:
        """Probability measure at a given world."""
        pass

    @abstractmethod
    def preference(self, world: World, w1: World, w2: World) -> bool:
        """True if w1 is preferred over w2 at world."""
        pass
```

You only need to implement the methods relevant to your logic. For classical logic, `accessibility`, `probability`, and `preference` can return dummy values.

### 3.5 Built‑in Solvers

The toolkit comes with four built‑in solvers:

- **`ClassicalSolver`** – Handles atomic formulas, connectives, and quantifiers (over finite domains).
- **`ModalSolver`** – Handles box, diamond, and derived modal operators.
- **`TemporalSolver`** – A simplified placeholder for temporal operators. For real applications, replace with an external model checker.
- **`FuzzySolver`** – Handles fuzzy connectives and graded truth using Gödel, Łukasiewicz, or product t‑norms.

All solvers are registered automatically when the engine is instantiated.

---

## 4. Tutorial: Step‑by‑Step Examples

### 4.1 Hello World: Parsing a Formula

Let's start by parsing a simple UniLang formula.

```python
from unilog.parser import UniLangParser

parser = UniLangParser()
formula = parser.parse_string("p and q")
print(type(formula))          # <class 'unilog.ast.nodes.AndFormula'>
print(formula.left.name)      # p
print(formula.right.name)     # q
```

If the formula has a syntax error, `UniLangSyntaxError` is raised:

```python
try:
    formula = parser.parse_string("p and")   # incomplete
except UniLangSyntaxError as e:
    print(f"Error at line {e.line}, column {e.column}: {e.message}")
```

### 4.2 Defining a Custom Model

We'll create a simple model with a single world and some atomic facts.

```python
from unilog.engine.model import Model, World
from unilog.ast import Variable, Constant

class SimpleModel(Model):
    def __init__(self):
        self._world = World(0)
        self.facts = {
            ("p",): True,
            ("q",): False,
        }

    def worlds(self): return {self._world}

    def valuation(self, world, atom, args):
        # atom is a string, args is a tuple
        key = (atom,) + args
        return self.facts.get(key, False)

    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()
    def interpret(self, term, assignment): return None
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False
```

Now we can evaluate formulas against this model.

### 4.3 Classical Logic: Family Relationships

We'll model a family with `parent` facts and define a rule for `ancestor` (transitive closure). Since the inference engine does not do forward‑chaining, we will compute the closure ourselves and add the derived facts to the model.

```python
class FamilyModel(Model):
    def __init__(self):
        self._world = World(0)
        self.facts = {
            ("parent", "alice", "bob"): True,
            ("parent", "bob", "charlie"): True,
            ("parent", "alice", "diana"): True,
        }
        # Compute ancestor closure
        self._compute_ancestors()

    def _compute_ancestors(self):
        # Add ancestor facts using transitive closure
        ancestors = set()
        # We'll do a simple loop
        changed = True
        while changed:
            changed = False
            for (rel, a, b) in list(self.facts.keys()):
                if rel == "parent":
                    if ("ancestor", a, b) not in self.facts:
                        self.facts[("ancestor", a, b)] = True
                        changed = True
                if rel == "ancestor":
                    # if ancestor(a,b) and parent(b,c) then ancestor(a,c)
                    for (rel2, c, d) in list(self.facts.keys()):
                        if rel2 == "parent" and b == c:
                            if ("ancestor", a, d) not in self.facts:
                                self.facts[("ancestor", a, d)] = True
                                changed = True
        # Also add self‑ancestor? Not needed for our query.

    def worlds(self): return {self._world}
    def valuation(self, world, atom, args): return self.facts.get((atom,)+args, False)
    # ... other methods as before

model = FamilyModel()
parser = UniLangParser()
engine = InferenceEngine.get_instance()

# Query: ancestor(alice, charlie)
query = parser.parse_string("ancestor(alice, charlie)")
result = engine.evaluate(query, model)
print(f"Is Alice an ancestor of Charlie? {result}")   # True
```

### 4.4 Modal Logic: Knowledge and Belief

We'll build an epistemic model with two worlds. World 0: `p` true, `q` false. World 1: `p` false, `q` true. The agent considers both worlds possible (S5).

```python
class EpistemicModel(Model):
    def __init__(self):
        self.w0 = World(0)
        self.w1 = World(1)
        # agent's epistemic relation: from each world, both worlds are accessible
        self._access = {
            (self.w0, 'K', 'agent'): {self.w0, self.w1},
            (self.w1, 'K', 'agent'): {self.w0, self.w1},
        }

    def worlds(self): return {self.w0, self.w1}

    def valuation(self, world, atom, args):
        if world == self.w0:
            return atom == 'p'
        else:
            return atom == 'q'

    def accessibility(self, world, modality, agent=None):
        return self._access.get((world, modality, agent), set())

    # other methods as before (return defaults)

model = EpistemicModel()
engine = InferenceEngine.get_instance()

# Evaluate at world 0
knows_p = parser.parse_string("K[agent] p")
knows_q = parser.parse_string("K[agent] q")
print(engine.evaluate(knows_p, model, world=model.w0))   # False
print(engine.evaluate(knows_q, model, world=model.w0))   # False
```

### 4.5 Fuzzy Logic: Temperature Control

Define a fuzzy predicate `high(x)` with membership function and evaluate a graded truth.

```python
class FuzzyTemperatureModel(Model):
    def __init__(self, temp):
        self.temp = temp
        self._world = World(0)

    def worlds(self): return {self._world}
    def valuation(self, world, atom, args): return False   # not used
    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()
    def interpret(self, term, assignment):
        if isinstance(term, Function) and term.name == 'high':
            arg = term.args[0]
            if isinstance(arg, Constant):
                x = arg.value
                # membership function: high(x) = max(0, min(1, (x-25)/10))
                return max(0.0, min(1.0, (x - 25) / 10))
        return None
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

model = FuzzyTemperatureModel(30)
formula = parser.parse_string("T_>= 0.5 (high(30))")
result = engine.evaluate(formula, model)
print(f"high(30) >= 0.5? {result}")   # True (value = 0.5)
```

### 4.6 Temporal Logic: Mutual Exclusion (Simplified)

We'll create a simple Kripke structure with three states and a transition relation. The temporal solver in the toolkit is a placeholder; we will simulate a basic check.

```python
class MutualExclusionModel(Model):
    def __init__(self):
        self.s0 = World('s0')
        self.s1 = World('s1')
        self.s2 = World('s2')
        self._worlds = {self.s0, self.s1, self.s2}
        self._transitions = {
            self.s0: [self.s1, self.s2],
            self.s1: [self.s0],
            self.s2: [self.s0],
        }

    def worlds(self): return self._worlds
    def valuation(self, world, atom, args):
        if atom == 'in_cs':
            if world == self.s1:
                return args == ('A',)
            if world == self.s2:
                return args == ('B',)
            return False
        return False
    def accessibility(self, world, modality, agent=None):
        if modality == 'X':   # next
            return set(self._transitions.get(world, []))
        return set()
    # ... other methods

model = MutualExclusionModel()
formula = parser.parse_string("G (in_cs(A) -> not in_cs(B))")
result = engine.evaluate(formula, model, world=model.s0)
print(result)   # True (placeholder)
```

For real temporal logic, you would replace the `TemporalSolver` with one that calls NuSMV or another model checker.

### 4.7 Probabilistic Logic: Weather Prediction

We'll define a model with three worlds representing the joint distribution of `cloudy` and `rain`, and compute the probability of `rain`.

```python
class WeatherModel(Model):
    def __init__(self):
        self.w1 = World('cloudy_rain')
        self.w2 = World('cloudy_dry')
        self.w3 = World('not_cloudy')
        self._worlds = {self.w1, self.w2, self.w3}
        self._probs = {
            self.w1: 0.32,
            self.w2: 0.08,
            self.w3: 0.60,
        }

    def worlds(self): return self._worlds
    def valuation(self, world, atom, args):
        if atom == 'rain':
            return world == self.w1
        if atom == 'cloudy':
            return world in (self.w1, self.w2)
        return False
    def probability(self, world, event):
        # total probability of event across all worlds
        total = 0.0
        for w in self._worlds:
            if w in event:
                total += self._probs[w]
        return total
    # ... other methods

model = WeatherModel()
# We want P(rain). Define an event as the set of worlds where rain is true.
rain_event = {w for w in model.worlds() if model.valuation(w, 'rain', ())}
prob_rain = model.probability(None, rain_event)
print(f"Probability of rain: {prob_rain}")
```

To evaluate a probabilistic formula like `P_>= 0.3 (rain)`, you would need a probabilistic solver that uses `probability` to compute the measure of the set of worlds satisfying the formula. The toolkit does not include such a solver by default, but you can write one.

### 4.8 Quantifiers and Domains

Quantifiers require a domain of individuals. The model must provide `domain()` and `interpret()` to handle terms. Here's a simple example:

```python
class QuantifierModel(Model):
    def __init__(self):
        self._world = World(0)
        self._domain = {1, 2, 3}
        self.facts = {
            ("p", 1): True,
            ("p", 2): True,
            ("p", 3): False,
        }

    def worlds(self): return {self._world}
    def valuation(self, world, atom, args):
        return self.facts.get((atom, args[0]), False)
    def domain(self): return self._domain
    def interpret(self, term, assignment):
        if isinstance(term, Variable):
            return assignment.get(term.name, None)
        if isinstance(term, Constant):
            return term.value
        return None
    # ... other methods

model = QuantifierModel()
formula = parser.parse_string("forall x . p(x)")
result = engine.evaluate(formula, model)
print(result)   # False (since p(3) is false)
```

---

## 5. Advanced Topics

### 5.1 Writing Custom Solvers

To handle new operators or custom evaluation strategies, you can write your own solver. Subclass `Solver` and implement `supports(formula)` and `evaluate(formula, model, world, assignment)`.

```python
from unilog.engine.solvers import Solver
from unilog.engine import InferenceEngine

class MySpecialSolver(Solver):
    def supports(self, formula):
        return isinstance(formula, MySpecialFormula)

    def evaluate(self, formula, model, world, assignment):
        # custom logic
        return some_value

engine = InferenceEngine.get_instance()
engine.register_solver(MySpecialSolver())
```

### 5.2 Integrating External Model Checkers

For temporal logic, you can replace the built‑in `TemporalSolver` with one that calls an external tool. Example sketch using NuSMV:

```python
import subprocess
import tempfile

class NuSMVSolver(Solver):
    def supports(self, formula):
        return isinstance(formula, (GFormula, FFormula, XFormula, UntilFormula))

    def evaluate(self, formula, model, world, assignment):
        # Translate formula and model to NuSMV input
        smv_code = self.translate(model, formula)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.smv') as f:
            f.write(smv_code)
            f.flush()
            result = subprocess.run(['NuSMV', f.name], capture_output=True, text=True)
        # Parse output to get True/False
        return 'true' in result.stdout.lower()
```

### 5.3 Using the Visitor Pattern for Transformations

The AST supports the visitor pattern. You can implement custom visitors for tasks like pretty‑printing, substitution, or conversion to other formats.

```python
from unilog.utils.visitors import PrettyPrinter

printer = PrettyPrinter()
print(printer.visit(formula))
```

To implement a substitution visitor:

```python
from unilog.ast import *
from unilog.utils.visitors import SubstitutionVisitor

sub = SubstitutionVisitor('x', Constant(5))
new_formula = sub.visit(formula)
```

### 5.4 Performance Considerations

- For large domains, quantifier evaluation can be expensive because it iterates over all domain elements. If possible, restrict the domain size or use symbolic methods.
- Modal logic evaluation may require exploring many worlds. Consider caching accessibility relations.
- For probabilistic logic, computing measures over sets of worlds can be costly; use efficient data structures.
- For temporal logic, external model checkers are recommended.

---

## 6. Best Practices

1. **Keep models simple** – Implement only the methods you need. For classical logic, you can leave `accessibility`, `probability`, and `preference` returning empty sets or defaults.
2. **Use the visitor pattern** for transformations rather than manually traversing the AST.
3. **Test incrementally** – Start with small formulas and models to verify correctness.
4. **Document your model** – Clearly state what each world represents and the meaning of atomic predicates.
5. **Extend solvers** when you need new semantics; don't modify the built‑in ones.
6. **Handle errors gracefully** – The parser raises `UniLangSyntaxError`; catch it and provide user‑friendly messages.

---

## 7. Troubleshooting

| Problem | Possible Solution |
|---------|-------------------|
| `UniLangSyntaxError` | Check your formula syntax. Use the error line/column to locate the mistake. |
| `ValueError: No solver found` | Your formula type is not supported by any registered solver. Implement a custom solver or ensure the formula uses only built‑in operators. |
| Quantifier evaluates incorrectly | Ensure your model's `domain()` returns all individuals and `interpret()` correctly maps terms. |
| Modal formula gives unexpected result | Verify your `accessibility` method returns the correct set of worlds. |
| Fuzzy logic returns boolean instead of float | Fuzzy operators are handled by `FuzzySolver`, which returns floats for sub‑formulas but `GradedTruth` returns a boolean. |
| Performance is slow | For large models, consider caching or using external solvers. |

---

## 8. Conclusion

The UniLog Toolkit provides a flexible foundation for working with multi‑paradigm logic in Python. This tutorial has covered installation, core concepts, and a range of examples from classical to fuzzy logic. You have learned how to define custom models, evaluate formulas, and extend the toolkit with your own solvers. The toolkit is open‑source and welcomes contributions. Use it to build intelligent systems that require rich logical constraints, and adapt it to your specific domain.

For further information, consult the API reference, the source code, and the research papers on UniLog. Happy reasoning!