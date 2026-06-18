# Stage 9 Document Templates

## Stage 9-A scope

Stage 9-A adds the first safe `DocumentTemplate` foundation for Legal Factory AI.

Implemented in this stage:

- `DocumentTemplate` backend model and migration;
- default template registry/seed for two debt-related templates;
- safe placeholder rendering without `eval` or arbitrary template code execution;
- `CompanyProfile` binding for template context;
- minimal integration with `GeneratedDocument`;
- backend API to list/get templates and apply a template to a generated document;
- minimal frontend template selector in the document pane.

Not implemented in Stage 9-A:

- the full template library;
- advanced DOCX base-letterhead merging;
- approval roles/auth changes;
- stamp/signature insertion.

## Implemented templates

Stage 9-A includes only:

- `client_debt_reminder` — `Письмо клиенту о задолженности`
- `client_debt_claim` — `Претензия клиенту о задолженности`

Deferred to later Stage 9 work:

- supplier letters;
- government replies;
- tax/customs letters;
- HR notices;
- orders;
- internal memos;
- certification and technical-regulation templates.

## Placeholder policy

Stage 9-A uses an allowlisted placeholder set only.

Examples:

- `{{ company.full_name }}`
- `{{ company.bank_account }}`
- `{{ document.body }}`
- `{{ verdict.summary }}`
- `{{ counterparty.name }}`
- `{{ amount }}`
- `{{ due_date }}`
- `{{ today }}`

Rules:

- unknown placeholders do not crash rendering;
- unknown placeholders are rendered as blank;
- no arbitrary code execution is allowed;
- stamp/signature placeholders are not supported.

## CompanyProfile binding

Template rendering can use safe CompanyProfile context from:

```text
app.services.company_profile.get_company_profile_context()
```

The safe context includes company text requisites and asset keys such as:

- `logo_storage_key`
- `letterhead_storage_key`

It does not include:

- stamp
- signature

## Letterhead and logo behavior

Stage 9-A behavior:

- `logo_storage_key` and `letterhead_storage_key` are available in render context;
- rendered document text can use CompanyProfile data immediately;
- DOCX export remains functional after template rendering;
- real uploaded assets remain local runtime assets only.

Stage 9-A limitation:

- advanced merging with a real uploaded letterhead DOCX base is not required and may be deferred to Stage 9-B.

## Security

- real company assets must not be committed to Git;
- real logo and letterhead files must stay in storage only;
- stamp/signature remain blocked;
- no upload or rendering flow for stamp/signature is enabled.

## Known limitations

- full template library is deferred;
- advanced DOCX base-letterhead merging may be deferred;
- approval roles are still deferred to Stage 11;
- stamp/signature remain blocked;
- template input UI for counterparty/amount/due date is still minimal in Stage 9-A.

## Next Stage 9-B plan

Natural next work after Stage 9-A:

- richer template metadata and categories;
- better per-template input forms for counterparty, amount, and deadlines;
- stronger DOCX layout control;
- optional safe base-letterhead DOCX merge;
- expansion to additional legal/business templates.
