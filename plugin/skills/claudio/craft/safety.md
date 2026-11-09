# Safety

## Safe by default

- **A tool that changes files only touches the project.** Anything outside is blocked with a
  message telling the person to do it themselves (2026-11-02). The one exception in Claudio: the
  user's own copy of this skill (2026-11-07).
- **Never undo the user's work.** Report what broke a rule; the user decides (2026-11-06).
- **Git is read-only for the AI:** suggest branch names and commit messages, never run them.
- **Locked means locked:** `.tdcg/`, the plugin's Python and hooks can't be changed by the AI, so
  it can improve the knowledge but never switch off the guard rails.

## Secrets

- Never read, print, commit or publish secrets: `.env` files, keys, tokens, `tfvars`, state files,
  wallets, personal documents.
- Don't paste a secret into a chat; if one appears, say it should be revoked.
- Secrets come from the environment or a secret store, never from the repository.

## Fail clearly

- **No fallbacks or defaults for required settings.** Missing → fail with a clear error that
  names it.
- Errors say what is wrong, where, and what to do. Every problem at once, not one per run.
- **Strict input:** check types as well as presence (text in place of a list is read letter by
  letter, and `*` then matches every file) (2026-11-06).
- Never "repair" a user's broken file; say what is accepted.

## Inputs and boundaries

- Resolve paths before comparing them, so `..` can't climb out of an allowed folder (2026-11-07).
- Treat every outside input (hook JSON, files, commands, network) as untrusted.
- Tests prove the behaviour asked for, not safety against a determined attacker: security work
  needs its own review.
