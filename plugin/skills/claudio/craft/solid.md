# SOLID

Managing **coupling and cohesion**: related things together (cohesion), unrelated things kept from
leaning on each other's insides (coupling). Each principle below is a check you can run on a diff.

## Single responsibility

One reason to change. A module answers to one actor or part of the business.

- Check: if you need "and" to describe it, split it.
- Check: would two different people ask to change it for unrelated reasons?
- Example: `Invoice` that totals, saves and formats a PDF → `Invoice`, `InvoiceRepository`,
  `InvoicePdfFormatter`.

## Open/closed

Open for extension, closed for modification: add behaviour with new parts, not by editing parts
that already work and are tested.

- Check: does each new case mean editing the same `if`/`switch` again?
- Fix: each case knows its own behaviour (an interface, an enum method, a table), so the old part
  never changes.

## Liskov substitution

A subtype must work wherever the base type is expected, without breaking correctness.

- Check: does a subclass refuse a call, throw "not supported", demand more from callers, or
  promise less than the base?
- Fix: a different type, or composition instead of inheritance.

## Interface segregation

Don't force a class to depend on methods it doesn't use. Many small, focused interfaces beat one
large one.

- Check: are there empty or "not implemented" methods just to satisfy an interface?

## Dependency inversion

High-level rules don't depend on low-level details; both depend on an abstraction.

- Check: does a rule create its own database client, HTTP client or file reader (`new
  EmailSender()` inside the service)?
- Fix: pass it in through the constructor behind an interface; the detail can then be swapped or
  mocked in a test.

## OOP underneath

- **Abstraction:** expose the *what*, hide the *how*. Callers know the contract, not the
  implementation.
- **Encapsulation:** state is private; expose behaviour that works on it rather than raw
  getters/setters.
- **Inheritance** couples tightly: a change in the parent ripples into every child, and deep
  hierarchies get hard to follow. **Favour composition** ("has-a" field) unless the "is-a" is
  real and stable.
- **Polymorphism:** one interface, many implementations, chosen at runtime.
- Abstract class = related types sharing state and some implementation; interface = a capability
  unrelated types opt into.

## Dependency injection

- A class declares what it needs; something outside gives it. That is Inversion of Control.
- **Constructor injection** is preferred: dependencies can be final, and the class can be tested
  with plain construction and mocks, no container.
- Setter injection for truly optional parts. Avoid field injection: the class can't be built
  without reflection or a running container.
