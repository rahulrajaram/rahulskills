## Guest profile routing

This bundled variant runs inside a Chasm guest. The lifecycle and host-to-guest
transfer procedure below is host-side; do not try to satisfy its host identity
marker, invoke the host Chasm CLI, or access host paths from this guest.

- If the requested project is already under `/workspace/<project>`, treat it as
the persistent guest checkout and continue the requested development task
there. Do not migrate it into the same guest again.
- If the requested source is unavailable under `/workspace`, report the exact
missing source and that migration must be initiated from the Chasm host. Stop
only the dependent copy/migration action; continue any independent guest work.
- Never substitute a host home path, `/shared`, credentials, or an unreviewed
filesystem route for the missing source. Do not use this skill to authorize
host lifecycle operations from the guest.
