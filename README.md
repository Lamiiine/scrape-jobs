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

Updated on 2026-11-23 16:45:00 UTC

- Listings: **82**
- Sponsorship evidence confirmed: **63**
- Sponsorship evidence likely (known sponsor list): **19**
- With a salary range: **28**
- With relocation assistance in the posting: **22**

Only jobs with `sponsorship_evidence` of `confirmed` or `likely` are included.
Apply links are employer or ATS URLs. Competitor boards are not used.

| Title | Company | Location | Posted | Evidence | Apply |
|-------|---------|----------|--------|----------|-------|
| Strategy & Operations Manager | Monzo | Dublin, Ireland | 2026-11-23T15:46:51Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8411444) |
| Industry Principal, Insurance | Anthropic | New York, NY, United States | 2026-11-23T15:43:32Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5293104008) |
| Software Engineer, Model-to-Product Behavior Engineering | Anthropic | San Francisco, CA, United States | 2026-11-23T14:45:28Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5487188008) |
| Program Manager, Cloud Partners | Anthropic | San Francisco, CA, United States | 2026-11-22T19:46:05Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491573008) |
| Head of Campaign Operations | Anthropic | San Francisco, CA, United States | 2026-11-22T19:40:48Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491578008) |
| Campaign Manager | Anthropic | San Francisco, CA, United States | 2026-11-22T19:37:34Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491575008) |
| Research Engineer, Finetuning | Anthropic | San Francisco, CA, United States | 2026-11-21T12:52:27Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5489567008) |
| Manager, Applied AI Architect | Anthropic | Seoul, South Korea | 2026-11-21T12:24:21Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5480986008) |
| Research Operations, External Artifacts | Anthropic | Remote, United States | 2026-11-21T00:47:30Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490492008) |
| Commercial Counsel, GTM Strategic Alliances | Anthropic | San Francisco, CA, United States | 2026-11-20T19:48:38Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490950008) |
| Staff+ Software Engineer, Capacity Engineering | Anthropic | San Francisco, CA, United States | 2026-11-20T18:05:27Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490979008) |
| Principal Engineer Capacity/Compute | Anthropic | San Francisco, CA, United States | 2026-11-20T18:05:21Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490978008) |
| Senior Third Party Risk Manager | Monzo | Remote, London, United Kingdom | 2026-11-20T18:01:26Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8195253) |
| GTM Strategy & Operations Business Partner | Anthropic | New York, NY, United States | 2026-11-20T17:48:34Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5485591008) |
| Research Engineer, Beneficial Deployments | Anthropic | San Francisco, CA, United States | 2026-11-20T16:38:57Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5485188008) |
| Strategic Account Executive, Hedge Funds | Anthropic | New York, NY, United States | 2026-11-20T15:42:00Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490572008) |
| Strategic Account Executive, HCLS | Anthropic | New York, NY, United States | 2026-11-20T14:48:51Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5480893008) |
| Strategic Account Executive, Financial Services | Anthropic | New York, NY, United States | 2026-11-20T14:48:35Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5480875008) |
| Engineering Manager, Privacy Infrastructure | Anthropic | New York, NY, United States | 2026-11-20T03:04:34Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490122008) |
| Applied AI Architect, Beneficial Deployment | Anthropic | Sydney, New South Wales, Australia | 2026-11-20T02:35:45Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5486780008) |
| Corporate Network Engineer | Anthropic | Remote | 2026-11-20T01:57:48Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5489564008) |
| Finance Systems Production Support Lead | Anthropic | San Francisco, CA, United States | 2026-11-19T23:24:42Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5483403008) |
| Head of Community Relations, Compute | Anthropic | San Francisco, CA, United States | 2026-11-19T17:30:20Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5456315008) |
| Strategic Account Executive, Tech | Anthropic | San Francisco, CA, United States | 2026-11-19T17:22:29Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5138549008) |
| AWS Partnerships Lead | Anthropic | London, England, United Kingdom | 2026-11-19T16:04:53Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5486656008) |
| Community Engagement Manager, Data Centres (Canada) | Anthropic | British Columbia, Canada | 2026-11-19T14:43:03Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5486907008) |
| Senior Treasury Product Control Analyst | Monzo | Remote, Cardiff, United Kingdom | 2026-11-19T10:00:42Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8398665) |
| Sales Director | Anthropic | Seoul, South Korea | 2026-11-19T05:55:15Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5474013008) |
| Applied AI Engineer, Commercial | Anthropic | San Francisco, CA, United States | 2026-11-18T16:26:55Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5483945008) |
| Staff Brand Designer | Monzo | London, United Kingdom | 2026-11-18T13:08:57Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8396136) |
| Enterprise Account Executive, Enterprise Account Executive, Hedge Funds & Quantitative Trading | Anthropic | London, England, United Kingdom | 2026-11-18T12:14:25Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484875008) |
| Strategic Pursuits Lead, DACH | Anthropic | Munich, Bavaria, Germany | 2026-11-18T11:09:34Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5486380008) |
| [Paris] Applied AI Architect, Industries | Anthropic | Paris, France | 2026-11-18T10:25:06Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5482967008) |
| Senior Regulatory Reporting Analyst | Monzo | London, United Kingdom | 2026-11-18T09:25:34Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385865) |
| Compute Capacity Strategy & Operations | Anthropic | San Francisco, CA, United States | 2026-11-17T23:52:27Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5485582008) |
| Developer Relations, Platform | Anthropic | San Francisco, CA, United States | 2026-11-17T23:10:36Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5206870008) |
| Web Strategy Lead | Anthropic | San Francisco, CA, United States | 2026-11-17T17:23:09Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5465637008) |
| Partner Marketing Manager, Cloud Partners EMEA | Anthropic | London, England, United Kingdom | 2026-11-17T13:28:19Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5473999008) |
| Software Engineer, Datacenter Server Lifecycle | Anthropic | Remote, United States | 2026-11-17T01:53:14Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5484171008) |
| Head of PMO, Workplace | Anthropic | San Francisco, CA, United States | 2026-11-17T01:27:33Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5482207008) |

_Showing 40 of 82. The full catalog is `data/latest-jobs.json`._
<!-- END OF JOB LISTINGS -->
















