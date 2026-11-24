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

Updated on 2026-11-24 16:41:13 UTC

- Listings: **51**
- Sponsorship evidence confirmed: **41**
- Sponsorship evidence likely (known sponsor list): **10**
- With a salary range: **17**
- With relocation assistance in the posting: **25**

Only jobs with `sponsorship_evidence` of `confirmed` or `likely` are included.
Apply links are employer or ATS URLs. Competitor boards are not used.

| Title | Company | Location | Posted | Evidence | Apply |
|-------|---------|----------|--------|----------|-------|
| Applied AI Architect, Industries | Anthropic | Zurich, Switzerland | 2026-11-24T13:12:53Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5466640008) |
| Senior Payment Partnerships Manager | Welltech | Limassol, Cyprus | 2026-11-17T12:00:00Z | confirmed | [Apply](https://jobs.ashbyhq.com/welltech/80cb9359-c30b-4e65-81da-81bc4408f9e3) |
| Senior DevOps Engineer | Multiverse Computing | Barcelona, Spain | 2026-11-12T12:00:00Z | confirmed | [Apply](https://multiversecomputing.teamtailor.com/jobs/8705864-senior-devops-engineer?promotion=2292403-trackable-share-link-relocate) |
| Senior Product Marketing Manager | N26 | Berlin, Germany | 2026-11-11T16:59:24Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8364836?gh_jid=8364836) |
| Software Engineer (Java) - Warehouse Automation | Picnic | Amsterdam, Netherlands | 2026-11-09T12:00:00Z | confirmed | [Apply](https://grnh.se/cjadfxl61us) |
| Data Director, Growth and Marketing | Monzo | Remote, Cardiff, United Kingdom | 2026-11-05T16:20:00Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8336726) |
| Senior Data Science Engineer / Senior Machine Learning Engineer (Applied Insights) | PayPay | Tokyo, Japan | 2026-10-14T12:00:00Z | confirmed | [Apply](https://grnh.se/3apwasyz4us) |
| Life Sciences Operator, External Research | Anthropic | San Francisco, CA, United States | 2026-11-24T12:55:45Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490502008) |
| Senior LLM Engineer | Multiverse Computing | Barcelona, Spain | 2026-11-03T12:00:00Z | confirmed | [Apply](https://multiversecomputing.teamtailor.com/jobs/8657602-senior-llm-engineer?promotion=2277939-trackable-share-link-relocate-me) |
| Senior Legal Counsel, Employment Law | N26 | Berlin, Germany | 2026-11-10T14:37:12Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8370910?gh_jid=8370910) |
| Staff AI Engineer - Agentic Shopping | Picnic | Amsterdam, Netherlands | 2026-10-08T12:00:00Z | confirmed | [Apply](https://jobs.picnic.app/nl/vacancies?gh_jid=8179444) |
| Data Director, EU | Monzo | Remote, Barcelona, Spain | 2026-10-07T08:48:42Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8258208) |
| Head of Laboratory Facilities | Anthropic | San Francisco, CA, United States | 2026-11-24T12:51:05Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490494008) |
| Forecasting Expert | N26 | Madrid, Spain | 2026-11-09T08:58:30Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8358521?gh_jid=8358521) |
| Staff Data Scientist | Monzo | Remote, Barcelona, Spain | 2026-09-30T10:11:35Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8232732) |
| Applied AI Architect, Technology Partnerships | Anthropic | New York, NY, United States | 2026-11-23T20:50:45Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491480008) |
| Manager für Beschwerdeaudits | N26 | Berlin, Germany | 2026-11-09T07:45:54Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8364763?gh_jid=8364763) |
| Staff Technical Program Manager, Operations | Monzo | London, United Kingdom | 2026-09-22T11:16:56Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8222576) |
| Industry Principal, Insurance | Anthropic | New York, NY, United States | 2026-11-23T15:43:32Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5293104008) |
| Senior Manager Complaints Operations & Service Delivery | N26 | Madrid, Spain | 2026-11-04T08:47:44Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8352134?gh_jid=8352134) |
| Lead Product Designer, Growth | Monzo | Remote, Cardiff, United Kingdom | 2026-09-09T09:05:09Z | confirmed | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8185694) |
| Software Engineer, Model-to-Product Behavior Engineering | Anthropic | San Francisco, CA, United States | 2026-11-23T14:45:28Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5487188008) |
| Compliance and Prevention Associate (Complaints Management) (Fluent German) | N26 | Berlin, Germany | 2026-11-03T12:52:47Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8349423?gh_jid=8349423) |
| Strategy & Operations Manager | Monzo | Dublin, Ireland | 2026-11-23T15:46:51Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8411444) |
| Program Manager, Cloud Partners | Anthropic | San Francisco, CA, United States | 2026-11-22T19:46:05Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491573008) |
| Complaints Project Manager - Fluent German | N26 | Berlin, Germany | 2026-10-30T14:51:55Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8336867?gh_jid=8336867) |
| Senior Third Party Risk Manager | Monzo | Remote, London, United Kingdom | 2026-11-20T18:01:26Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8195253) |
| Head of Campaign Operations | Anthropic | San Francisco, CA, United States | 2026-11-22T19:40:48Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491578008) |
| Senior Manager Business Audit / French Market | N26 | Paris, France | 2026-10-12T13:03:07Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8266560?gh_jid=8266560) |
| Senior Treasury Product Control Analyst | Monzo | Remote, Cardiff, United Kingdom | 2026-11-19T10:00:42Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8398665) |
| Campaign Manager | Anthropic | San Francisco, CA, United States | 2026-11-22T19:37:34Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5491575008) |
| Data Analyst - Investments | N26 | Barcelona, Spain | 2026-10-07T15:27:00Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8203962?gh_jid=8203962) |
| Staff Brand Designer | Monzo | London, United Kingdom | 2026-11-18T13:08:57Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8396136) |
| Research Engineer, Finetuning | Anthropic | San Francisco, CA, United States | 2026-11-21T12:52:27Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5489567008) |
| Manager Business Audit / Spanish Market | N26 | Madrid, Spain | 2026-10-01T11:49:54Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8239606?gh_jid=8239606) |
| Senior Regulatory Reporting Analyst | Monzo | London, United Kingdom | 2026-11-18T09:25:34Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385865) |
| Manager, Applied AI Architect | Anthropic | Seoul, South Korea | 2026-11-21T12:24:21Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5480986008) |
| Business Audit Manager | N26 | Berlin, Germany | 2026-10-01T11:42:40Z | confirmed | [Apply](https://n26.com/en-eu/careers/positions/8242571?gh_jid=8242571) |
| Sales Manager | Monzo | London, United Kingdom | 2026-11-16T11:12:33Z | likely | [Apply](https://job-boards.greenhouse.io/monzo/jobs/8385191) |
| Research Operations, External Artifacts | Anthropic | Remote, United States | 2026-11-21T00:47:30Z | confirmed | [Apply](https://job-boards.greenhouse.io/anthropic/jobs/5490492008) |

_Showing 40 of 51. The full catalog is `data/latest-jobs.json`._
<!-- END OF JOB LISTINGS -->


















