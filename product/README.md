# product/

PRDs and product improvements for El Club de las Emprendedoras: the **what and why** of a change
before anyone builds it. `CLAUDE.md` and the folder READMEs (`site/`, `brand/`, `newsletter/`)
cover the **how**. Nothing here is deployed: Vercel only serves `site/`.

## Index

| # | Initiative | Status | Branch / PR |
|---|---|---|---|
| [0001](0001-club-2027/prd.md) | Landing: from "taller de 8 semanas" to "el club 2027" | draft | `docs/club-2027-prd` |

Keep this table current. It's the first thing an agent reads to see what's planned, in progress or shipped.

## Layout

```
product/
  README.md            this file: rules + index
  _template/           copy it to start a new one
  NNNN-slug/
    prd.md             the requirements: stable, edited only when the requirements change
    log.md             append-only work log: progress, decisions (with the why), next steps
    assets/            optional: screenshots, mock-ups, research exports
```

- **Number + slug:** `0002-recetas-search`, zero-padded, kebab-case, never reused or renamed.
- **Two files, two jobs** (the same split as the personal `~/prd` system: `task.md` + `sessions.md`):
  `prd.md` says what done looks like and doesn't change because work happened. `log.md` grows
  with each session, newest entry last, so a fresh session can pick it up cold.

## Status lifecycle

Set in `prd.md` front matter and mirrored in the index:

`draft` → `approved` → `in-progress` → `shipped`. It can also end as `dropped` or `superseded`
(write `superseded_by: NNNN`).

- **draft:** open questions remain. Agents may research and refine it but **don't implement**.
- **approved:** the owner answered the open questions in chat or in the log. Implementation can start.
- **shipped:** merged and checked on production. Tick the acceptance criteria and link the PR.
- Never delete a PRD. When the plan changes a lot, write a new one that supersedes it.

## Writing rules (for humans and agents)

1. **Write for a cold start.** Someone with no chat history should be able to act on it. Name
   exact files, sections and selectors (`site/index.html` → `#taller`). Never write "as discussed".
2. **Problem, user, done, out of scope.** Every PRD states the problem, who it's for, checkable
   acceptance criteria and explicit non-goals. A chat prompt usually skips those four.
3. **Open questions carry a recommendation and an owner.** "Q: X? Recommended: Y. Owner: Manu."
   The agent proposes, the person decides. Answers go into `log.md` as decisions.
4. **Decisions are logged with the why.** `log.md` → *Decisions*: what was decided, by whom,
   and why. These are lightweight ADRs: don't rewrite past entries; add a new one that reverses them.
5. **Copy drafts live in the PRD.** Final copy goes to `site/` and `brand/voice.md` when it ships,
   following `brand/voice.md` (Mexican Spanish, *tú*, no hype, no jargon).
6. **Link sources, don't paste them.** Notion pages, Figma, the Sheet: link and summarise only
   what the PRD needs. **This repo is public:** no secrets, no private data about members,
   no internal numbers. Private context goes in `~/prd`.
7. **Keep it short.** One page of requirements beats ten of narrative. If it grows, split it.

## Workflow

1. Start: copy `_template/` to `NNNN-slug/`, fill `prd.md` (status `draft`), add an index row,
   and open a docs-only PR (branch `docs/<slug>`) so it can be reviewed and commented on.
2. Approve: the owner answers the open questions. Log the decisions and set status `approved`.
3. Build: on its own branch (CLAUDE.md → Workflow), with a prompt like *"Implement
   product/0001-club-2027/prd.md"*. The PR description links the PRD; each session appends to `log.md`.
4. Ship: tick the acceptance criteria, set `shipped`, link the PR, update the index.

Sources for these conventions: spec-driven development (Kiro's per-feature
`requirements.md`/`design.md`/`tasks.md`, GitHub Spec Kit), MADR-style decision records
(statuses, append-don't-rewrite), and Claude Code practice (keep `CLAUDE.md` short and point to
docs; use plan files as the handoff between planning and implementing sessions).
