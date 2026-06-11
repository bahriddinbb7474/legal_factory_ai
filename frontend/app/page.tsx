import Sidebar from "./components/Sidebar";

export default function HomePage() {
  return (
    <main className="workspace-shell">
      <Sidebar />

      <section className="chat-area">
        <header className="topbar">
          <button className="compact-button">Legal Factory AI</button>
          <div className="topbar-actions">
            <button className="compact-button">Cost: $0.00</button>
            <button className="icon-button" aria-label="Поделиться">
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
              Подготовь черновик ответа клиенту по задолженности и укажи, нужен ли approval директора.
            </p>
          </article>

          <article className="message assistant-message">
            <div className="message-toolbar">
              <button className="pill-button">Редактировать</button>
              <span className="risk-badge yellow">Yellow risk</span>
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
                <span>Approval</span>
                <strong>Главбух</strong>
              </div>
            </div>

            <div className="document-card">
              <div className="doc-icon">DOCX</div>
              <div>
                <strong>Письмо клиенту о задолженности</strong>
                <span>Черновик документа</span>
              </div>
              <button className="compact-button">Открыто справа</button>
            </div>

            <div className="message-actions">
              <button>Copy</button>
              <button>Like</button>
              <button>Send to Agent 3</button>
            </div>
          </article>
        </div>

        <div className="composer-wrap">
          <div className="agent-row" aria-label="Выбор агента">
            <button className="agent-chip active">Agent 1 Fast</button>
            <button className="agent-chip">Agent 2 Strong</button>
            <button className="agent-chip">Agent 3 Reviewer</button>
          </div>
          <form className="composer">
            <button type="button" className="icon-button" aria-label="Добавить файл">
              +
            </button>
            <input aria-label="Сообщение" placeholder="Спросите Legal Factory AI" />
            <button type="button" className="compact-button">
              Расширенное
            </button>
            <button type="button" className="voice-button" aria-label="Отправить">
              Send
            </button>
          </form>
          <p className="disclaimer">Legal Factory AI может ошибаться. Важные выводы проверяются ответственным специалистом.</p>
        </div>
      </section>

      <aside className="document-pane">
        <header className="document-header">
          <div>
            <strong>Письмо клиенту о задолженности</strong>
            <span>Document · DOCX</span>
          </div>
          <div className="document-actions">
            <button className="icon-button" aria-label="Скачать">
              v
            </button>
            <button className="icon-button" aria-label="Закрыть документ">
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
                  <td>Желтый: требуется проверка бухгалтерии</td>
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
    </main>
  );
}
