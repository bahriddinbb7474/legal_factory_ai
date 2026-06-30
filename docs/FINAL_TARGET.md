# Final Target

The final product is a secure internal legal workspace for the factory.

Expected result:

- Web UI similar to ChatGPT, with chat history, central chat, and bottom input field.
- Three AI legal agents: fast lawyer, strong analyst, and reviewer/critic.
- Upload and analysis of PDF, DOCX, XLSX, TXT, and letter images.
- Right-side document editor similar to Claude artifacts.
- Telegram bot for quick questions, uploads, risk notifications, and approval actions.
- RAG over factory documents and official Uzbekistan legal sources.
- Approval workflow for red-risk questions and final documents.
- Token and dollar cost tracking by chat and agent.

The final workflow must provide human-readable lawyer answers before verdict and use structured
payload only for a verified verdict from Lawyer 2 or Lawyer 3. Lawyer 1 cannot issue a verdict.
The final workspace separates `Шаблонные документы` (approved-template AI-Секретарь flow without
RAG or verdict by default) from `Юридические вопросы и заключения` (AI-Юрист analysis, targeted
RAG, review, and eligible verdict flow). Stable internal codes control routing; visible labels do
not. A verdict is bound to
its concrete source package and context snapshot, and the model cannot control citation,
approval, or document-generation gate fields.

The final version must always prefer active official Uzbekistan sources for current-law answers.
If a reliable source is missing, the system must block final legal conclusions and direct the user
to a lawyer or responsible specialist. Red topics require approval in every section, and uploaded
untrusted documents must never override instructions or become official law.
