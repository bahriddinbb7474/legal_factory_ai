"use client";

import { useMemo, useState } from "react";

type ChatListItem = {
  id: number;
  title: string;
  section?: string | null;
  status?: string;
  approval_status?: string;
};

type SidebarProps = {
  currentUser: { email: string; full_name: string; role: string };
  canWriteWorkspace: boolean;
  onLogout: () => void;
  onOpenSettings?: () => void;
  sections: readonly string[];
  chatList: ChatListItem[];
  chatListLoading: boolean;
  chatListError: string | null;
  activeChatId: number | null;
  selectedSection: string | null;
  onNewChat: (section?: string | null) => void;
  onSelectChat: (chatId: number) => void;
  pendingInvokeByChatId: Record<number, boolean>;
};

export default function Sidebar({
  currentUser,
  canWriteWorkspace,
  onLogout,
  onOpenSettings,
  sections,
  chatList,
  chatListLoading,
  chatListError,
  activeChatId,
  selectedSection,
  onNewChat,
  onSelectChat,
  pendingInvokeByChatId,
}: SidebarProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [searchBySection, setSearchBySection] = useState<Record<string, string>>({});
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const initials = (currentUser.full_name.trim() || currentUser.email)
    .split(/\s+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const sectionEntries = useMemo(() => {
    const byTitle = new Map<string, ChatListItem[]>(sections.map((t) => [t, []]));
    const others: ChatListItem[] = [];
    for (const chat of chatList) {
      const key = (chat.section ?? "").trim();
      if (byTitle.has(key)) {
        byTitle.get(key)!.push(chat);
      } else {
        others.push(chat);
      }
    }
    const result = sections.map((title) => ({ title, chats: byTitle.get(title)! }));
    if (others.length > 0) result.push({ title: "Прочие", chats: others });
    return result;
  }, [chatList, sections]);

  function handleCompose(sectionTitle: string) {
    setExpandedSection(sectionTitle);
    onNewChat(sectionTitle);
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
        {chatListError ? <p className="section-chat empty-hint">{chatListError}</p> : null}
        {sectionEntries.map(({ title: sectionTitle, chats: allChats }) => {
          const isExpanded = sectionTitle === expandedSection;
          const query = searchBySection[sectionTitle] ?? "";
          const visibleChats = allChats
            .filter((chat) => chat.title.toLowerCase().includes(query.toLowerCase()))
            .slice(0, isExpanded ? allChats.length : 1);
          const showNewChatPlaceholder = activeChatId === null && selectedSection === sectionTitle;

          return (
            <section
              className={isExpanded ? "workspace-section expanded" : "workspace-section"}
              key={sectionTitle}
            >
              <div className="section-title-row">
                <button
                  className="section-title"
                  onClick={() => setExpandedSection(isExpanded ? null : sectionTitle)}
                  type="button"
                >
                  <span className="section-chevron">{isExpanded ? "v" : ">"}</span>
                  <span>{sectionTitle}</span>
                </button>
                {canWriteWorkspace ? (
                  <button
                    className="compose-button"
                    onClick={() => handleCompose(sectionTitle)}
                    title={`Новый чат: ${sectionTitle}`}
                    type="button"
                    aria-label={`Новый чат в разделе ${sectionTitle}`}
                  >
                    <span className="compose-glyph">✎</span>
                  </button>
                ) : null}
              </div>

              {isExpanded && allChats.length > 3 ? (
                <input
                  className="section-search"
                  aria-label={`Поиск в разделе ${sectionTitle}`}
                  placeholder="Поиск в разделе"
                  value={query}
                  onChange={(event) =>
                    setSearchBySection((current) => ({
                      ...current,
                      [sectionTitle]: event.target.value,
                    }))
                  }
                />
              ) : null}

              <div className="section-chat-list">
                {showNewChatPlaceholder ? (
                  <button
                    className="section-chat active"
                    type="button"
                    onClick={() => onNewChat(sectionTitle)}
                  >
                    Новый чат
                  </button>
                ) : null}
                {chatListLoading && isExpanded ? (
                  <span className="section-chat empty-hint">Загрузка…</span>
                ) : (
                  visibleChats.map((chat) => (
                    <button
                      className={chat.id === activeChatId ? "section-chat active" : "section-chat"}
                      key={chat.id}
                      onClick={() => onSelectChat(chat.id)}
                      type="button"
                    >
                      {chat.title}
                      {pendingInvokeByChatId[chat.id] ? <span className="chat-pending-dot" aria-label="юрист отвечает"> ●</span> : null}
                    </button>
                  ))
                )}
              </div>
            </section>
          );
        })}
      </div>

      <div className="profile-strip sidebar-profile">
        {userMenuOpen && (
          <div className="user-menu">
            <div className="user-menu-header">
              <strong>{currentUser.full_name || currentUser.email}</strong>
              <span>{currentUser.email}</span>
              <span className="user-menu-role">{currentUser.role}</span>
            </div>
            {onOpenSettings && (
              <button
                className="user-menu-item"
                type="button"
                onClick={() => { setUserMenuOpen(false); onOpenSettings(); }}
              >
                Настройки
              </button>
            )}
            <button
              className="user-menu-item user-menu-logout"
              type="button"
              onClick={() => { setUserMenuOpen(false); onLogout(); }}
            >
              Выйти
            </button>
          </div>
        )}
        <button
          className="profile-toggle"
          onClick={() => setUserMenuOpen((v) => !v)}
          type="button"
          aria-expanded={userMenuOpen}
          aria-label="Меню пользователя"
        >
          <span className="avatar">{initials}</span>
          <span className="profile-info">
            <strong>{currentUser.full_name || currentUser.email}</strong>
            <span>{currentUser.role}</span>
          </span>
          <span className="profile-chevron" aria-hidden="true">{userMenuOpen ? "▴" : "▾"}</span>
        </button>
      </div>
    </aside>
  );
}
