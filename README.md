# Visa sponsorship job scraper

Daily scraper for [visajobs.xyz](https://visajobs.xyz). It reads employer ATS boards (Greenhouse, Lever, Ashby), keeps a job only when the posting or a known sponsor list supports visa sponsorship, and can publish that catalog to `relocate-with-us/relocate-with-us.github.io`.

A job is tagged visa-sponsored only with `sponsorship_evidence`:

- `confirmed` — the title or description offers sponsorship, and that sentence is not a refusal
- `likely` — the employer is on the short known-sponsor list and the posting does not refuse sponsorship
- `unverified` — dropped, not published

Apply links are the employer or ATS URL. Competitor boards (Arbeitnow, Relocate.me, VisaSponsor.jobs, Jaabz, EuropeVisaJobs, and similar) are not used. Each record has `valid_through` (posting date plus 45 days, extended while the employer listing is still open), a location/address when the board provides one, and salary when a range is present.

The site update runs only when the Actions secret `SITE_GITHUB_TOKEN` is set. Without it, this repository still records `data/latest-jobs.json` and the workflow succeeds. See the workflow log for the exact token permissions. The public site has not deployed since 13 August 2026 because its own bot push cannot start **Build and Deploy**, and `gh workflow run deploy.yml` returns HTTP 403.

<!-- START OF JOB LISTINGS -->
# Visa sponsorship jobs

Updated on 2026-11-18 16:32:26 UTC

- Listings: **105**
- Sponsorship evidence confirmed: **90**
- Sponsorship evidence likely (known sponsor list): **15**
- With a salary range: **40**
- With relocation assistance in the posting: **49**

Only jobs with `sponsorship_evidence` of `confirmed` or `likely` are included.
Apply links are employer or ATS URLs. Competitor boards are not used.

| Title | Company | Location | Evidence | Valid through | Apply |
|-------|---------|----------|----------|---------------|-------|
| Regulatory Project Manager | N26 | Berlin, Germany | confirmed | 2027-01-02 | [Apply](https://n26.com/en-eu/careers/positions/8398981?gh_jid=8398981) |
| Account Executive, Quantitative Trading & Investing | Anthropic | London, United Kingdom | confirmed | 2027-01-02 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484875008) |
| Applied AI Engineer, Commercial | Anthropic | San Francisco, CA, United States | confirmed | 2027-01-02 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5483945008) |
| [Paris] Applied AI Architect, Industries | Anthropic | Paris, France | confirmed | 2027-01-02 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5482967008) |
| Strategic Pursuits Lead, DACH | Anthropic | Munich, Germany | confirmed | 2027-01-02 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5486380008) |
| Senior Regulatory Reporting Analyst | Monzo | London, United Kingdom | likely | 2027-01-02 | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385865) |
| Staff Brand Designer | Monzo | London, United Kingdom | likely | 2027-01-02 | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8396136) |
| Compute Capacity Strategy & Operations | Anthropic | San Francisco, CA, United States | confirmed | 2027-01-01 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5485582008) |
| Developer Relations, Platform | Anthropic | San Francisco, CA, United States | confirmed | 2027-01-01 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5206870008) |
| GTM Activations Strategy Lead | Anthropic | San Francisco, CA, United States | confirmed | 2027-01-01 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5483359008) |
| Partner Marketing Manager, Cloud Partners EMEA | Anthropic | London, United Kingdom | confirmed | 2027-01-01 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5473999008) |
| Web Strategy Lead | Anthropic | San Francisco, CA, United States | confirmed | 2027-01-01 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5465637008) |
| Integrated Marketing Lead, Business Banking | Monzo | Cardiff, United Kingdom | likely | 2027-01-01 | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8333519) |
| Applied AI Architect, Beneficial Deployments (Non-Profits) | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484035008) |
| Docs Lead, Platform | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5482310008) |
| GTM Strategy & Operations - Strategic Planning | Anthropic | New York City, NY, United States | confirmed | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481842008) |
| Head of PMO, Workplace | Anthropic | New York City, NY, United States | confirmed | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5482207008) |
| Research Engineer, AI Monitoring | Anthropic | London, United Kingdom | confirmed | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5477416008) |
| Software Engineer, Datacenter Server Lifecycle | Anthropic | Remote, United States | confirmed | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484171008) |
| Staff+ Software Engineer, Deployment | Anthropic | London, United Kingdom | confirmed | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484144008) |
| Creative Studio Resource Manager - Creative Ops | Monzo | Cardiff, United Kingdom | likely | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8393062) |
| Global Director of Sales | Monzo | London, United Kingdom | likely | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8188282) |
| Product Operations Manager | Monzo | London, United Kingdom | likely | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8392439) |
| Sales Manager | Monzo | London, United Kingdom | likely | 2026-12-31 | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385191) |
| Corporate Counsel, Public Reporting | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-29 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5462511008) |
| Engineering Manager, Billing Platform | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-29 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5469291008) |
| Manager, Enterprise Sales - Industries, ANZ | Anthropic | Sydney, Australia | confirmed | 2026-12-29 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5473344008) |
| CMC & Manufacturing Lead, Life Sciences | Anthropic | Remote, United States | confirmed | 2026-12-28 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481396008) |
| GTM Narrative Lead | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-28 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481671008) |
| Partner Marketing Lead, APAC | Anthropic | Sydney, Australia | confirmed | 2026-12-28 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5473362008) |
| Staff+ Software Engineer, Consumer | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-28 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5477652008) |
| Staff Software Engineer, Internal Products | Anthropic | Remote | confirmed | 2026-12-28 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481096008) |
| Technical Program Manager, Life Sciences Research (Genetic Medicine) | Anthropic | Boston, MA, United States | confirmed | 2026-12-28 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481980008) |
| Interim Director of Financial Operations & Control | Monzo | Cardiff, United Kingdom | likely | 2026-12-28 | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385203) |
| Commercial Activation Lead | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-27 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5478939008) |
| Customer Marketing Lead, Startups Program | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-27 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5477150008) |
| External Affairs, Southeast Asia | Anthropic | Singapore | confirmed | 2026-12-27 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5479890008) |
| Partner Support Operations Lead | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-27 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5453322008) |
| Resale Operations Lead | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-27 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5468548008) |
| Staff Software Engineer, Support Technology | Anthropic | San Francisco, CA, United States | confirmed | 2026-12-27 | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5478876008) |

_Showing 40 of 105. The full catalog is `data/latest-jobs.json`._
<!-- END OF JOB LISTINGS -->



