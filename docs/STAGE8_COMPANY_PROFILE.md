# Stage 8 CompanyProfile

## Scope

Stage 8-A adds the first `CompanyProfile` foundation for Legal Factory AI.

This stage is limited to:

- one editable company profile for the current MVP;
- backend model, migration, schemas, service, and API;
- frontend admin/settings form for company requisites;
- safe future placeholders for non-sensitive branding assets;
- a helper context path for future document template stages.

This stage does not implement Stage 8-B, Stage 9 templates, Telegram, VPS, pgvector, or roles/auth.

## CompanyProfile fields

Implemented fields:

- `id`
- `full_name`
- `short_name`
- `legal_address`
- `actual_address`
- `tax_id`
- `oked`
- `bank_name`
- `bank_mfo`
- `bank_account`
- `director_name`
- `chief_accountant_name`
- `legal_responsible_name`
- `phone`
- `email`
- `website`
- `logo_storage_key`
- `letterhead_storage_key`
- `is_active`
- `notes`
- `created_at`
- `updated_at`

Current MVP behavior:

- the application works with one effective company profile;
- `PUT /api/company-profile` creates the profile if missing and updates it afterwards;
- the service keeps only one active profile for normal use.

## API

Stage 8-A exposes:

```text
GET /api/company-profile
PUT /api/company-profile
```

If no profile exists yet, `GET` returns `404`.

## Validation

Current validation is intentionally basic:

- `full_name` is required;
- `short_name` is required;
- `tax_id` is optional;
- `email` is optional but must have a basic valid form if provided;
- `website` is optional;
- blank optional text is normalized to `null`.

No complex local validation for TIN/OKED formatting is added in Stage 8-A.

## Sensitive Assets Policy

Allowed in Stage 8-A:

- keep nullable future-safe fields for `logo` and `letterhead`;
- show disabled placeholder inputs in the UI;
- prepare future integration notes for document generation.

Forbidden in Stage 8-A:

- real stamp upload;
- real signature upload;
- showing real stamp/signature assets in the UI;
- using stamp/signature in generated documents.

Mandatory rule:

```text
Real stamp/signature assets must not be uploaded before access control/sensitive protection is implemented.
```

Stage 8-A therefore provides no stamp upload endpoint and no signature upload endpoint.

## Future document usage

Future template work may use the company profile through:

```text
app.services.company_profile.get_company_profile_context()
```

This helper is intended to provide stable company requisites for letters, claims, replies to state bodies, and later DOCX templates without rewriting the whole generated-document pipeline in Stage 8-A.

## Known limitations

- only one company profile is supported for the MVP;
- branding asset upload is deferred;
- stamp/signature handling is deferred until protected storage and access control exist;
- no Stage 9 template binding is implemented yet;
- no role-based access separation is implemented yet.
