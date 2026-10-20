# Security and deployment notes

## Required environment variables
- `DJANGO_SECRET_KEY`: unique, long random secret. Never commit it.
- `DJANGO_DEBUG`: use `False` in production.
- `DJANGO_ALLOWED_HOSTS`: comma-separated exact hostnames.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated HTTPS origins when needed.

Production startup intentionally fails when `DJANGO_SECRET_KEY` is missing. Local development may set `DJANGO_DEBUG=True` and use a local-only key.

## Database and personal information
The SQLite database is runtime data and must not be versioned. If a committed database contained real resident data, treat it as potentially exposed: assess the records, rotate any credentials/tokens, notify the appropriate privacy/security owner, and remove sensitive data from Git history with a coordinated history rewrite if appropriate. Removing the latest copy alone does not erase prior commits.

## Uploaded documents
Files containing government IDs, certificates, or complaint evidence should be stored in private storage and served only through authorized views. Do not expose the media directory as a public static directory in production. Validate uploads server-side and scan them where feasible.

## Deployment
Run the automated checks in GitHub Actions and review their results before merging or deploying.
Set HTTPS at the hosting platform, configure the exact allowed hostnames and CSRF origins, run `python manage.py check --deploy`, apply migrations, and run the automated test suite before release.
