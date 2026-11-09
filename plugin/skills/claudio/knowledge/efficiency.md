# Efficiency

## Read this when

- a loop sits inside a loop, or a list grows with the input
- choosing a collection (list, set, map, queue, tree)
- strings are built in a loop
- recursion appears, or a search over a graph or tree
- errors and exceptions are designed, or memory grows

## Big O

How cost (time or memory) grows as the input grows. An O(n) algorithm on a slow machine beats an
O(n²) one on a fast machine once n is large.

| Class | Meaning | Example |
|---|---|---|
| O(1) | same cost for any n | index into an array, hash map get |
| O(log n) | the problem halves each step | binary search, balanced tree lookup |
| O(n) | one pass | scan a list |
| O(n log n) | n times log n | merge sort, heap sort |
| O(n²) | every element against every other | nested loops over the same input |
| O(2ⁿ) | doubles with each element | naive recursion with two calls (Fibonacci) |
| O(n!) | every permutation | brute force over orderings |

Rules: blocks one after another **add** (O(n + m)); nested blocks **multiply** (O(n × m)); drop
constants (O(2n) → O(n)); drop lower terms (O(n² + n) → O(n²)).

- **Amortized:** an occasional expensive step spread over many cheap ones. A growing array
  copies everything when full (O(n)), but rarely, so each append is amortized O(1).
- **Recursion:** draw the call tree and count the calls. Space is the deepest stack of waiting
  calls (Fibonacci: O(2ⁿ) time, O(n) space). Remember results (memoization) to cut repeated
  calls.

## Data structures

| Structure | Access | Insert / remove | Notes |
|---|---|---|---|
| Array | O(1) by index | O(n) in the middle | fixed size, contiguous memory |
| Dynamic array (`ArrayList`, Python `list`) | O(1) | append amortized O(1); middle O(n) | the usual default |
| Linked list | O(n) to reach i | O(1) at the ends or at a node you hold | no random access |
| Hash map / set | O(1) average | O(1) average | worst O(n) if every key collides; keys need a good hash |
| Tree map / set | O(log n) | O(log n) | sorted; balanced tree (red-black) |
| Stack (LIFO) | top only | O(1) push / pop | undo, call stack, DFS |
| Queue (FIFO) | ends only | O(1) add / remove | jobs, BFS |
| Priority queue | min/max O(1) | O(log n) | a heap, not FIFO |

- A hash table is an array of buckets; the key's hash picks the bucket; a collision adds to the
  bucket's list.
- `Map` is not a `Collection` in Java; a hash set is a hash map with dummy values.
- Membership tests in a loop: use a set, not a list (O(1) vs O(n)).
- Walk a collection with its iterator; remove during the walk only through the iterator.

## Strings

Strings are immutable. Joining with `+=` in a loop copies everything built so far each time:
1x + 2x + … + nx = O(n²). Use a builder (`StringBuilder`) or a join (`"".join(words)`): O(n).

## Graphs and trees

- **Graph:** nodes and edges. Store as an adjacency list (usual) or a V×V matrix (dense graphs).
- **DFS** O(V + E): as deep as possible first, with a stack and a "visited" mark. Path exists?
  Cycles? Topological sort.
- **BFS** O(V + E): level by level, with a queue. Shortest path in an unweighted graph.
- **Tree:** a connected graph without cycles. **Binary search tree:** left < node < right; kept
  balanced, search and insert are O(log n), skewed it degrades to O(n).
- Traversals: in-order (sorted order in a BST), pre-order (copy a tree), post-order (delete,
  sizes). Recursive sums visit each node once: O(n) time, O(height) space.

## Bits

`&` both 1 · `|` at least one · `^` different · `~` flip · `<<` shift left · `>>` signed right ·
`>>>` unsigned right. Tricks: check a bit `(n & (1 << i)) != 0`; set `n | (1 << i)`; clear
`n & ~(1 << i)`; toggle `n ^ (1 << i)`; the one number without a pair: XOR everything (`x ^ x = 0`).

## Enums

A closed set of values the compiler or checker knows. Prefer them to string or int constants.
They can carry fields and behaviour; a `switch` over an enum can warn about a missing case.

## Exceptions

- Checked (must be declared or caught: `IOException`), unchecked (runtime: `NullPointerException`),
  errors (usually unrecoverable: `OutOfMemoryError`).
- Catch only what you can handle; wrap with context and rethrow otherwise. `finally` always runs.
- Exceptions for exceptional cases, not normal control flow.

## Memory and garbage collection

- An object can be collected once nothing reachable from a root (stack variables, statics, live
  threads) points to it.
- Generational GC: most objects die young, so the young area is collected often and cheaply.
- Leaks in a GC language are references kept by mistake: caches without limits, listeners never
  removed, static collections that only grow.
