"use client";

import { FormEvent, useEffect, useState } from "react";

import Sidebar from "./components/Sidebar";

const lawyers = [
  { id: "lawyer-1", short: "Ю1", label: "Юрист 1 · GPT-4o mini" },
  { id: "lawyer-2", short: "Ю2", label: "Юрист 2 · Claude Sonnet" },
  { id: "lawyer-3", short: "Ю3", label: "Юрист 3 · Арбитр · Gemini Pro" },
];

export default function HomePage() {
  const [selectedLawyer, setSelectedLawyer] = useState(lawyers[0].id);
  const [isDocumentOpen, setIsDocumentOpen] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const lawyerNumber = params.get("lawyer");
    const nextLawyer = lawyers.find((lawyer) => lawyer.id === `lawyer-${lawyerNumber}`);
    if (nextLawyer) {
      setSelectedLawyer(nextLawyer.id);
    }
    setIsDocumentOpen(params.get("document") === "open");
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
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
              <button className="icon-button" aria-label="Скачать">
                v
              </button>
              <button className="icon-button" onClick={() => setIsDocumentOpen(false)} aria-label="Закрыть документ">
                x
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
                <p>
                  Уважаемые партнеры, просим провести сверку взаиморасчетов и подтвердить срок оплаты
                  задолженности по договору поставки.
                </p>
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
