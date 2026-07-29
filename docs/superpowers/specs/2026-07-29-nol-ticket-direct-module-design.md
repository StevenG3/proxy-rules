# NOL Ticket Direct Module Design

## Goal

Provide a Shadowrocket module that can be imported from the Modules screen and
routes the two confirmed NOL ticketing and payment domains directly.

## Module

Add `shadowrocket/nol-ticket-direct.sgmodule` with Shadowrocket module metadata
and a `[Rule]` section containing:

```ini
DOMAIN,secureapi.ext.eximbay.com,DIRECT
DOMAIN,gpoticket.globalinterpark.com,DIRECT
```

Use exact `DOMAIN` matches. Do not broaden either entry to `DOMAIN-SUFFIX`,
because unrelated services under the parent domains should keep their existing
routing behavior.

## Documentation

Add the module's raw GitHub URL and brief import instructions to `README.md`.
The URL must be suitable for Shadowrocket's remote module import flow.

## Verification

- Confirm the module contains valid metadata, one `[Rule]` section, and exactly
  the two expected `DOMAIN` rules using the `DIRECT` policy.
- Confirm the raw GitHub URL returns the committed module content after push.
- Confirm the repository is clean and local `main` matches `origin/main`.

## Scope

This change does not modify the existing Claude rule set, add wildcard domain
matching, or introduce rewrite, MITM, script, or certificate settings.
