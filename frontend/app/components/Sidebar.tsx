"use client";

import { useMemo, useState } from "react";

import { normalizeSectionCode, type SectionCode, type SectionGroup } from "../sections";

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
  sectionGroups: readonly SectionGroup[];
  chatList: ChatListItem[];
  chatListLoading: boolean;
  chatListError: string | null;
  activeChatId: number | null;
  selectedSection: SectionCode | null;
  onNewChat: (section?: SectionCode | null) => void;
  onSelectChat: (chatId: number) => void;
  pendingInvokeByChatId: Record<number, boolean>;
};

export default function Sidebar({
  currentUser,
  canWriteWorkspace,
  onLogout,
  onOpenSettings,
  sectionGroups,
  chatList,
  chatListLoading,
  chatListError,
  activeChatId,
  selectedSection,
  onNewChat,
  onSelectChat,
  pendingInvokeByChatId,
}: SidebarProps) {
  const [expandedSection, setExpandedSection] = useState<SectionCode | null>(null);
  const [searchBySection, setSearchBySection] = useState<Record<string, string>>({});
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const initials = (currentUser.full_name.trim() || currentUser.email)
    .split(/\s+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const sectionEntries = useMemo(() => {
    const sections = sectionGroups.flatMap((group) => group.sections);
    const byCode = new Map<SectionCode, ChatListItem[]>(sections.map((section) => [section.code, []]));
    for (const chat of chatList) {
      byCode.get(normalizeSectionCode(chat.section))!.push(chat);
    }
    return sectionGroups.map((group) => ({
      ...group,
      sections: group.sections.map((section) => ({ ...section, chats: byCode.get(section.code)! })),
    }));
  }, [chatList, sectionGroups]);

  function handleCompose(sectionCode: SectionCode) {
    onNewChat(sectionCode);
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
        {sectionEntries.map((group) => (
          <div className="workspace-section-group" key={group.code}>
            <h2 className="workspace-section-group-label">{group.label}</h2>
            {group.sections.map(({ code: sectionCode, label: sectionLabel, chats: allChats }) => {
              const isExpanded = sectionCode === expandedSection;
              const query = searchBySection[sectionCode] ?? "";
              const visibleChats = allChats.filter((chat) =>
                chat.title.toLowerCase().includes(query.toLowerCase()),
              );
              const showNewChatPlaceholder = activeChatId === null && selectedSection === sectionCode;

              return (
                <section
                  className={isExpanded ? "workspace-section expanded" : "workspace-section"}
                  key={sectionCode}
                >
                  <div className="section-title-row">
                    <button
                      aria-expanded={isExpanded}
                      className="section-title"
                      onClick={() => setExpandedSection(isExpanded ? null : sectionCode)}
                      type="button"
                    >
                      <span className="section-chevron">{isExpanded ? "v" : ">"}</span>
                      <span>{sectionLabel}</span>
                    </button>
                    {canWriteWorkspace ? (
                      <button
                        className="compose-button"
                        onClick={() => handleCompose(sectionCode)}
                        title={`Новый чат: ${sectionLabel}`}
                        type="button"
                        aria-label={`Новый чат в разделе ${sectionLabel}`}
                      >
                        <span className="compose-glyph">✎</span>
                      </button>
                    ) : null}
                  </div>

                  {isExpanded && allChats.length > 3 ? (
                    <input
                      className="section-search"
                      aria-label={`Поиск в разделе ${sectionLabel}`}
                      placeholder="Поиск в разделе"
                      value={query}
                      onChange={(event) =>
                        setSearchBySection((current) => ({
                          ...current,
                          [sectionCode]: event.target.value,
                        }))
                      }
                    />
                  ) : null}

                  {isExpanded ? (
                    <div className="section-chat-list">
                      {showNewChatPlaceholder ? (
                        <button
                          className="section-chat active"
                          type="button"
                          onClick={() => onNewChat(sectionCode)}
                        >
                          Новый чат
                        </button>
                      ) : null}
                      {chatListLoading ? (
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
                  ) : null}
                </section>
              );
            })}
          </div>
        ))}
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
