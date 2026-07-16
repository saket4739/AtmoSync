# Custom Superset config for AtmoSync local dev.
#
# By default, Superset blocks connections to local file-based databases
# (like SQLite) as a security guard against SSRF/file-read attacks in
# production deployments. For local dev against our own atmosync.db file,
# we disable that check.

PREVENT_UNSAFE_DB_CONNECTIONS = False