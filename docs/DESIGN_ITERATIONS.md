# Actual design verification
Initial Ledger Audit interface implemented and production build completed.
In-app browser inspection confirmed paper/night themes, computed scenario changes,
and the invalid-date filter. The visible default layout was reviewed.

Standalone Playwright with installed Chrome exited before page creation with an
OS permission/process error. No automated screenshots, axe results or Lighthouse
scores were produced. The required three measured critique iterations are pending;
this document does not invent defect counts or completed iterations.

To run the prepared matrix outside the restricted execution environment:
1. In web/: `npm run build`
2. `python3 -m http.server 4173 --bind 127.0.0.1 --directory dist`
3. In another terminal, in web/: `node tests/browser.mjs`
The result is saved to results/ui.json. Eight viewport/theme combinations and ten
sections are configured. A passing result must be inspected, not assumed.

## Baseline completed by user-run audit
The corrected browser harness captured 80 screens across four sizes and two themes.
All eight axe checks reported zero violations, and there were no console errors
or external requests. Scenario and filter interactions passed. Saved evidence:
results/ui-baseline.json. This is automated coverage, not human accessibility certification.

## Revision 1 — implemented, recapture pending
Inspected baseline verdict, revenue and quarantine screenshots.
1. Revenue bars had only A/S labels: add visible INR values alongside months.
2. All receipts said QUARANTINED: distinguish invalid/rejected rows from ambiguous/quarantined rows.
3. Receipt titles/filter options exposed shouting reason codes: show readable labels while preserving codes in data.
4. Filter provided no result count: add a live result count and lineage explanation.
5. Print button printed the entire investigation: restrict print output to the executive summary.
6. Summary word-count evidence was absent: show actual generated text word count.
No completed post-change audit or visual improvement is claimed until recapture.

Revision 1 recapture passed: results/ui-iteration-1.json, 80 screenshots,
zero axe violations, no console errors/external requests. Inspected tablet revenue
and scenario screenshots before revision 2.

## Revision 2 — implemented, recapture pending
1. SVG data labels shrink on tablet: increase chart text from 14 to 18 SVG units.
2. Table text forced to 12px at tablet: raise to 14px.
3. Scenario options expose internal identifiers: use explicit decision descriptions.
4. Scenario assumptions hidden below control: add persistent descriptive help and association.
5. Bounds caveat collapsed by default: show it expanded to avoid an overconfident reading.
6. Tablet navigation targets small: give links 44px minimum height and allow sidebar scrolling.
7. Product table units/ranking basis implicit: include both in its caption.
