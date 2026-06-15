"use client";

import { FormEvent, useEffect, useState } from "react";

import Sidebar from "./components/Sidebar";

const lawyers = [
  { id: "lawyer-1", short: "Ю1", label: "Юрист 1 · GPT-4o mini" },
  { id: "lawyer-2", short: "Ю2", label: "Юрист 2 · Claude Sonnet" },
  { id: "lawyer-3", short: "Ю3", label: "Юрист 3 · Арбитр · Gemini Pro" },
];

const initialDocumentBody =
  "Уважаемые партнеры, просим провести сверку взаиморасчетов и подтвердить срок оплаты задолженности по договору поставки.";

export default function HomePage() {
  const [selectedLawyer, setSelectedLawyer] = useState(lawyers[0].id);
  const [isDocumentOpen, setIsDocumentOpen] = useState(false);
  const [isDocumentEditing, setIsDocumentEditing] = useState(false);
  const [documentBody, setDocumentBody] = useState(initialDocumentBody);
  const [openDocumentMenu, setOpenDocumentMenu] = useState<"download" | "reply" | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const lawyerNumber = params.get("lawyer");
    const nextLawyer = lawyers.find((lawyer) => lawyer.id === `lawyer-${lawyerNumber}`);
    if (nextLawyer) {
      setSelectedLawyer(nextLawyer.id);
    }
    setIsDocumentOpen(params.get("document") === "open");
    setIsDocumentEditing(params.get("mode") === "edit");
    const menu = params.get("menu");
    if (menu === "download" || menu === "reply") {
      setOpenDocumentMenu(menu);
    }
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
  }

  function closeDocumentPanel() {
    setIsDocumentOpen(false);
    setIsDocumentEditing(false);
    setOpenDocumentMenu(null);
  }

  function startDocumentEditing() {
    setIsDocumentEditing(true);
    setOpenDocumentMenu(null);
  }

  function saveDocumentChanges() {
    setIsDocumentEditing(false);
    setOpenDocumentMenu(null);
  }

  function cancelDocumentChanges() {
    setDocumentBody(initialDocumentBody);
    setIsDocumentEditing(false);
    setOpenDocumentMenu(null);
  }

  function toggleDocumentMenu(menu: "download" | "reply") {
    setOpenDocumentMenu((currentMenu) => (currentMenu === menu ? null : menu));
  }

  return (
    <main className={isDocumentOpen ? "workspace-shell document-open" : "workspace-shell"}>
      <Sidebar />

      <section className="chat-area">
        <header className="topbar">
          <h1 className="chat-title">Долги / претензии · Письмо клиенту о задолженности…</h1>
          <div className="topbar-actions">
            <button className="compact-button">Расходы: $0.00</button>
            <button className="icon-button" aria-label="Свернуть">
              ^
            </button>
            <button className="icon-button" aria-label="Еще">
              ...
            </button>
          </div>
        </header>

        <div className="conversation">
          <article className="message user-message">
            <p>
              Подготовь черновик ответа клиенту по задолженности и укажи, нужно ли согласование директора.
            </p>
          </article>

          <article className="message assistant-message">
            <div className="message-toolbar">
              <span className="assistant-meta">Ю1 · 14:32</span>
              <span className="risk-badge yellow">Жёлтый риск</span>
              <button className="pill-button verdict-button" onClick={() => setIsDocumentOpen(true)} type="button">
                Пометить как вердикт
              </button>
            </div>

            <h1>Краткий вывод</h1>
            <p>
              Можно направить клиенту мягкое письмо с требованием сверки и оплаты. Финальное признание
              долга или уступки по срокам оплаты давать нельзя без проверки договора и бухгалтерии.
            </p>

            <div className="legal-grid">
              <div>
                <span>Источник</span>
                <strong>Договор поставки N 14/25</strong>
              </div>
              <div>
                <span>Редакция</span>
                <strong>10.06.2026</strong>
              </div>
              <div>
                <span>Согласование</span>
                <strong>Главбух</strong>
              </div>
            </div>

            <button className="document-card document-card-button" onClick={() => setIsDocumentOpen(true)} type="button">
              <div className="doc-icon">DOCX</div>
              <div>
                <strong>Письмо клиенту о задолженности</strong>
                <span>Черновик документа</span>
              </div>
              <span className="compact-button">Открыть справа</span>
            </button>

            <div className="message-actions">
              <button>Копировать</button>
              <button>Нравится</button>
              <button>Отправить Юристу 3</button>
            </div>
          </article>
        </div>

        <div className="composer-wrap">
          <form className="composer" onSubmit={handleSubmit}>
            <button type="button" className="icon-button" aria-label="Добавить файл">
              +
            </button>
            <input aria-label="Сообщение" placeholder="Спросите Legal Factory AI" />
            <button type="submit" className="voice-button" aria-label="Отправить выбранному юристу">
              <span className="send-arrow" aria-hidden="true" />
            </button>
          </form>
          <div className="agent-row" aria-label="Выбор юриста">
            {lawyers.map((lawyer) => (
              <button
                className={lawyer.id === selectedLawyer ? "agent-chip active" : "agent-chip"}
                key={lawyer.id}
                onClick={() => setSelectedLawyer(lawyer.id)}
                type="button"
              >
                {lawyer.label}
              </button>
            ))}
          </div>
          <p className="disclaimer">Legal Factory AI может ошибаться. Важные выводы проверяются ответственным специалистом.</p>
        </div>
      </section>

      {isDocumentOpen ? (
        <aside className="document-pane">
          <header className="document-header">
            <div>
              <strong>Письмо клиенту о задолженности</strong>
              <span>Документ · DOCX</span>
            </div>
            <div className="document-actions">
              <div className="document-action-group">
                {isDocumentEditing ? (
                  <>
                    <button
                      className="document-icon-button"
                      onClick={saveDocumentChanges}
                      title="Сохранить изменения"
                      type="button"
                      aria-label="Сохранить изменения"
                    >
                      ✓
                    </button>
                    <button
                      className="document-icon-button cancel-edit-button"
                      onClick={cancelDocumentChanges}
                      title="Отменить изменения"
                      type="button"
                      aria-label="Отменить изменения"
                    >
                      ×
                    </button>
                  </>
                ) : (
                  <button
                    className="document-icon-button"
                    onClick={startDocumentEditing}
                    title="Редактировать документ"
                    type="button"
                    aria-label="Редактировать документ"
                  >
                    ✎
                  </button>
                )}

                <div className="document-menu-wrap">
                  <button
                    className="document-icon-button"
                    onClick={() => toggleDocumentMenu("download")}
                    title="Скачать документ"
                    type="button"
                    aria-label="Скачать документ"
                    aria-expanded={openDocumentMenu === "download"}
                  >
                    ⇩
                  </button>
                  {openDocumentMenu === "download" ? (
                    <div className="document-dropdown">
                      <button type="button">Скачать Word (.docx)</button>
                      <button type="button">Скачать PDF (.pdf)</button>
                    </div>
                  ) : null}
                </div>

                <div className="document-menu-wrap">
                  <button
                    className="document-icon-button"
                    onClick={() => toggleDocumentMenu("reply")}
                    title="Отправить документ в чат"
                    type="button"
                    aria-label="Отправить документ в чат"
                    aria-expanded={openDocumentMenu === "reply"}
                  >
                    ↩
                  </button>
                  {openDocumentMenu === "reply" ? (
                    <div className="document-dropdown">
                      <button type="button">Отправить Юристу 1</button>
                      <button type="button">Отправить Юристу 2</button>
                      <button type="button">Отправить Юристу 3</button>
                    </div>
                  ) : null}
                </div>
              </div>
              <span className="document-action-separator" aria-hidden="true" />
              <button
                className="document-icon-button document-close-button"
                onClick={closeDocumentPanel}
                title="Закрыть документ"
                type="button"
                aria-label="Закрыть документ"
              >
                ×
              </button>
            </div>
          </header>

          <div className="document-stage">
            <article className="document-page">
              <div className="document-band">ЧЕРНОВИК</div>
              <h2>ООО “KABEL TECH ENERGY”</h2>
              <p className="doc-center">111116, Республика Узбекистан, Ташкентская область</p>

              <section>
                <h3>Письмо о задолженности</h3>
                {isDocumentEditing ? (
                  <textarea
                    className="document-editor"
                    aria-label="Текст документа"
                    value={documentBody}
                    onChange={(event) => setDocumentBody(event.target.value)}
                  />
                ) : (
                  <p>{documentBody}</p>
                )}
              </section>

              <table>
                <tbody>
                  <tr>
                    <th>Клиент</th>
                    <td>ООО “Example Cable Trade”</td>
                  </tr>
                  <tr>
                    <th>Договор</th>
                    <td>N 14/25 от 10.06.2026</td>
                  </tr>
                  <tr>
                    <th>Риск</th>
                    <td>Жёлтый: требуется проверка бухгалтерии</td>
                  </tr>
                </tbody>
              </table>

              <section>
                <h3>Практический вывод для завода</h3>
                <p>
                  Письмо можно использовать как черновик. Перед отправкой нужно сверить сумму, срок
                  оплаты и полномочия подписанта.
                </p>
              </section>
            </article>
          </div>
        </aside>
      ) : null}
    </main>
  );
}
