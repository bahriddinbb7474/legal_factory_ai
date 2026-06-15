"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import Sidebar from "./components/Sidebar";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type Agent = {
  id: number;
  code: "lawyer_1" | "lawyer_2" | "lawyer_3";
  display_name: string;
  provider_code: string;
  model_name: string;
  input_price_per_1m: string;
  output_price_per_1m: string;
  supports_zdr: boolean;
};

type Provider = {
  provider_code: string;
  display_name: string;
  is_allowlisted: boolean;
  supports_zdr: boolean;
  is_trusted_for_sensitive: boolean;
  is_enabled: boolean;
};

type ChatMessage = {
  id?: number;
  author_type: "user" | "agent1" | "agent2" | "agent3" | "system";
  content: string;
  model_id?: string | null;
  provider_code?: string | null;
  input_tokens?: number;
  output_tokens?: number;
  cost_usd?: string;
  created_at?: string;
};

type OpenRouterModel = {
  model_id: string;
  name: string;
  provider: string;
  input_price: string;
  output_price: string;
  context_length: number;
  is_free: boolean;
  supports_zdr: boolean;
  supports_vision: boolean;
  is_available: boolean;
};

const fallbackAgents: Agent[] = [
  {
    id: 1,
    code: "lawyer_1",
    display_name: "Юрист 1",
    provider_code: "qwen",
    model_name: "qwen/qwen3.7-plus",
    input_price_per_1m: "0.320000",
    output_price_per_1m: "1.280000",
    supports_zdr: false,
  },
  {
    id: 2,
    code: "lawyer_2",
    display_name: "Юрист 2",
    provider_code: "deepseek",
    model_name: "deepseek/deepseek-r1",
    input_price_per_1m: "0.800000",
    output_price_per_1m: "0.800000",
    supports_zdr: false,
  },
  {
    id: 3,
    code: "lawyer_3",
    display_name: "Юрист 3 · Арбитр",
    provider_code: "google",
    model_name: "google/gemini-flash-1.5",
    input_price_per_1m: "0.075000",
    output_price_per_1m: "0.300000",
    supports_zdr: false,
  },
];

const initialDocumentBody =
  "Уважаемые партнеры, просим провести сверку взаиморасчетов и подтвердить срок оплаты задолженности по договору поставки.";

const initialMessages: ChatMessage[] = [
  {
    author_type: "user",
    content: "Подготовь черновик ответа клиенту по задолженности и укажи, нужно ли согласование директора.",
  },
  {
    author_type: "agent1",
    content:
      "Можно направить клиенту мягкое письмо с требованием сверки и оплаты. Финальное признание долга или уступки по срокам оплаты давать нельзя без проверки договора и бухгалтерии.",
    model_id: "qwen/qwen3.7-plus",
    provider_code: "qwen",
    input_tokens: 0,
    output_tokens: 0,
    cost_usd: "0.000000",
  },
];

const authorMeta: Record<ChatMessage["author_type"], string> = {
  user: "Пользователь",
  agent1: "Ю1",
  agent2: "Ю2",
  agent3: "Ю3",
  system: "Система",
};

