# Visa sponsorship job scraper

Daily scraper for [visajobs.xyz](https://visajobs.xyz). It reads employer ATS boards (Greenhouse, Lever, Ashby), keeps a job only when the posting or a known sponsor list supports visa sponsorship, and can publish that catalog to `relocate-with-us/relocate-with-us.github.io`.

A job is tagged visa-sponsored only with `sponsorship_evidence`:

- `confirmed` — the title or description offers sponsorship, and that sentence is not a refusal
- `likely` — the employer is on the short known-sponsor list and the posting does not refuse sponsorship
- `unverified` — dropped, not published

Apply links are the employer or ATS URL. Competitor boards (Arbeitnow, Relocate.me, VisaSponsor.jobs, Jaabz, EuropeVisaJobs, and similar) are not used. Each record stores the employer's posted timestamp (`posted_at`, not a date pinned to noon), the posting text (`body`), `valid_through` (posting date plus 45 days, extended while the employer listing is still open), a location/address when the board provides one, and salary when a range is present. Jobs older than 90 days are left off the board.

The site update runs only when the Actions secret `SITE_GITHUB_TOKEN` is set. Without it, this repository still records `data/latest-jobs.json` and the workflow succeeds. See the workflow log for the exact token permissions.

New roles are also posted to Telegram and LinkedIn when those secrets are set. Each channel gets one digest a day, with at most five roles, and a role is never posted twice (`data/posted-ids.json`). Set the workflow input “Preview the Telegram and LinkedIn posts” (or `DRY_RUN_SOCIAL=1`) to print the message without sending it. The wording lives in `scraper/post_template.py`. LinkedIn and X do not offer a public job search, so they are distribution channels, not sources. Extra roles come from the monthly Hacker News “Who is hiring?” thread, where the employer writes the visa line and links to their own site.

### Telegram

1. Open @BotFather, send `/newbot`, and copy the token.
2. Add the bot as an administrator of the channel (`@visa_sponsored_jobss`).
3. On Lamiiine/scrape-jobs, add Actions secrets `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (`@visa_sponsored_jobss`).

### LinkedIn company page

LinkedIn must approve an app before it can post. Create one at https://www.linkedin.com/developers/apps, request the Community Management API, and complete the one-time sign-in described in the workflow log (`LINKEDIN IS NOT CONNECTED`). Secrets: `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REFRESH_TOKEN`, `LINKEDIN_ORGANIZATION_ID`. The daily run refreshes the access token itself.

<!-- START OF JOB LISTINGS -->
# Visa sponsorship jobs

Updated on 2026-11-19 12:51:46 UTC

- Listings: **97**
- Sponsorship evidence confirmed: **71**
- Sponsorship evidence likely (known sponsor list): **26**
- With a salary range: **35**
- With relocation assistance in the posting: **25**

Only jobs with `sponsorship_evidence` of `confirmed` or `likely` are included.
Apply links are employer or ATS URLs. Competitor boards are not used.

| Title | Company | Location | Posted | Evidence | Apply |
|-------|---------|----------|--------|----------|-------|
| Senior Treasury Product Control Analyst | Monzo | Remote, Cardiff, United Kingdom | 2026-11-19T10:00:42Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8398665) |
| Sales Director | Anthropic | Seoul, South Korea | 2026-11-19T05:55:15Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5474013008) |
| Applied AI Engineer, Commercial | Anthropic | San Francisco, CA, United States | 2026-11-18T16:26:55Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5483945008) |
| Staff Brand Designer | Monzo | London, United Kingdom | 2026-11-18T13:08:57Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8396136) |
| Account Executive, Quantitative Trading & Investing | Anthropic | London, England, United Kingdom | 2026-11-18T12:14:25Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484875008) |
| Strategic Pursuits Lead, DACH | Anthropic | Munich, Bavaria, Germany | 2026-11-18T11:09:34Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5486380008) |
| [Paris] Applied AI Architect, Industries | Anthropic | Paris, France | 2026-11-18T10:25:06Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5482967008) |
| Senior Regulatory Reporting Analyst | Monzo | London, United Kingdom | 2026-11-18T09:25:34Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385865) |
| Compute Capacity Strategy & Operations | Anthropic | San Francisco, CA, United States | 2026-11-17T23:52:27Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5485582008) |
| Developer Relations, Platform | Anthropic | San Francisco, CA, United States | 2026-11-17T23:10:36Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5206870008) |
| GTM Activations Strategy Lead | Anthropic | San Francisco, CA, United States | 2026-11-17T20:20:48Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5483359008) |
| Web Strategy Lead | Anthropic | San Francisco, CA, United States | 2026-11-17T17:23:09Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5465637008) |
| Partner Marketing Manager, Cloud Partners EMEA | Anthropic | London, England, United Kingdom | 2026-11-17T13:28:19Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5473999008) |
| Integrated Marketing Lead, Business Banking | Monzo | Remote, Cardiff, United Kingdom | 2026-11-17T09:35:04Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8333519) |
| Software Engineer, Datacenter Server Lifecycle | Anthropic | Remote, United States | 2026-11-17T01:53:14Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484171008) |
| Head of PMO, Workplace | Anthropic | San Francisco, CA, United States | 2026-11-17T01:27:33Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5482207008) |
| Staff+ Software Engineer, Deployment | Anthropic | London, England, United Kingdom | 2026-11-17T00:33:44Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484144008) |
| Applied AI Architect, Beneficial Deployments (Non-Profits) | Anthropic | San Francisco, CA, United States | 2026-11-16T23:14:39Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484035008) |
| Docs Lead, Platform | Anthropic | San Francisco, CA, United States | 2026-11-16T22:11:44Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5482310008) |
| Research Engineer, AI Monitoring | Anthropic | London, England, United Kingdom | 2026-11-16T21:28:41Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5477416008) |
| Creative Studio Resource Manager - Creative Ops | Monzo | Remote, Cardiff, United Kingdom | 2026-11-16T19:06:54Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8393062) |
| GTM Strategy & Operations - Strategic Planning | Anthropic | New York, NY, United States | 2026-11-16T18:10:36Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481842008) |
| Sales Manager | Monzo | London, United Kingdom | 2026-11-16T11:12:33Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385191) |
| Product Operations Manager | Monzo | London, United Kingdom | 2026-11-16T10:13:12Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8392439) |
| Global Director of Sales | Monzo | London, United Kingdom | 2026-11-16T09:36:46Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8188282) |
| Engineering Manager, Billing Platform | Anthropic | San Francisco, CA, United States | 2026-11-14T20:19:44Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5469291008) |
| Corporate Counsel, Public Reporting | Anthropic | New York, NY, United States | 2026-11-14T05:41:15Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5462511008) |
| Manager, Enterprise Sales - Industries, ANZ | Anthropic | Sydney, New South Wales, Australia | 2026-11-14T05:18:57Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5473344008) |
| Technical Program Manager, Life Sciences Research (Genetic Medicine) | Anthropic | San Francisco, CA, United States | 2026-11-13T21:57:59Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481980008) |
| GTM Narrative Lead | Anthropic | San Francisco, CA, United States | 2026-11-13T21:52:16Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481671008) |
| CMC & Manufacturing Lead, Life Sciences | Anthropic | Remote, United States | 2026-11-13T21:43:08Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481396008) |
| Staff+ Software Engineer, Consumer | Anthropic | San Francisco, CA, United States | 2026-11-13T18:51:11Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5477652008) |
| Staff Software Engineer, Internal Products | Anthropic | San Francisco, CA, United States | 2026-11-13T17:59:01Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5481096008) |
| Partner Marketing Lead, APAC | Anthropic | Sydney, New South Wales, Australia | 2026-11-13T17:32:06Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5473362008) |
| Interim Director of Financial Operations & Control | Monzo | Remote, Cardiff, United Kingdom | 2026-11-13T13:12:21Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385203) |
| External Affairs, Southeast Asia | Anthropic | Singapore | 2026-11-13T04:19:56Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5479890008) |
| Commercial Activation Lead | Anthropic | San Francisco, CA, United States | 2026-11-13T01:32:22Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5478939008) |
| Customer Marketing Lead, Startups Program | Anthropic | San Francisco, CA, United States | 2026-11-12T23:47:11Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5477150008) |
| Partner Support Operations Lead | Anthropic | San Francisco, CA, United States | 2026-11-12T21:58:14Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5453322008) |
| Tech Lead Manager, Growth Data Science | Anthropic | San Francisco, CA, United States | 2026-11-12T21:54:18Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5478799008) |

_Showing 40 of 97. The full catalog is `data/latest-jobs.json`._
<!-- END OF JOB LISTINGS -->










