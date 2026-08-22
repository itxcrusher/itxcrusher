Quarterly profile review. Opened automatically by `.github/workflows/profile-review.yml`.

A profile rots quietly. Nothing on this list is urgent, and that is exactly why it needs
a scheduled reminder. Budget ten minutes.

## Broken things (2 min)

- [ ] Open <https://github.com/itxcrusher> logged out, in **light mode**, on a **phone**.
      Look at it. Every past defect on this profile was visible and nobody was looking.
- [ ] Does the snake render? If not, the `profile` workflow has been failing and the
      failure issue should already be open. Check the Actions tab.
- [ ] Is the `_Generated YYYY-MM-DD_` stamp under `// what is public` less than two
      weeks old? If it is older, the generator is dead and the block is lying.
- [ ] Click every link in the README. The two domains, the repositories tab, the
      ripple-proof walkthrough, the four dbt PRs, both upstream PRs.

## True things (4 min)

- [ ] Run the command the README tells strangers to run, from a **fresh clone**:
      `git clone https://github.com/itxcrusher/ripple-proof && cd ripple-proof && PYTHONPATH=src python -S -m lineage_agent.cli demo`
      It must still print `CAMPAIGN AUDIT: PASSED`. If it does not, that block comes out
      of the README the same day. It is the whole credibility bet.
- [ ] Are the two upstream PRs still open? If one merged, the generated block now says
      "Some have since been merged" by itself, but the `// operating stack` prose still
      says "Upstream, open" and needs a hand edit.
- [ ] Does every line of the `operating stack` fence still have a public artifact behind
      it? Two lines are one repo deep: `Kubernetes` rests on `elunic-challenge-devops`,
      and `Azure` rests on `azure-devops-demo`. If either goes private or archived, that
      line comes out.
- [ ] Any new public repo worth the `showcase` topic? Any showcased repo that no longer
      deserves it? Removing the topic is the whole edit; the block updates itself.

## Descriptions (3 min)

- [ ] Showcased repo descriptions are injected verbatim into the README. They must be
      **plain ASCII**. A curly quote or an en dash in one of them triggers a warning in
      the render step and gets silently folded. Fix the repo field, not the generator.
- [ ] Does each showcased description still describe what the repo actually contains?
      This is the drift that matters: the description is the only thing most visitors
      read.

## Dependencies (1 min)

- [ ] `Platane/snk` still maintained? It is the only third-party action left, and it
      runs in a `contents: read` job so the blast radius is a missing snake.
- [ ] Any new file under `assets/`? It must pass R6/R7/R8 in `scripts/check_readme.py`.
      Do not add an image that carries a fact.

## The standing rule

Everything on the page is either true and checkable, or it is not on the page. If a
claim cannot survive a stranger clicking it, delete the claim rather than softening it.