export default function HomePage() {
  const [agents, setAgents] = useState<Agent[]>(fallbackAgents);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedLawyer, setSelectedLawyer] = useState<Agent["code"]>("lawyer_1");
  const [chatId, setChatId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [inputValue, setInputValue] = useState("");
  const [isInvoking, setIsInvoking] = useState(false);
  const [apiStatus, setApiStatus] = useState("");
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [selectedAgentForSettings, setSelectedAgentForSettings] = useState<Agent | null>(null);
  const [models, setModels] = useState<OpenRouterModel[]>([]);
  const [modelSearch, setModelSearch] = useState("");
  const [providerFilter, setProviderFilter] = useState("");
  const [onlyFree, setOnlyFree] = useState(false);
  const [onlyCheap, setOnlyCheap] = useState(false);
  const [onlyAllowlisted, setOnlyAllowlisted] = useState(true);
  const [settingsError, setSettingsError] = useState("");
  const [isDocumentOpen, setIsDocumentOpen] = useState(false);
  const [isDocumentEditing, setIsDocumentEditing] = useState(false);
  const [documentBody, setDocumentBody] = useState(initialDocumentBody);
  const [openDocumentMenu, setOpenDocumentMenu] = useState<"download" | "reply" | null>(null);

  const selectedAgent = agents.find((agent) => agent.code === selectedLawyer) ?? agents[0];
  const totalCost = messages.reduce((sum, message) => sum + Number(message.cost_usd ?? 0), 0);

  const filteredModels = useMemo(() => {
    const allowlistedProviders = new Set(providers.filter((provider) => provider.is_allowlisted).map((provider) => provider.provider_code));
    return models
      .filter((model) => model.name.toLowerCase().includes(modelSearch.toLowerCase()) || model.model_id.toLowerCase().includes(modelSearch.toLowerCase()))
      .filter((model) => !providerFilter || model.provider === providerFilter)
      .filter((model) => !onlyFree || model.is_free)
      .filter((model) => !onlyCheap || Number(model.input_price) <= 0.000001)
      .filter((model) => !onlyAllowlisted || allowlistedProviders.has(model.provider))
      .slice(0, 20);
  }, [modelSearch, models, onlyAllowlisted, onlyCheap, onlyFree, providerFilter, providers]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const lawyerNumber = params.get("lawyer");
    if (lawyerNumber === "1" || lawyerNumber === "2" || lawyerNumber === "3") {
      setSelectedLawyer(`lawyer_${lawyerNumber}` as Agent["code"]);
    }
    setIsDocumentOpen(params.get("document") === "open");
    setIsDocumentEditing(params.get("mode") === "edit");
    const menu = params.get("menu");
    if (menu === "download" || menu === "reply") {
      setOpenDocumentMenu(menu);
    }
    void loadSettingsData();
  }, []);

  async function loadSettingsData() {
    try {
      const [agentsResponse, providersResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/agents`),
        fetch(`${API_BASE_URL}/api/admin/providers`),
      ]);
      if (agentsResponse.ok) {
        setAgents(await agentsResponse.json());
      }
      if (providersResponse.ok) {
        setProviders(await providersResponse.json());
      }
    } catch {
      setApiStatus("Backend недоступен: UI работает в демонстрационном режиме.");
    }
  }

  async function ensureChat(): Promise<number> {
    if (chatId !== null) {
      return chatId;
    }
    const response = await fetch(`${API_BASE_URL}/api/chats`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Письмо клиенту о задолженности" }),
    });
    if (!response.ok) {
      throw new Error("Не удалось создать чат в backend.");
    }
    const chat = await response.json();
    setChatId(chat.id);
    return chat.id;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = inputValue.trim();
    if (!content || isInvoking) {
      return;
    }

    const userMessage: ChatMessage = { author_type: "user", content };
    setInputValue("");
    setMessages((current) => [...current, userMessage]);
    setIsInvoking(true);
    setApiStatus("");

    try {
      const nextChatId = await ensureChat();
      await fetch(`${API_BASE_URL}/api/chats/${nextChatId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userMessage),
      });
      const invokeResponse = await fetch(`${API_BASE_URL}/api/chats/${nextChatId}/invoke`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_code: selectedLawyer }),
      });
      if (!invokeResponse.ok) {
        const error = await invokeResponse.json().catch(() => ({ detail: "Ошибка OpenRouter" }));
        throw new Error(error.detail ?? "Ошибка OpenRouter");
      }
      const lawyerMessage = await invokeResponse.json();
      setMessages((current) => [...current, lawyerMessage]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          author_type: "system",
          content: error instanceof Error ? error.message : "Не удалось вызвать выбранного юриста.",
        },
      ]);
    } finally {
      setIsInvoking(false);
    }
  }

  async function openModelModal(agent: Agent) {
    setSelectedAgentForSettings(agent);
    setSettingsError("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/openrouter/models`);
      if (!response.ok) {
        throw new Error("Список моделей OpenRouter недоступен.");
      }
      setModels(await response.json());
    } catch (error) {
      setSettingsError(error instanceof Error ? error.message : "Не удалось загрузить модели.");
      setModels([]);
    }
  }

  async function saveModelChoice(model: OpenRouterModel) {
    if (!selectedAgentForSettings) {
      return;
    }
    setSettingsError("");
    const response = await fetch(`${API_BASE_URL}/api/admin/agents/${selectedAgentForSettings.code}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider_code: model.provider,
        model_name: model.model_id,
        input_price_per_1m: Number(model.input_price) * 1_000_000,
        output_price_per_1m: Number(model.output_price) * 1_000_000,
        supports_zdr: model.supports_zdr,
      }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Модель не сохранена." }));
      setSettingsError(error.detail ?? "Модель не сохранена.");
      return;
    }
    const updatedAgent = await response.json();
    setAgents((current) => current.map((agent) => (agent.code === updatedAgent.code ? updatedAgent : agent)));
    setSelectedAgentForSettings(null);
  }

  function closeDocumentPanel() {
    setIsDocumentOpen(false);
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
      <Sidebar onOpenSettings={() => setIsSettingsOpen(true)} />

      <section className="chat-area">
        <header className="topbar">
          <h1 className="chat-title">Долги / претензии · Письмо клиенту о задолженности…</h1>
          <div className="topbar-actions">
            <button className="compact-button" type="button">
              Расходы: ${totalCost.toFixed(2)}
            </button>
            <button className="icon-button" aria-label="Свернуть" type="button">
              ^
            </button>
            <button className="icon-button" aria-label="Еще" type="button">
              ...
            </button>
          </div>
        </header>

        <div className="conversation">
          {messages.map((message, index) =>
            message.author_type === "user" ? (
              <article className="message user-message" key={`${message.author_type}-${index}`}>
                <p>{message.content}</p>
              </article>
            ) : (
              <article className="message assistant-message" key={`${message.author_type}-${index}`}>
                <div className="message-toolbar">
                  <span className="assistant-meta">{messageLabel(message)}</span>
                  {message.author_type.startsWith("agent") ? <span className="risk-badge yellow">Жёлтый риск</span> : null}
                  {message.author_type.startsWith("agent") ? (
                    <button className="pill-button verdict-button" onClick={() => setIsDocumentOpen(true)} type="button">
                      Пометить как вердикт
                    </button>
                  ) : null}
                </div>
                <h1>{message.author_type === "system" ? "Статус" : "Краткий вывод"}</h1>
                <p>{message.content}</p>
                {message.author_type.startsWith("agent") ? (
                  <>
                    <div className="legal-grid">
                      <div>
                        <span>Модель</span>
                        <strong>{message.model_id ?? "не указана"}</strong>
                      </div>
                      <div>
                        <span>Провайдер</span>
                        <strong>{message.provider_code ?? "не указан"}</strong>
                      </div>
                      <div>
                        <span>Расход</span>
                        <strong>${Number(message.cost_usd ?? 0).toFixed(6)}</strong>
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
                      <button type="button">Копировать</button>
                      <button type="button">Нравится</button>
                      <button type="button">Отправить Юристу 3</button>
                    </div>
                  </>
                ) : null}
              </article>
            ),
          )}
        </div>

        <div className="composer-wrap">
          <form className="composer" onSubmit={handleSubmit}>
            <button type="button" className="icon-button" aria-label="Добавить файл">
              +
            </button>
            <input
              aria-label="Сообщение"
              placeholder="Спросите Legal Factory AI"
              value={inputValue}
              onChange={(event) => setInputValue(event.target.value)}
              disabled={isInvoking}
            />
            <button
              type="submit"
              className="voice-button"
              aria-label="Отправить выбранному юристу"
              disabled={isInvoking}
            >
              <span className="send-arrow" aria-hidden="true" />
            </button>
          </form>
          <div className="agent-row" aria-label="Выбор юриста">
            {agents.map((agent) => (
              <button
                className={agent.code === selectedLawyer ? "agent-chip active" : "agent-chip"}
                key={agent.code}
                onClick={() => setSelectedLawyer(agent.code)}
                type="button"
                disabled={isInvoking}
              >
                {agent.display_name} · {agent.model_name}
                {isInvoking && agent.code === selectedLawyer ? " · отвечает..." : ""}
              </button>
            ))}
          </div>
          <p className="disclaimer">{apiStatus || "Legal Factory AI может ошибаться. Важные выводы проверяются ответственным специалистом."}</p>
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
                    <button className="document-icon-button" onClick={() => setIsDocumentEditing(false)} title="Сохранить изменения" type="button" aria-label="Сохранить изменения">
                      ✓
                    </button>
                    <button className="document-icon-button cancel-edit-button" onClick={cancelDocumentChanges} title="Отменить изменения" type="button" aria-label="Отменить изменения">
                      ×
                    </button>
                  </>
                ) : (
                  <button className="document-icon-button" onClick={() => setIsDocumentEditing(true)} title="Редактировать документ" type="button" aria-label="Редактировать документ">
                    ✎
                  </button>
                )}
                <div className="document-menu-wrap">
                  <button className="document-icon-button" onClick={() => toggleDocumentMenu("download")} title="Скачать документ" type="button" aria-label="Скачать документ" aria-expanded={openDocumentMenu === "download"}>
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
                  <button className="document-icon-button" onClick={() => toggleDocumentMenu("reply")} title="Отправить документ в чат" type="button" aria-label="Отправить документ в чат" aria-expanded={openDocumentMenu === "reply"}>
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
              <button className="document-icon-button document-close-button" onClick={closeDocumentPanel} title="Закрыть документ" type="button" aria-label="Закрыть документ">
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
                  <textarea className="document-editor" aria-label="Текст документа" value={documentBody} onChange={(event) => setDocumentBody(event.target.value)} />
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
                <p>Письмо можно использовать как черновик. Перед отправкой нужно сверить сумму, срок оплаты и полномочия подписанта.</p>
              </section>
            </article>
          </div>
        </aside>
      ) : null}

      {isSettingsOpen ? (
        <div className="modal-backdrop">
          <section className="settings-modal">
            <header className="settings-header">
              <div>
                <strong>Профиль / Настройки</strong>
                <span>Модели юристов и провайдеры</span>
              </div>
              <button className="document-icon-button" onClick={() => setIsSettingsOpen(false)} type="button" aria-label="Закрыть настройки">
                ×
              </button>
            </header>
            <div className="settings-body">
              <section>
                <h2>Модели юристов</h2>
                <div className="settings-list">
                  {agents.map((agent) => (
                    <article className="settings-row" key={agent.code}>
                      <div>
                        <strong>{agent.display_name}</strong>
                        <span>{agent.provider_code} · {agent.model_name}</span>
                      </div>
                      <button className="compact-button" onClick={() => openModelModal(agent)} type="button">
                        Изменить
                      </button>
                    </article>
                  ))}
                </div>
              </section>
              <section>
                <h2>Провайдеры</h2>
                <div className="provider-grid">
                  {providers.map((provider) => (
                    <article className="provider-card" key={provider.provider_code}>
                      <strong>{provider.display_name}</strong>
                      <span>{provider.is_allowlisted ? "разрешен" : "запрещен"}</span>
                      <span>{provider.supports_zdr ? "ZDR" : "без ZDR"}</span>
                      <span>{provider.is_trusted_for_sensitive ? "доверен" : "не доверен для чувствительных документов"}</span>
                    </article>
                  ))}
                </div>
              </section>
            </div>
          </section>
        </div>
      ) : null}

      {selectedAgentForSettings ? (
        <div className="modal-backdrop">
          <section className="settings-modal model-modal">
            <header className="settings-header">
              <div>
                <strong>Выбор модели: {selectedAgentForSettings.display_name}</strong>
                <span>OpenRouter models</span>
              </div>
              <button className="document-icon-button" onClick={() => setSelectedAgentForSettings(null)} type="button" aria-label="Закрыть выбор модели">
                ×
              </button>
            </header>
            <div className="model-filters">
              <input placeholder="Поиск модели" value={modelSearch} onChange={(event) => setModelSearch(event.target.value)} />
              <select value={providerFilter} onChange={(event) => setProviderFilter(event.target.value)}>
                <option value="">Все провайдеры</option>
                {[...new Set(models.map((model) => model.provider))].map((provider) => (
                  <option key={provider} value={provider}>{provider}</option>
                ))}
              </select>
              <label><input type="checkbox" checked={onlyFree} onChange={(event) => setOnlyFree(event.target.checked)} /> Бесплатные</label>
              <label><input type="checkbox" checked={onlyCheap} onChange={(event) => setOnlyCheap(event.target.checked)} /> Дешёвые</label>
              <label><input type="checkbox" checked={onlyAllowlisted} onChange={(event) => setOnlyAllowlisted(event.target.checked)} /> Только разрешенные</label>
              <button className="compact-button" onClick={() => openModelModal(selectedAgentForSettings)} type="button">Обновить список</button>
            </div>
            {settingsError ? <p className="settings-error">{settingsError}</p> : null}
            <div className="model-list">
              {filteredModels.map((model) => (
                <article className="model-row" key={model.model_id}>
                  <div>
                    <strong>{model.name}</strong>
                    <span>{model.model_id} · {model.provider}</span>
                    <span>${model.input_price}/input · ${model.output_price}/output · {model.context_length} ctx</span>
                  </div>
                  <div className="model-tags">
                    {model.is_free ? <span>Бесплатная</span> : null}
                    {model.supports_zdr ? <span>ZDR</span> : null}
                    {model.supports_vision ? <span>Vision</span> : null}
                    <span>{model.is_available ? "доступна" : "недоступна"}</span>
                  </div>
                  <button className="compact-button" onClick={() => saveModelChoice(model)} disabled={!model.is_available} type="button">
                    Сохранить
                  </button>
                </article>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </main>
  );
}

function messageLabel(message: ChatMessage): string {
  const base = authorMeta[message.author_type];
  if (message.author_type === "user" || message.author_type === "system") {
    return base;
  }
  const time = message.created_at
    ? new Date(message.created_at).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })
    : "14:32";
  return `${base} · ${time}`;
}
