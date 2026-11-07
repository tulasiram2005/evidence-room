# Optional deployment (not yet performed)
The challenge does not grade deployment. No hosted account is required for the core.

Before any publication, verify current account plan and remaining free allowance;
never enable billing or use paid resources. Use Cloudflare Pages Free or Vercel
Hobby only if current eligibility permits. Re-check terms before use.

Build locally: `python analysis.py`, then `cd web && npm ci && npm run build`.
Publish only web/dist, never the repository root or raw/clean CSVs.
Cloudflare Pages: connect the private repository; build the root pipeline and web
bundle, output web/dist. Configure a compatible Python/Node environment.
Vercel: use the same build/output configuration and translate public/_headers into
vercel.json response headers. Do not assume Cloudflare _headers applies on Vercel.
No runtime variables or credentials belong in the static bundle.

Deployment automation, host billing validation and hosted response-header checks
remain pending. A built website is not proof of a correct hosted configuration.
