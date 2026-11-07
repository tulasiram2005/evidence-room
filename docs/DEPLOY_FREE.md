# Free static deployment

Live site: https://evidence-room-tawny.vercel.app

Verified 2026-11-07: RAM's projects displays Hobby in the Vercel dashboard.
Project evidence-room uses repository tulasiram2005/evidence-room, root `web`,
Vite build `npm run build`, output `dist`. No backend, database, environment
secrets, paid add-ons or billing changes were configured.

Deployment dpl_FbEWGA9yfU1CVj78MucKzmxYpHP1 reached READY from commit d964f4d.
HTTP 200, security headers and matching local JS/CSS hashes are recorded in
`results/hosted_smoke.json`. The hosted page was inspected; hosted interaction
checks were interrupted by browser permission loss and are not claimed complete.

Git pushes now trigger Vercel builds. Build locally and run tests before pushing.
Run `python tools/build_gate.py` after the web build to exclude raw files and secrets.
Only static output is published; repository CSV files are not served by the site.

Alternative: Cloudflare Pages Free can publish `web/dist`; `_headers` is included.
Re-check account eligibility and limits before switching hosts. No Cloudflare
project has been created. Never enable billing to work around free-tier limits.
