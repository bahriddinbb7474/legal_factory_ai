"use client";

import { useMemo, useState } from "react";

type WorkspaceSection = {
  id: string;
  title: string;
  chats: string[];
};

const workspaceSections: WorkspaceSection[] = [
  {
    id: "contracts",
    title: "Договоры",
    chats: [
      "Проверка договора поставки N258",
      "Импортный контракт Китай",
      "Протокол разногласий UzCable",
      "Условия оплаты по дилеру",
      "Договор аренды склада",
    ],
  },
  {
    id: "claims",
    title: "Долги / претензии",
    chats: [
      "Долг клиента Navoiy Kabel",
      "Претензия по просрочке оплаты",
      "Сверка задолженности июнь",
      "Письмо о реструктуризации",
    ],
  },
  {
    id: "hr",
    title: "HR / кадры",
    chats: [
      "Приказ о дисциплине",
      "Трудовой договор мастера",
      "График отпусков производство",
      "Увольнение по соглашению",
    ],
  },
  {
    id: "court",
    title: "Судебные вопросы",
    chats: ["Досудебная позиция", "Иск по поставке", "Ответ на претензию юриста"],
  },
  {
    id: "tax",
    title: "ГНИ",
    chats: [
      "Ответ налоговой по запросу",
      "Пояснение по НДС",
      "Камеральная проверка",
      "Письмо о корректировке",
    ],
  },
  {
    id: "government",
    title: "Прочие Гос",
    chats: [
      "Письмо в таможенный орган",
      "Экология: официальный ответ",
      "Санитарный запрос",
      "Лицензия и сертификаты",
    ],
  },
  {
    id: "other",
    title: "Прочие",
    chats: ["Служебная записка директору", "Шаблон письма партнеру", "Общий юридический вопрос"],
  },
];

type SidebarProps = {
  onOpenSettings?: () => void;
};

export default function Sidebar({ onOpenSettings }: SidebarProps) {
  const [expandedSection, setExpandedSection] = useState("");
  const [activeChat, setActiveChat] = useState("Проверка договора поставки N258");
  const [searchBySection, setSearchBySection] = useState<Record<string, string>>({});

  const activeSection = useMemo(
    () => workspaceSections.find((section) => section.id === expandedSection) ?? workspaceSections[0],
    [expandedSection],
  );

  function startSectionChat(section: WorkspaceSection) {
    setExpandedSection(section.id);
    setActiveChat(`Новый чат · ${section.title}`);
  }

  return (
    <aside className="sidebar workspace-sidebar">
      <div className="sidebar-head workspace-brand">
        <div className="brand-mark">KT</div>
        <div className="brand-copy">
          <strong>Kabel Tech Energy</strong>
          <span>Legal Factory AI</span>
        </div>
        <button className="icon-button" aria-label="Свернуть меню">
          ||
        </button>
      </div>

      <div className="workspace-sections" aria-label="Разделы проекта">
        {workspaceSections.map((section) => {
          const isExpanded = section.id === expandedSection;
          const query = searchBySection[section.id] ?? "";
          const visibleChats = section.chats
            .filter((chat) => chat.toLowerCase().includes(query.toLowerCase()))
            .slice(0, isExpanded ? section.chats.length : 1);

          return (
            <section className={isExpanded ? "workspace-section expanded" : "workspace-section"} key={section.id}>
              <div className="section-title-row">
                <button
                  className="section-title"
                  onClick={() => setExpandedSection(isExpanded ? "" : section.id)}
                  type="button"
                >
                  <span className="section-chevron">{isExpanded ? "v" : ">"}</span>
                  <span>{section.title}</span>
                </button>
                <button
                  className="compose-button"
                  onClick={() => startSectionChat(section)}
                  title={`Новый чат: ${section.title}`}
                  type="button"
                  aria-label={`Новый чат в разделе ${section.title}`}
                >
                  <span className="compose-glyph">✎</span>
                </button>
              </div>

              {isExpanded && section.chats.length > 3 ? (
                <input
                  className="section-search"
                  aria-label={`Поиск в разделе ${section.title}`}
                  placeholder="Поиск в разделе"
                  value={query}
                  onChange={(event) =>
                    setSearchBySection((current) => ({ ...current, [section.id]: event.target.value }))
                  }
                />
              ) : null}

              <div className="section-chat-list">
                {activeChat === `Новый чат · ${section.title}` ? (
                  <button className="section-chat active" type="button">
                    Новый чат
                  </button>
                ) : null}
                {visibleChats.map((chat) => (
                  <button
                    className={chat === activeChat ? "section-chat active" : "section-chat"}
                    key={chat}
                    onClick={() => {
                      setExpandedSection(section.id);
                      setActiveChat(chat);
                    }}
                    type="button"
                  >
                    {chat}
                  </button>
                ))}
              </div>
            </section>
          );
        })}
      </div>

      <div className="profile-strip sidebar-profile">
        <button
          className="avatar profile-button"
          onClick={onOpenSettings}
          aria-label="Профиль / Настройки"
          type="button"
        >
          BB
        </button>
        <button className="profile-copy" onClick={onOpenSettings} type="button">
          <strong>Bahriddin Boboev</strong>
          <span>фин.директор</span>
        </button>
      </div>
    </aside>
  );
}
