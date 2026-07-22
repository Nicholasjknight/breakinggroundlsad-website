# Launch Checklist — Breaking Ground

## Repo / org
- [x] Repo live: https://github.com/Nicholasjknight/breakinggroundlsad-website
- [ ] Create GitHub org `Breaking-Ground-LSAD` (requires captcha at https://github.com/account/organizations/new?plan=free)
- [ ] Transfer repo to `Breaking-Ground-LSAD/breakinggroundlsad-website`
- [ ] Re-enable GitHub Pages on the org repo (Settings → Pages → GitHub Actions)

## Before DNS cutover
- [ ] Replace Formspree ID in `formspree.json` and `data/site.json`, then re-run `python scripts/build_site.py`
- [ ] Confirm Zoho email `info@breakinggroundlsad.com` receives Formspree notifications
- [ ] Client approves staging site on GitHub Pages (`https://nicholasjknight.github.io/breakinggroundlsad-website/` until custom domain)
- [ ] Document current DNS (especially MX/SPF/DKIM/DMARC)

## DNS cutover
- [ ] Point only A/CNAME/AAAA for the website to GitHub Pages
- [ ] Do **not** replace the entire DNS zone blindly
- [ ] Preserve email records

## After cutover
- [ ] Confirm SSL
- [ ] Test contact form end-to-end
- [ ] Verify preserved URLs: /demolition/, /land-clearing/, /tree-removal/, /stump-removal/, /about/, /contact/
- [ ] Verify redirects from legacy post URLs
- [ ] Submit sitemap in Google Search Console
- [ ] Update Google Business Profile website link (client-owned)

## Out of scope reminders
No CRM, GBP automation, or dynamic review widgets in Phase 1.
