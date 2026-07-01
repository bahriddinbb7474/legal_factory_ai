# UI Concept

Stage 3 v2 keeps the same practical workspace shape from Stage 1 v2 and adds document upload/preview behavior. The UI is still a skeleton for the first product version: it demonstrates the workflow and connects to backend document APIs, but final production editing/export logic is deferred.

## Layout

- Left sidebar: project workspace for `Kabel Tech Energy`, grouped by the two approved functional groups and their sections.
- Center: primary chat workspace with a wide reading area and a matching message composer.
- Right side: document preview/editor panel, closed by default and opened from a generated document card or uploaded document.
- Top bar: current section plus shortened chat title, and a compact `Расходы: $0.00` button.
- Bottom of sidebar: user profile block with avatar, name, and short role.

## Sidebar

The sidebar is section-based, not a global application menu. It contains the approved groups:

- `Шаблонные документы`: `Письма`, `Договоры`, `Справки`, `Доверенности`, `Приказы`, `Прочие документы`;
- `Юридические вопросы и заключения`: `Экспертиза контрактов`, `Долги (дебиторы / кредиторы)`, `Валютное регулирование`, `Налоговые вопросы`, `Государственные органы`, `Контрагенты и переписка`, `Бухгалтерия`, `HR / Трудовое право`, `Прочие внут.подразделения`, `Судебные и досудебные дела`, `Прочие юридические вопросы`.

The frontend displays these names but sends stable internal codes. Labels may change without changing routing. The canonical mapping is in `../10_policies/SECTION_GROUPS_AND_RAG_POLICY.md`.

Each section has a small compose icon for creating a new chat inside that section. Section rows are collapsed by default, and chat titles remain hidden until the user expands a section. Expanded sections show their chats and may show a local search field when the list is longer.

There is no separate large `Новый чат` button.

## Chat Workspace

The central chat is the main working surface:

- When the right document panel is closed, the chat uses the available space after the sidebar.
- Chat content, answer cards, document chips, and the composer share the same visual width.
- The header format is `Раздел · начало названия чата…`.
- Messages use Russian interface labels.
- Lawyer messages show a compact marker such as `Ю1 · 14:32`, not the full model name.

## Lawyer Selection

The composer has one active lawyer at a time:

- `Юрист 1 · GPT-4o mini`
- `Юрист 2 · Claude Sonnet`
- `Юрист 3 · Арбитр · Gemini Pro`

The model is shown on the selection button. Future message submission sends the user's message only to the selected lawyer, while that lawyer can read the current chat history, other lawyers' messages, and the latest user message.

## Document Upload

The `+` button in the composer opens local file selection for:

- PDF;
- DOCX;
- XLSX;
- TXT;
- JPG/PNG/WebP images.

After selecting a file, the user confirms metadata in a compact modal:

- category;
- sensitivity;
- counterparty;
- document number;
- document date.

Uploaded documents appear as chips above the composer. A chip opens the right document panel with metadata and extracted text. The remove action unlinks the document from the current chat.

## Response Card

The legal response card includes:

- short conclusion;
- risk badge, for example `Жёлтый риск`;
- source, revision date, and approval field;
- document card that opens the right panel;
- Russian service actions such as `Копировать` and `Отправить Юристу 3`.

Normal lawyer replies are labeled `Мнение юриста` and have no manual mark-as-verdict action. A real explicit Lawyer 2/3 verdict is labeled `Юридический вердикт`; an unconfirmed verdict shows no document-generation action.

The response card does not include a document editing button. Editing belongs to the right document panel.

## Document Panel

The document panel behaves like a Claude-style artifact area:

- closed by default;
- opens from a permitted document card or uploaded document chip;
- takes about half of the workspace when open;
- narrows the chat automatically;
- can be closed from the panel header;
- shows either the mock DOCX-style preview or uploaded document metadata/extracted text.

For uploaded documents, the panel shows:

- filename;
- category;
- sensitivity;
- extraction/OCR status;
- original file download link;
- extracted text preview.

Toolbar actions are currently UI-stage controls: edit mode, download menu, send-back-to-chat menu, and close.

## Design Direction

The interface should remain calm, light, and business-focused: thin borders, compact controls, readable legal text, and a three-zone workspace when a document is open.

## Planned Settings Sections After Stage 6

The next roadmap adds operational settings, but the core workspace remains chat + right document panel.

Planned settings sections:

- `Настройки -> Юридическая база`
- `Настройки -> Данные компании`
- `Настройки -> Шаблоны документов`

`Настройки -> Юридическая база` should support the existing curated legal-source workflow and Stage 7 completion needs:

- list legal sources;
- upload or paste source text;
- show document type, number, revision date, source URL, status, language, last check date, and next check date;
- show active/outdated/archived state;
- show freshness warnings;
- reindex chunks.

`Настройки -> Данные компании` is planned for Stage 8:

- edit official company profile fields;
- upload logo;
- upload letterhead;
- upload stamp/signature with sensitive access controls;
- preview the company block;
- show change history from audit logs.

`Настройки -> Шаблоны документов` is planned for Stage 9:

- list templates;
- create and edit templates;
- preview;
- activate a version;
- archive an old version;
- run test generation.

Telegram is not part of the current UI path. It is postponed until the Web UI, legal base, templates, local launch, and real users are stable.

## P2-B3 Verdict UI Boundary

The current UI follows the policy boundary:

- normal Lawyer 1/2/3 messages have no manual mark-as-verdict action;
- explicit verdict phrases select verdict mode only for Lawyer 2 or Lawyer 3;
- ambiguous consent stays in normal or clarification flow;
- a new verdict skeleton remains unconfirmed and cannot expose document generation;
- the right panel shows the generated document content, status, and editor controls;
- save/cancel applies to the generated document editor only;
- download opens Word/PDF actions backed by `/api/generated-documents/...`;
- reply/send-back has one action: `Отправить в общий чат`.

The existing generated-document editor describes the legacy baseline. P5 must connect it only to a source-verified, backend-approved verdict gate.

The right-panel reply action does not show Lawyer 1/2/3 options and does not invoke an LLM. After the document is returned to the chat, the user must select a lawyer in the bottom composer and send a normal follow-up message.

Uploaded document preview remains separate from generated document editing. Uploaded documents can be opened for metadata/extracted-text preview, while generated documents are the editable artifacts.
