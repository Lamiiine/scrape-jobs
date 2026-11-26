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

Updated on 2026-11-26 15:58:25 UTC

- Listings: **51**
- Sponsorship evidence confirmed: **43**
- Sponsorship evidence likely (known sponsor list): **8**
- With a salary range: **16**
- With relocation assistance in the posting: **27**

Only jobs with `sponsorship_evidence` of `confirmed` or `likely` are included.
Apply links are employer or ATS URLs. Competitor boards are not used.

| Title | Company | Location | Posted | Evidence | Apply |
|-------|---------|----------|--------|----------|-------|
| Area Lead, Data Center Security Operations (NORAM - North East) | Anthropic | New York, NY, United States | 2026-11-25T19:04:37Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491501008) |
| AFC Senior Associate / SAR Delegate | N26 | Paris, France | 2026-11-25T14:35:49Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8414044?gh_jid=8414044) |
| Staff Backend Engineer | Monzo | London, United Kingdom | 2026-11-25T10:51:35Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8392560) |
| Senior Payment Partnerships Manager | Welltech | Limassol, Cyprus | 2026-11-17T12:00:00Z | confirmed | [Apply](https://jobs.ashbyhq.com/welltech/80cb9359-c30b-4e65-81da-81bc4408f9e3) |
| Senior DevOps Engineer | Multiverse Computing | Barcelona, Spain | 2026-11-12T12:00:00Z | confirmed | [Apply](https://multiversecomputing.teamtailor.com/jobs/8705864-senior-devops-engineer?promotion=2292403-trackable-share-link-relocate) |
| Software Engineer (Java) - Warehouse Automation | Picnic | Amsterdam, Netherlands | 2026-11-09T12:00:00Z | confirmed | [Apply](https://grnh.se/cjadfxl61us) |
| Senior Data Science Engineer / Senior Machine Learning Engineer (Applied Insights) | PayPay | Tokyo, Japan | 2026-10-14T12:00:00Z | confirmed | [Apply](https://grnh.se/3apwasyz4us) |
| Safeguards Enforcement Analyst, Targeting, Tracking & Surveillance | Anthropic | San Francisco, CA, United States | 2026-11-25T01:42:41Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5494145008) |
| Associate Product Designer - Wealth building and Lending | N26 | Barcelona, Spain | 2026-11-25T09:09:11Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8355849?gh_jid=8355849) |
| Senior Backend Engineer | Monzo | London, United Kingdom | 2026-11-25T10:51:09Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8392368) |
| Senior LLM Engineer | Multiverse Computing | Barcelona, Spain | 2026-11-03T12:00:00Z | confirmed | [Apply](https://multiversecomputing.teamtailor.com/jobs/8657602-senior-llm-engineer?promotion=2277939-trackable-share-link-relocate-me) |
| Staff AI Engineer - Agentic Shopping | Picnic | Amsterdam, Netherlands | 2026-10-08T12:00:00Z | confirmed | [Apply](https://jobs.picnic.app/nl/vacancies?gh_jid=8179444) |
| Manager, Compliance & Regulatory Operations | Anthropic | New York, NY, United States | 2026-11-24T22:57:35Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5489900008) |
| Senior Product Manager - Investments | N26 | Barcelona, Spain | 2026-11-25T08:41:32Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8416464?gh_jid=8416464) |
| Data Director, Growth and Marketing | Monzo | Remote, Cardiff, United Kingdom | 2026-11-05T16:20:00Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8336726) |
| Engineering Manager, Cybersecurity Products | Anthropic | San Francisco, CA, United States | 2026-11-24T22:52:11Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5494120008) |
| Senior Product Marketing Manager | N26 | Berlin, Germany | 2026-11-11T16:59:24Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8364836?gh_jid=8364836) |
| Data Director, EU | Monzo | Remote, Barcelona, Spain | 2026-10-07T08:48:42Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8258208) |
| Applied AI Architect, Industries | Anthropic | Zurich, Switzerland | 2026-11-24T13:12:53Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5466640008) |
| Site Reliability Engineer - Data Platform | N26 | Berlin, Germany | 2026-11-11T12:33:58Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8378357?gh_jid=8378357) |
| Staff Data Scientist | Monzo | Remote, Barcelona, Spain | 2026-09-30T10:11:35Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8232732) |
| Life Sciences Operator, External Research | Anthropic | San Francisco, CA, United States | 2026-11-24T12:55:45Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490502008) |
| Senior Legal Counsel, Employment Law | N26 | Berlin, Germany | 2026-11-10T14:37:12Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8370910?gh_jid=8370910) |
| Staff Technical Program Manager, Operations | Monzo | London, United Kingdom | 2026-09-22T11:16:56Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8222576) |
| Head of Laboratory Facilities | Anthropic | San Francisco, CA, United States | 2026-11-24T12:51:05Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490494008) |
| Forecasting Expert | N26 | Madrid, Spain | 2026-11-09T08:58:30Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8358521?gh_jid=8358521) |
| Lead Product Designer, Growth | Monzo | Remote, Cardiff, United Kingdom | 2026-09-09T09:05:09Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8185694) |
| Applied AI Architect, Technology Partnerships | Anthropic | New York, NY, United States | 2026-11-23T20:50:45Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491480008) |
| Manager für Beschwerdeaudits | N26 | Berlin, Germany | 2026-11-09T07:45:54Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8364763?gh_jid=8364763) |
| Head of Compliance Advisory - Payments and Mobile, 12 month fixed term contract | Monzo | Remote, Cardiff, United Kingdom | 2026-11-26T14:26:59Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8419136) |
| Industry Principal, Insurance | Anthropic | New York, NY, United States | 2026-11-23T15:43:32Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5293104008) |
| Senior Manager Complaints Operations & Service Delivery | N26 | Madrid, Spain | 2026-11-04T08:47:44Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8352134?gh_jid=8352134) |
| Social Content Manager | Monzo | Remote, Cardiff, United Kingdom | 2026-11-26T13:52:52Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8414122) |
| Software Engineer, Model-to-Product Behavior Engineering | Anthropic | San Francisco, CA, United States | 2026-11-23T14:45:28Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5487188008) |
| Compliance and Prevention Associate (Complaints Management) (Fluent German) | N26 | Berlin, Germany | 2026-11-03T12:52:47Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8349423?gh_jid=8349423) |
| Creator Marketing Executive | Monzo | Remote, Cardiff, United Kingdom | 2026-11-26T13:50:40Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8414096) |
| Program Manager, Cloud Partners | Anthropic | San Francisco, CA, United States | 2026-11-22T19:46:05Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491573008) |
| Complaints Project Manager - Fluent German | N26 | Berlin, Germany | 2026-10-30T14:51:55Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8336867?gh_jid=8336867) |
| Senior Software Engineer | Monzo | Barcelona, Spain | 2026-11-25T12:05:03Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8392754) |
| Head of Campaign Operations | Anthropic | San Francisco, CA, United States | 2026-11-22T19:40:48Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491578008) |

_Showing 40 of 51. The full catalog is `data/latest-jobs.json`._
<!-- END OF JOB LISTINGS -->




















