# Plan and config

Two files in `.tdcg/` drive a project. Claude writes them with you in PLAN; `/claudio:next`
checks them and lists every problem. The full rules are in the schemas:
[`plan.schema.json`](../plugin/tdcg/schema/plan.schema.json) and
[`config.schema.json`](../plugin/tdcg/schema/config.schema.json).

## The plan: `.tdcg/plan.json`

What you build, why, and the small cycles that get there.

```json
{
  "title": "ID generator",
  "status": "active",
  "goal": "One shared ID generator, so two parts of the app never hand out the same ID.",
  "cycles": [
    {
      "key": "1",
      "type": "behaviour",
      "what": "next() returns a higher number each time",
      "done": false,
      "notes": ["One instance only: getInstance() always returns the same object."],
      "files": ["src/**", "spec/**"]
    }
  ]
}
```

| Field | What it is |
|---|---|
| `title` | Letters, digits and single spaces. Becomes the file name in `.tdcg/done/`. |
| `status` | `"active"` or `"done"`. |
| `goal` | What you build and why, in a few lines. |
| `cycles` | At least one cycle, in order. The current one is the first with `done: false`. |

Each cycle:

| Field | What it is |
|---|---|
| `key` | A number from 1, optionally with one lowercase letter: `"1"`, `"2"`, `"2b"`. Unique. |
| `type` | Optional, default `behaviour`. See [cycle types](phases.md#cycle-types). |
| `what` | What this cycle builds, in a few words. |
| `done` | `true` or `false`. Set by ClaudioXP after COMMIT, never by hand. |
| `notes` | Details and edge cases, enough to start SPECIFY. |
| `files` | At least one file pattern this cycle may change, e.g. `"src/**"`. |

**Good cycles are small:** one behaviour each. If a cycle needs "and" to describe it, split it.
List every file it may touch, tests and shared ones included; a file left out means going back
to PLAN.

## The config: `.tdcg/config.json`

How your project runs its tests, and which files are tests.

```json
{
  "test_command": "npm test --silent",
  "test_files": ["spec/**"],
  "claude_free_writing_files": ["docs/**", "notes.md"]
}
```

| Field | What it is |
|---|---|
| `test_command` | The command that runs your tests, e.g. `./gradlew test`. Any command works (build, lint and tests chained with `&&`); only its exit status counts. |
| `test_files` | At least one file pattern that says which files are tests. |
| `claude_free_writing_files` | Optional. File patterns Claude may change in any phase, tests included. `.tdcg/` stays locked. |

Paths start from the project folder. Patterns work like shell wildcards, but `*` also matches
across folders: `src/*` covers everything under `src/`.

## Done plans

When the last cycle is done, `/claudio:next` moves the plan to `.tdcg/done/` and goes back to
PLAN, ready for the next one.
