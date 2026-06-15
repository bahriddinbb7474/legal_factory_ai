# UI Concept

Stage 1 v2 defines a practical web workspace for Legal Factory AI. The current UI is a clickable skeleton with mock data only; it does not call AI agents, OpenRouter, RAG, file upload, or backend chat logic yet.

## Layout

- Left sidebar: project workspace for `Kabel Tech Energy`, grouped by legal sections.
- Center: primary chat workspace with a wide reading area and a matching wide message composer.
- Right side: document preview/editor panel, closed by default and opened only from a generated document card or verdict action.
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

There is no separate large `Новый чат` button in Stage 1 v2.

## Chat Workspace

The central chat is the main working surface:

- When the right document panel is closed, the chat uses the available space after the sidebar.
- Chat content, answer cards, and the composer share the same visual width.
- The header format is `Раздел · начало названия чата…`.
- Messages use Russian interface labels.
- Lawyer messages show a compact marker such as `Ю1 · 14:32`, not the full model name.

## Lawyer Selection

The composer has one active lawyer at a time:

- `Юрист 1 · GPT-4o mini`
- `Юрист 2 · Claude Sonnet`
- `Юрист 3 · Арбитр · Gemini Pro`

The model is shown on the selection button. Future message submission should send the user's message only to the selected lawyer, while that lawyer can read the current chat history, other lawyers' messages, and the latest user message.

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
- opens from the document card or verdict placeholder;
- takes about half of the workspace when open;
- narrows the chat automatically;
- can be closed from the panel header;
- currently shows a mock DOCX-style document preview.

## Design Direction

The interface should remain calm, light, and business-focused: thin borders, compact controls, readable legal text, and a three-zone workspace when a document is open.
