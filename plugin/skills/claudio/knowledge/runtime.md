# Runtime

## Read this when

- the work runs on the JVM (Java, Kotlin), or a runtime detail matters
- memory, threads, strings or startup time come up
- a language basic (types, access, constructors) shapes the design

Other languages get their own sections as projects need them.

## The JVM

- Source compiles to **bytecode** (`.class`), not machine instructions; any machine with a JVM
  runs it. The portability lives in the JVM.
- The JVM loads and verifies classes, interprets bytecode, **JIT-compiles** hot paths to native
  machine instructions, and manages memory.
- Startup is slow compared with plain Python or native binaries: a reason short-lived tools (like
  hooks run on every action) are written in a fast-starting language.

## JVM memory

- **Heap** (shared by all threads): every object and array; garbage collected. Shared, so
  concurrent access needs synchronization.
- **Method area / Metaspace** (shared): class metadata, static fields, bytecode.
- **Stack** (one per thread): a frame per call with locals and arguments. Not shared.
- **PC register** (one per thread): the current instruction.

## Language basics

- `main` is a fixed contract with the runtime; change its signature and it is no longer the entry
  point.
- **Strings** are immutable and pooled: literals share one object; `new String("a")` makes a new
  one; compare with `equals`, not `==`.
- **Access:** `public` everywhere, `protected` package + subclasses, package-private (no keyword)
  package only, `private` the class only. Keep things as private as possible.
- **Primitives vs references:** primitives hold values; references point to objects on the
  heap. Wrappers (`Integer`) let primitives live in collections; they are immutable.
- **Static** = one per class; instance fields = one per object.
- **Constructors** have the class name, no return type; overload them for different ways to build.
- **Records / data classes** for immutable values with equality by value.

## Concurrency basics

- `volatile` gives visibility between threads, **not** atomicity: `count++` can still lose
  updates; use `synchronized` or atomic types.
- `StringBuffer` is synchronized; `StringBuilder` is faster and fine unless threads share it.
- Prefer immutable data and message passing over shared mutable state.

## I/O

Buffered streams cut the number of slow device calls; always close resources (try-with-resources,
`use {}` in Kotlin, `with` in Python).
