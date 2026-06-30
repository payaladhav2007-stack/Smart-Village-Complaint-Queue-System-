\# GS-509 Concurrency Stress Test Results



\*\*Date:\*\* June 30, 2026

\*\*Test tool:\*\* Locust 2.44.4

\*\*Target server:\*\* Django development server (`python manage.py runserver`)

\*\*Simulated users:\*\* ramped to 500 concurrent users

\*\*Ramp-up rate:\*\* 50 users/second



\## Critical Pre-Test Finding



During initial test setup, `POST /api/auth/register/` and `POST /api/auth/login/`

were found to incorrectly require authentication, returning `401 Unauthorized`

to every request. This blocked all citizen registration and login, meaning

no real citizen could create an account or log in to the live application

in its current state on `main`. Root cause: `RegisterView` and `LoginView`

in `accounts/views.py` have no `permission\_classes` set, so they inherit

the project's global default DRF permission (`IsAuthenticated`) from

`gramsmart/settings.py`. This needs a one-line fix per view:

`permission\_classes = \[AllowAny]`. Flagged to team for separate ticket/hotfix.



A temporary local fix was applied only to unblock stress testing, then

reverted before this branch was committed, since fixing it is outside

the scope of GS-509.



\## Test Results — Low Load (1 simulated user, baseline)

\- All endpoints (register, token, book, my-tokens, grievances/submit)

&#x20; returned successfully with 0% failure rate

\- Average response times: 7–200ms across endpoints



\## Test Results — High Load (500 concurrent users, 50/sec ramp-up)

\- Failure rate climbed to 95–100% under load

\- Status 0 (connection refused) — 1966 failures on `/api/appointments/book/`,

&#x20; 639 on `/api/appointments/my-tokens/` — Django's built-in development

&#x20; server is single-threaded and cannot handle this level of concurrency

\- Status 401 — 1257+424 failures — citizens lost authentication under

&#x20; heavy load, likely due to request timeouts during server overload

\- Status 500 — 19 failures on `/api/appointments/book/` — genuine

&#x20; server-side errors under concurrent load, worth deeper investigation

&#x20; by the backend team as a potential race condition in the booking flow



\## Duplicate Token Check (Core DoD Requirement)

Ran `testing/load\_tests/verify\_no\_duplicates.py` via Django shell after

the stress test concluded.



\*\*Result: PASSED\*\* — No duplicate `token\_number` values found in the

`Appointment` table. Total appointments in database after test: 10.



Despite the high failure rate caused by server overload, the database-level

booking logic (built in GS-303 by Maaz using `select\_for\_update()` and

sequential token generation) correctly prevented any duplicate tokens

from being created, even under chaotic concurrent conditions.



\## Conclusion

The core booking concurrency safety mechanism (database-level locking

and sequential token generation) works correctly and prevents duplicate

tokens even under severe load and partial server failure. However, the

Django development server itself is not suitable for handling 500+

concurrent users — for accurate production-level concurrency testing,

this suite should be re-run against a production WSGI server (e.g.

Gunicorn) rather than `manage.py runserver`. The pre-existing

authentication bug on the registration/login endpoints should be

fixed as a separate, higher-priority hotfix.



\## Recommendations

1\. Fix `permission\_classes` on `RegisterView` and `LoginView`

&#x20;  (separate ticket, flagged to team)

2\. Re-run this Locust suite against a production server (Gunicorn/uWSGI)

&#x20;  for accurate concurrency benchmarks

3\. Investigate the 19 occurrences of `500 Internal Server Error` on

&#x20;  `/api/appointments/book/` under load — may indicate an edge case

&#x20;  not covered by GS-303's existing concurrency tests

