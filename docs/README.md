<img src="../logo.png" alt="ClaudioXP logo: a rooster" width="110" align="right">

# ClaudioXP docs

ClaudioXP is a Claude Code plugin that puts guard rails on AI-assisted development. You work in
small TDCG cycles (Test-Driven Code Generation): Claude writes the code fast, and you decide what
is right. Hooks enforce each phase's rules, so Claude can't skip a step, change a locked test, or
commit for you.

> The AI generates. The human decides what is right and what is not.

## Is it for you?

ClaudioXP is for software engineers who want AI's speed and keep responsibility for what they
ship.

- **You need the fundamentals.** It guides an engineer; it does not stand in for one. If you
  can't judge a change, ClaudioXP can't help you.
- **Know your paradigm:** object-oriented, functional or structured, and why.
- **You don't need to be an expert in the language.** Bring the engineering know-how, and ask
  Claude to explain the language as you go.
- **It is not for "vibe" coding.** Every cycle stops for your decision: the spec, the tests, the
  review, the commit.

## The pages

1. [Install](install.md): two commands, then turn it on in a project.
2. [Your first cycle](first-cycle.md): from plan to commit, with what to expect at each step.
3. [Phases and cycle types](phases.md): what each phase allows and how you move between them.
4. [Plan and config](plan-and-config.md): the two files that drive a project.
5. [Troubleshooting](troubleshooting.md): the usual problems and their fixes.

Want a full worked example? Try one of the demos:
[TypeScript in VS Code](../demos/typescript/TRY-IT-YOURSELF-TYPESCRIPT.md) or
[Java in IntelliJ](../demos/java/TRY-IT-YOURSELF-JAVA.md).

**Names:** ClaudioXP is the project. The plugin and its commands are called `claudio`
(`claudio@claudio-plugin`, `/claudio:next`), and its messages start with `Claudio:`.
