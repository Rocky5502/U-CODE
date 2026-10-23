# U-CODE: Springer Nature / Overleaf working draft (2026-10-24)

**Prospective LaTeX manuscript skeleton, NOT a submission-ready paper.**

## Official journal requirement

- Automated Software Engineering specifically requires LaTeX with
  \documentclass{sn-jnl}:
  https://link.springer.com/journal/10515/submission-guidelines
- Abstract: 150--250 words once results exist.
- Index keywords: 4--6; this shell has four.
- Single-blind review: use proper identified author data, but confirm final
  authorship and their contributions with the humans involved.
- Springer Nature template:
  https://www.overleaf.com/latex/templates/springer-nature-latex-template/myxmhdsbzkyd
- Submission CFP and deadline (2027-01-30):
  https://link.springer.com/collections/jjcfecffai

## How to use in Overleaf

1. Open the **official Springer Nature** Overleaf template linked above and
   create a project in the user's Overleaf account.
2. Retain the publisher-supplied sn-jnl.cls and bibliography style files.
3. Replace the template's main manuscript file with this main.tex and place
   references.bib beside it.
4. Compile using pdfLaTeX; check errors, missing figures, bibliography,
   publisher macros and declarations.
5. Keep one canonical manuscript source and review conflicts before syncing.
   The GitHub files are the canonical project archive until a sync direction
   and an authenticated Overleaf project are explicitly established.
6. Do not remove verified references or rewrite results without checking logs.

## Limitations

The repository does **not** vendor Springer Nature's publisher class, so
main.tex alone cannot compile from a bare empty Overleaf project; start from
the official template. Current abstract, results and declarations are
placeholders, which must be replaced by verified research/author statements.
No direct write to a user's actual Overleaf project has occurred.
