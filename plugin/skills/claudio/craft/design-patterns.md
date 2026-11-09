# Design patterns

Use a pattern when the problem asks for it, never to show off (KISS, YAGNI). For each one: the
problem it solves, the signs you need it, and the signs it is overkill. In REVIEW check both ways:
missing where needed, forced where not.

## Creational

### Factory Method

- **Problem:** the caller shouldn't know which concrete class it gets.
- **Signs you need it:** the same `if type == …: X() else Y()` choice repeated where objects are
  built; construction needs setup beyond a plain constructor.
- **Overkill when:** there is one implementation and no sign of a second.

### Abstract Factory

- **Problem:** creating families of related objects that must match (a theme's button + menu).
- **Signs:** mixing parts from two families would break things.
- **Overkill when:** there is only one family.

### Builder

- **Problem:** an object with many optional parts, or built in steps.
- **Signs:** a constructor with a long list of parameters, several of them `None`/null.
- **Overkill when:** the language has named arguments and defaults, or a data class does the job.

### Prototype

- **Problem:** copying a ready object is simpler than building a new one.
- **Signs:** expensive setup repeated to make near-identical objects.
- **Overkill when:** construction is cheap.

### Singleton

- **Problem:** exactly one instance must exist.
- **Use with care:** hidden global state, hard to test. Prefer creating one instance at the edge
  and passing it in (Dependency Injection).
- **Overkill when:** almost always; one instance is a wiring choice, not a class rule.

## Structural

### Adapter

- **Problem:** you must use a class whose interface doesn't fit yours.
- **Signs:** translation logic for a library spread through business rules.
- **Overkill when:** you own both sides; change one instead.

### Bridge

- **Problem:** two things vary on their own (shape and renderer).
- **Signs:** a class per combination (`RedCircle`, `BlueCircle`, `RedSquare` …).
- **Overkill when:** only one side varies.

### Composite

- **Problem:** a tree where single items and groups are treated the same.
- **Signs:** `if is_group: for child …` repeated by every caller.
- **Overkill when:** the structure is flat.

### Decorator

- **Problem:** add behaviour to one object without changing its class (logging, caching, retries).
- **Signs:** a subclass per combination of extras.
- **Overkill when:** one fixed extra; just put it in the class.

### Facade

- **Problem:** one simple entry point to a messy subsystem.
- **Signs:** every caller repeats the same five calls in the same order.
- **Overkill when:** the subsystem is already simple.

### Flyweight

- **Problem:** many small objects share most of their data.
- **Signs:** memory grows with millions of near-identical objects.
- **Overkill when:** the numbers are small; measure first.

### Proxy

- **Problem:** control access to an object (lazy load, cache, permissions, remote calls).
- **Signs:** the same access check or cache lookup around every call.
- **Overkill when:** one caller; put the check there.

## Behavioural

### Strategy

- **Problem:** swap one way of doing something for another; replaces `if/else` on a type.
- **Signs:** the same switch on a kind in several places; a new kind means editing them all.
- **Overkill when:** two fixed cases that never grow; a plain `if` is clearer.

### State

- **Problem:** an object's behaviour changes with its state (e.g. TDCG phases).
- **Signs:** every method starts with `if state == …`.
- **Overkill when:** few states, simple rules: an enum plus a table is enough. Same shape as
  Strategy; Strategy picks *how* once, State reacts to transitions *over time*.

### Observer

- **Problem:** others must react when something changes, without the source knowing them.
- **Signs:** the source calls a growing list of unrelated listeners by name.
- **Overkill when:** one fixed listener.

### Command

- **Problem:** turn a request into an object (queue, undo, log, retry).
- **Signs:** you need to store, replay or undo actions.
- **Overkill when:** actions run once, right away.

### Template Method

- **Problem:** the same steps, different details in subclasses.
- **Signs:** copies of one algorithm that differ in one or two steps.
- **Overkill when:** passing a function for the step that varies is simpler (prefer that in most
  languages).

### Chain of Responsibility

- **Problem:** several handlers may take a request, in order (e.g. a row of guards).
- **Signs:** a long `if a … elif b … elif c` deciding who handles it.
- **Overkill when:** one or two fixed handlers.

### Iterator

- **Problem:** walk a collection without knowing how it is stored.
- **Signs:** callers reaching into a structure's insides to loop over it.
- **Overkill when:** the language's own iteration already does it (it usually does).

### Mediator

- **Problem:** many objects talk through one place instead of to each other.
- **Signs:** a web of objects that all know each other.
- **Overkill when:** two or three collaborators.

### Memento

- **Problem:** save and restore an object's state without exposing its insides.
- **Signs:** undo, snapshots, "go back to before".
- **Overkill when:** the state is a plain immutable value; just keep the old one.

### Visitor

- **Problem:** add operations to a fixed set of types without changing them.
- **Signs:** many operations over a stable type tree (an AST).
- **Overkill when:** the types change often, or the language has pattern matching.

## More

### Repository

- **Problem:** keep storage details away from business rules; the rest asks a repository for
  data without knowing where it comes from (database, cache, file).
- **Signs:** queries or file reads inside business logic.
- **Overkill when:** a script with one read.

### Dependency Injection

- **Problem:** a class needs collaborators; pass them in instead of building them inside. Makes
  it testable and swappable.
- **Signs:** `new` of a client inside a service; tests that can't replace a dependency.
- **Overkill when:** a pure function with no collaborators.

### Value Object

- **Problem:** a small immutable object compared by value (a money amount, a cycle).
- **Signs:** the same few fields passed around together; bugs from changing shared objects.
- **Overkill when:** a single plain value with no rules.

### Null Object

- **Problem:** a do-nothing object instead of `None` checks everywhere.
- **Signs:** the same `if x is None` before every call.
- **Overkill when:** `None` means a real error; then raise instead.

## Architecture-level patterns

- **Event-driven:** services produce and consume events instead of calling each other; the
  producer doesn't know the consumers. See [system design](../knowledge/system-design.md).
- **API gateway**, **pub/sub**, **message queue**, **CQRS**-style read replicas: see the same
  page.
