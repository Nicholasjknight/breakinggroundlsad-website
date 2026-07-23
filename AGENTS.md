# Breaking Ground Land Services and Demolition — Agent Instructions

**Domain:** `breakinggroundlsad.com`  
**Site folder:** `E:\All Client Websites\Breaking Ground Land Services and Demolition`  
**GitHub org:** `Breaking-Ground-Land-Services`  
**GitHub repo:** `Breaking-Ground-Land-Services/breakinggroundlsad-website`  
**Org profile:** https://github.com/Breaking-Ground-Land-Services  
**Preview:** https://breaking-ground-land-services.github.io/breakinggroundlsad-website/  
**Pages:** GitHub Pages → custom domain `breakinggroundlsad.com` (see LAUNCH-CHECKLIST.md)

## Public contact

- Phone: `(863) 899-9717`
- Email: `info@breakinggroundlsad.com` (Zoho domain email — do **not** publish Gmail)
- HQ area: Kathleen / Lakeland, Polk County, Florida
- Legal: Breaking Ground Land Services and Demolition LLC (formed 2024)
- Owners: Guy S. McMillen & Andrew S. McMillen (father-and-son)

## Positioning (hard rules)

1. **Demolition first:** Mobile homes, sheds, barns, decks, light structures, debris removal.
2. **No GC claims:** Never say “licensed demolition contractor,” “fully licensed,” “general contractor,” or unrestricted residential/commercial building demolition.
3. **Safe demo wording:** Smaller demolition and structure removal; permit requirements vary; coordinate permitting as required by jurisdiction.
4. **Secondary services:** Land clearing, tree/stump removal, pond/drainage earthwork, grading, storm cleanup — real capabilities, lighter SEO emphasis.
5. **Service area:** Based in Kathleen serving Central Florida; larger demolition and site jobs considered statewide by scope.
6. **Founded 2024** with decades of heavy-equipment experience (Andrew since ~1975). Never imply the LLC has operated since 1975.

## Faith Works firewall (partner priority)

Faith Works Outdoor Services (`faithworksclearing.com`) is a business partner. Do **not** steal their customers:

- Do not build competing forestry-mulching / pond-bank / ditch-clearing SEO pages for Auburndale, Winter Haven, Lake Alfred, etc.
- On overlapping cities, lead with mobile-home / light demolition; land clearing is secondary only.
- Prefer sending mulching / pond / ditch clearing work toward Faith Works when appropriate.

## Forms

- Formspree estimate form (see `formspree.json`). Update form ID after Formspree account setup.
- Thank-you page: `/thank-you/`

## Build scripts

```powershell
python scripts/build_site.py
python scripts/build_sitemap.py
```

## DNS cutover

Change only website A/CNAME records. Preserve MX, SPF, DKIM, DMARC for Zoho email.
