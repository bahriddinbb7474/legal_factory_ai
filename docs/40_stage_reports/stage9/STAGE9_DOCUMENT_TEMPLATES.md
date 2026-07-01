# Stage 9 Document Templates

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

## Stage 9-B Debt Template Practical Inputs

### Implemented Input Fields
The following fields are now structured and processed during template application for `client_debt_reminder` and `client_debt_claim`:

**Required Fields:**
- `counterparty_name`: mapped to `{{ counterparty.name }}`
- `debt_amount`: mapped to `{{ debt.amount }}`
- `currency`: mapped to `{{ debt.currency }}`
- `payment_basis`: mapped to `{{ payment_basis }}`

**Optional Fields:**
- `counterparty_address`: mapped to `{{ counterparty.address }}`
- `counterparty_tax_id`: mapped to `{{ counterparty.tax_id }}`
- `contract_number`: mapped to `{{ contract.number }}`
- `contract_date`: mapped to `{{ contract.date }}`
- `invoice_or_spec_number`: mapped to `{{ invoice_or_spec_number }}`
- `due_date`: mapped to `{{ due_date }}`
- `overdue_days`: mapped to `{{ overdue_days }}`
- `requested_payment_deadline`: mapped to `{{ requested_payment_deadline }}`
- `responsible_person`: mapped to `{{ responsible_person }}`
- `additional_note`: mapped to `{{ additional_note }}`
- `bank_details_note`: mapped to `{{ bank_details_note }}`
- `attached_documents_note`: mapped to `{{ attached_documents_note }}`

### Placeholder Policy
- Templates have been updated to utilize these exact placeholders.
- Safe substitution is strictly enforced via `DocumentTemplateService.render()`.
- Unrecognized or empty placeholders are rendered as blank and are listed in `missing_placeholders` array in API response.
- `CompanyProfile` context (`{{ company.* }}`) continues working seamlessly.

### Manual Editing and Security
- Manual editing is preserved after rendering text in the UI.
- Stamp/signature variables (`{{ company.stamp }}`, `{{ company.signature }}`) remain blocked by design.
- Logo and Letterhead placeholders are not directly inserted into the raw text body but are available as storage key metadata (`{{ company.logo_storage_key }}`, etc.) if needed downstream.

### Known Limitations
- Advanced DOCX base-letterhead merge deferred unless implemented safely.
- Full template catalog deferred.
- Roles/auth deferred.
- Approval workflow separate.
- No stamp/signature insertion.
