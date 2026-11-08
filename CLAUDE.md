# CLAUDE.md

Before doing anything in this repo, read in this order:
1. `TEAM_PLAN.md`: rules (section 1), who does what, deadlines.
2. `HANDOFF.md`: course requirements, methods, data plan, evaluation.
3. Course materials in `course/` (syllabus, project requirements, lectures, labs).
4. `README.md`, `CONTRIBUTIONS.md`, `docs/AI_LOG.md` (read only).

Hard rules (TEAM_PLAN.md §1 has the details; they override anything else in this repo):
- NEVER run `git commit`, `git push`, `git add` or anything else that changes git history or staging. Read-only git only. At the end of a task, list the changed files, suggest a commit message and the commands the member runs himself.
- NEVER write or edit `docs/AI_LOG.md` or `CONTRIBUTIONS.md`. The students write them; you only remind them and list the facts they need.
- Ask and explain first, then work: restate the task, explain the plan and the NLP concept behind it, wait for confirmation, work in small steps, explain the result.
- At the start of a session, find out which team member you are working with (`git config user.name`, otherwise ask). After every task, update that member's study notes in `study/<member>/` (LEARNING_LOG.md, concepts/, DEFENSE_QA.md), written as Obsidian-friendly Markdown with [[wikilinks]].
- Talk to the team in Bosnian (ijekavica); code, comments, README and paper in English.
- Never invent results, numbers, datasets or references. Seed 3004, `uv run` for every command, tune on val, never touch the test set before the configuration is locked.
