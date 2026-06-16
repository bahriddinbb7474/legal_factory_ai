# UI Concept

Stage 3 v2 keeps the same practical workspace shape from Stage 1 v2 and adds document upload/preview behavior. The UI is still a skeleton for the first product version: it demonstrates the workflow and connects to backend document APIs, but final production editing/export logic is deferred.

## Layout

- Left sidebar: project workspace for `Kabel Tech Energy`, grouped by legal sections.
- Center: primary chat workspace with a wide reading area and a matching message composer.
- Right side: document preview/editor panel, closed by default and opened from a generated document card or uploaded document.
- Top bar: current section plus shortened chat title, and a compact `Расходы: $0.00` button.
- Bottom of sidebar: user profile block with avatar, name, and short role.

## Sidebar

The sidebar is section-based, not a global application menu. It contains:

- `Договоры`
- `Долги / претензии`
- `HR / кадры`
- `Судебные вопросы`
- `ГНИ`
- `Прочие Гос`
- `Прочие`

Each section has a small compose icon for creating a future new chat inside that section. By default each section shows one recent chat so the full workspace and user profile remain visible. Expanded sections can show more chats and a local search field when the list is longer.

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

The mock legal response card includes:

- short conclusion;
- risk badge, for example `Жёлтый риск`;
- source, revision date, and approval field;
- document card that opens the right panel;
- `Пометить как вердикт` placeholder action;
- Russian service actions such as `Копировать` and `Отправить Юристу 3`.

The response card does not include a document editing button. Editing belongs to the right document panel.

## Document Panel

The document panel behaves like a Claude-style artifact area:

- closed by default;
- opens from the document card, verdict placeholder, or uploaded document chip;
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

## Stage 5 v2 Verdict Document Workflow

The current UI adds a practical verdict-to-document flow:

- lawyer messages have `Пометить как вердикт`;
- only one lawyer message is visually active as the current verdict;
- the document card creates or opens a generated document from that active verdict;
- the right panel shows the generated document content, status, and editor controls;
- save/cancel applies to the generated document editor only;
- download opens Word/PDF actions backed by `/api/generated-documents/...`;
- reply/send-back has one action: `Отправить в общий чат`.

The right-panel reply action does not show Lawyer 1/2/3 options and does not invoke an LLM. After the document is returned to the chat, the user must select a lawyer in the bottom composer and send a normal follow-up message.

Uploaded document preview remains separate from generated document editing. Uploaded documents can be opened for metadata/extracted-text preview, while generated documents are the editable artifacts.
