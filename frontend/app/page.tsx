"use client";

import { ChangeEvent, FormEvent, useEffect, useRef, useMemo, useState } from "react";

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
  structured_payload?: LegalStructuredPayload | null;
  risk?: "green" | "yellow" | "red" | null;
  confidence?: "high" | "medium" | "low" | null;
  approval_required?: "none" | "chief_accountant" | "director" | "external_lawyer" | null;
  source_check_status?: "not_checked" | "confirmed" | "partially_confirmed" | "unconfirmed";
  red_flag_codes?: string[];
  model_id?: string | null;
  provider_code?: string | null;
  input_tokens?: number;
  output_tokens?: number;
  cost_usd?: string;
  created_at?: string;
  is_verdict?: boolean;
};

type LegalStructuredPayload = {
  summary: string;
  risk: "green" | "yellow" | "red";
  findings: { title: string; description: string }[];
  sources: {
    source_type: "uploaded_document" | "law" | "law_unconfirmed";
    document_id: number | null;
    legal_source_id?: number | null;
    title: string;
    document_type?: string | null;
    document_number: string | null;
    revision_date: string | null;
    article_or_point: string | null;
    source_name?: string | null;
    source_url?: string | null;
    quote: string;
    verification_status: "pending" | "confirmed" | "unconfirmed";
  }[];
  meaning_for_factory: string;
  actions: string[];
  confidence: "high" | "medium" | "low";
  approval_required: "none" | "chief_accountant" | "director" | "external_lawyer";
  agreement: {
    agreed_points: string[];
    disagreed_points: string[];
    unresolved_points: string[];
  } | null;
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

type UploadedDocument = {
  id: number;
  original_filename: string;
  mime_type: string;
  file_size: number;
  category: string;
  suggested_category: string;
  sensitivity: "normal" | "internal" | "sensitive";
  counterparty?: string | null;
  document_number?: string | null;
  document_date?: string | null;
  extraction_status: string;
  ocr_status: string;
};

type GeneratedDocument = {
  id: number;
  chat_id: number;
  verdict_message_id: number;
  created_by_agent_id: number | null;
  title: string;
  document_type: string;
  template_key?: string | null;
  content: string;
  status: "draft" | "needs_review" | "approved" | "rejected" | "archived";
};

type DocumentTemplate = {
  id: number;
  template_key: string;
  name: string;
  description: string;
  category: string;
  language: string;
  template_type: string;
  body_template: string;
  is_active: boolean;
  requires_approval: boolean;
};

type UploadForm = {
  category: string;
  sensitivity: "normal" | "internal" | "sensitive";
  counterparty: string;
  document_number: string;
  document_date: string;
};

type LegalSourceAdmin = {
  id: number;
  document_type: string;
  title: string;
  document_number: string | null;
  source_name: string;
  source_url: string | null;
  adoption_date: string | null;
  revision_date: string | null;
  last_checked_at: string | null;
  next_check_due_at: string | null;
  language: string;
  status: "active" | "outdated" | "draft" | "archived";
  official_status: "official" | "non_official" | "unknown";
  chunks_count: number;
  needs_revision_check: boolean;
  revision_warning: string | null;
  readiness_warnings: string[];
  readiness_warning_messages: string[];
};

type LegalSourceChunk = {
  id: number;
  chunk_index: number;
  article_or_point: string | null;
  section_title: string | null;
  text_preview: string;
  chunk_text: string;
  char_count: number;
  created_at: string;
};

type LegalSourceForm = {
  document_type: string;
  title: string;
  document_number: string;
  source_name: string;
  source_url: string;
  adoption_date: string;
  revision_date: string;
  language: string;
  status: "active" | "outdated" | "draft" | "archived";
  official_status: "official" | "non_official" | "unknown";
  last_checked_at: string;
  next_check_due_at: string;
  raw_text: string;
};

type CompanyProfile = {
  id: number;
  full_name: string;
  short_name: string;
  legal_address: string | null;
  actual_address: string | null;
  tax_id: string | null;
  oked: string | null;
  bank_name: string | null;
  bank_mfo: string | null;
  bank_account: string | null;
  director_name: string | null;
  chief_accountant_name: string | null;
  legal_responsible_name: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  logo_storage_key: string | null;
  letterhead_storage_key: string | null;
  is_active: boolean;
  notes: string | null;
};

type CompanyProfileForm = {
  full_name: string;
  short_name: string;
  legal_address: string;
  actual_address: string;
  tax_id: string;
  oked: string;
  bank_name: string;
  bank_mfo: string;
  bank_account: string;
  director_name: string;
  chief_accountant_name: string;
  legal_responsible_name: string;
  phone: string;
  email: string;
  website: string;
  notes: string;
};

const fallbackAgents: Agent[] = [
  {
    id: 1,
    code: "lawyer_1",
    display_name: "Юрист 1",
    provider_code: "novita",
    model_name: "inclusionai/ling-2.6-flash",
    input_price_per_1m: "0.010000",
    output_price_per_1m: "0.030000",
    supports_zdr: false,
  },
  {
    id: 2,
    code: "lawyer_2",
    display_name: "Юрист 2",
    provider_code: "cloudflare",
    model_name: "ibm-granite/granite-4.0-h-micro",
    input_price_per_1m: "0.017000",
    output_price_per_1m: "0.112000",
    supports_zdr: false,
  },
  {
    id: 3,
    code: "lawyer_3",
    display_name: "Юрист 3 · Арбитр",
    provider_code: "novita/fp4",
    model_name: "openai/gpt-oss-20b",
    input_price_per_1m: "0.040000",
    output_price_per_1m: "0.150000",
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
    model_id: "inclusionai/ling-2.6-flash",
    provider_code: "novita",
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
  const [chatApprovalStatus, setChatApprovalStatus] = useState<"draft" | "needs_review" | "approved" | "rejected" | "archived">("draft");
  const [approvalComment, setApprovalComment] = useState("");
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
  const [savedDocumentBody, setSavedDocumentBody] = useState(initialDocumentBody);
  const [generatedDocument, setGeneratedDocument] = useState<GeneratedDocument | null>(null);
  const [activeVerdictMessageId, setActiveVerdictMessageId] = useState<number | null>(null);
  const [openDocumentMenu, setOpenDocumentMenu] = useState<"download" | "reply" | null>(null);
  const [isCostOpen, setIsCostOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [uploadForm, setUploadForm] = useState<UploadForm>({
    category: "",
    sensitivity: "internal",
    counterparty: "",
    document_number: "",
    document_date: "",
  });
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<UploadedDocument | null>(null);
  const [selectedDocumentText, setSelectedDocumentText] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [legalSources, setLegalSources] = useState<LegalSourceAdmin[]>([]);
  const [legalSourceForm, setLegalSourceForm] = useState<LegalSourceForm>({
    document_type: "cabinet_resolution",
    title: "",
    document_number: "",
    source_name: "LEX.UZ",
    source_url: "",
    adoption_date: "",
    revision_date: "",
    language: "ru",
    status: "draft",
    official_status: "official",
    last_checked_at: "",
    next_check_due_at: "",
    raw_text: "",
  });
  const [legalSourceStatus, setLegalSourceStatus] = useState("");
  const [editingLegalSourceId, setEditingLegalSourceId] = useState<number | null>(null);
  const [expandedLegalSourceId, setExpandedLegalSourceId] = useState<number | null>(null);
  const [legalSourceChunks, setLegalSourceChunks] = useState<Record<number, LegalSourceChunk[]>>({});
  const [companyProfile, setCompanyProfile] = useState<CompanyProfile | null>(null);
  const [companyProfileForm, setCompanyProfileForm] = useState<CompanyProfileForm>({
    full_name: "",
    short_name: "",
    legal_address: "",
    actual_address: "",
    tax_id: "",
    oked: "",
    bank_name: "",
    bank_mfo: "",
    bank_account: "",
    director_name: "",
    chief_accountant_name: "",
    legal_responsible_name: "",
    phone: "",
    email: "",
    website: "",
    notes: "",
  });
  const [companyProfileStatus, setCompanyProfileStatus] = useState("");
  const [companyAssetUploading, setCompanyAssetUploading] = useState<"logo" | "letterhead" | null>(null);
  const [documentTemplates, setDocumentTemplates] = useState<DocumentTemplate[]>([]);
  const [selectedTemplateKey, setSelectedTemplateKey] = useState("client_debt_reminder");
  const [templateStatus, setTemplateStatus] = useState("");
  const [debtTemplateFields, setDebtTemplateFields] = useState({
    counterparty_name: "",
    counterparty_address: "",
    counterparty_tax_id: "",
    debt_amount: "",
    currency: "UZS",
    payment_basis: "",
    contract_number: "",
    contract_date: "",
    invoice_or_spec_number: "",
    due_date: "",
    overdue_days: "",
    requested_payment_deadline: "",
    responsible_person: "",
    additional_note: "",
    bank_details_note: "",
    attached_documents_note: "",
  });

  const selectedAgent = agents.find((agent) => agent.code === selectedLawyer) ?? agents[0];
  const selectedTemplate = documentTemplates.find((template) => template.template_key === selectedTemplateKey) ?? documentTemplates[0] ?? null;
  const totalCost = messages.reduce((sum, message) => sum + Number(message.cost_usd ?? 0), 0);
  const costBreakdown = useMemo(() => {
    const rows = new Map<string, { label: string; input: number; output: number; cost: number }>();
    messages
      .filter((message) => message.author_type.startsWith("agent"))
      .forEach((message) => {
        const key = `${message.author_type}-${message.provider_code ?? ""}-${message.model_id ?? ""}`;
        const row = rows.get(key) ?? {
          label: `${authorMeta[message.author_type]} · ${message.provider_code ?? "провайдер не указан"} · ${message.model_id ?? "модель не указана"}`,
          input: 0,
          output: 0,
          cost: 0,
        };
        row.input += message.input_tokens ?? 0;
        row.output += message.output_tokens ?? 0;
        row.cost += Number(message.cost_usd ?? 0);
        rows.set(key, row);
      });
    return [...rows.values()];
  }, [messages]);

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
      void loadLegalSources();
      void loadCompanyProfile();
      void loadDocumentTemplates();
    } catch {
      setApiStatus("Backend недоступен: UI работает в демонстрационном режиме.");
    }
  }

  async function loadLegalSources() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/legal-sources`);
      if (response.ok) {
        setLegalSources(await response.json());
      }
    } catch {
      setLegalSourceStatus("Юридическая база пока недоступна.");
    }
  }

  async function loadCompanyProfile() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-profile`);
      if (response.status === 404) {
        setCompanyProfile(null);
        setCompanyProfileStatus("");
        resetCompanyProfileForm();
        return;
      }
      if (response.ok) {
        const profile = (await response.json()) as CompanyProfile;
        setCompanyProfile(profile);
        setCompanyProfileForm({
          full_name: profile.full_name,
          short_name: profile.short_name,
          legal_address: profile.legal_address ?? "",
          actual_address: profile.actual_address ?? "",
          tax_id: profile.tax_id ?? "",
          oked: profile.oked ?? "",
          bank_name: profile.bank_name ?? "",
          bank_mfo: profile.bank_mfo ?? "",
          bank_account: profile.bank_account ?? "",
          director_name: profile.director_name ?? "",
          chief_accountant_name: profile.chief_accountant_name ?? "",
          legal_responsible_name: profile.legal_responsible_name ?? "",
          phone: profile.phone ?? "",
          email: profile.email ?? "",
          website: profile.website ?? "",
          notes: profile.notes ?? "",
        });
      }
    } catch {
      setCompanyProfileStatus("РџСЂРѕС„РёР»СЊ РєРѕРјРїР°РЅРёРё РїРѕРєР° РЅРµРґРѕСЃС‚СѓРїРµРЅ.");
    }
  }

  async function loadDocumentTemplates() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/document-templates`);
      if (!response.ok) {
        return;
      }
      const templates = (await response.json()) as DocumentTemplate[];
      setDocumentTemplates(templates);
      if (templates.length && !templates.some((template) => template.template_key === selectedTemplateKey)) {
        setSelectedTemplateKey(templates[0].template_key);
      }
    } catch {
      setTemplateStatus("Шаблоны документов пока недоступны.");
    }
  }

  async function saveCompanyProfile() {
    setCompanyProfileStatus("");
    const response = await fetch(`${API_BASE_URL}/api/company-profile`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: companyProfileForm.full_name,
        short_name: companyProfileForm.short_name,
        legal_address: emptyToNull(companyProfileForm.legal_address),
        actual_address: emptyToNull(companyProfileForm.actual_address),
        tax_id: emptyToNull(companyProfileForm.tax_id),
        oked: emptyToNull(companyProfileForm.oked),
        bank_name: emptyToNull(companyProfileForm.bank_name),
        bank_mfo: emptyToNull(companyProfileForm.bank_mfo),
        bank_account: emptyToNull(companyProfileForm.bank_account),
        director_name: emptyToNull(companyProfileForm.director_name),
        chief_accountant_name: emptyToNull(companyProfileForm.chief_accountant_name),
        legal_responsible_name: emptyToNull(companyProfileForm.legal_responsible_name),
        phone: emptyToNull(companyProfileForm.phone),
        email: emptyToNull(companyProfileForm.email),
        website: emptyToNull(companyProfileForm.website),
        notes: emptyToNull(companyProfileForm.notes),
        is_active: true,
      }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕС…СЂР°РЅРёС‚СЊ CompanyProfile." }));
      setCompanyProfileStatus(error.detail ?? "РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕС…СЂР°РЅРёС‚СЊ CompanyProfile.");
      return;
    }
    const profile = (await response.json()) as CompanyProfile;
    setCompanyProfile(profile);
    setCompanyProfileStatus("Р РµРєРІРёР·РёС‚С‹ РєРѕРјРїР°РЅРёРё СЃРѕС…СЂР°РЅРµРЅС‹.");
    await loadCompanyProfile();
  }

  async function uploadCompanyProfileAsset(assetType: "logo" | "letterhead", event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";
    if (!selectedFile) {
      return;
    }
    if (!companyProfile) {
      setCompanyProfileStatus("Create and save CompanyProfile before uploading assets.");
      return;
    }
    setCompanyAssetUploading(assetType);
    setCompanyProfileStatus("");
    try {
      const form = new FormData();
      form.append("file", selectedFile);
      const response = await fetch(`${API_BASE_URL}/api/company-profile/${assetType}`, {
        method: "POST",
        body: form,
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: `Failed to upload ${assetType}.` }));
        setCompanyProfileStatus(error.detail ?? `Failed to upload ${assetType}.`);
        return;
      }
      const profile = (await response.json()) as CompanyProfile;
      setCompanyProfile(profile);
      setCompanyProfileStatus(`${assetType === "logo" ? "Logo" : "Letterhead"} uploaded.`);
      await loadCompanyProfile();
    } finally {
      setCompanyAssetUploading(null);
    }
  }

  async function deleteCompanyProfileAsset(assetType: "logo" | "letterhead") {
    if (!companyProfile) {
      return;
    }
    setCompanyAssetUploading(assetType);
    setCompanyProfileStatus("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-profile/${assetType}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: `Failed to delete ${assetType}.` }));
        setCompanyProfileStatus(error.detail ?? `Failed to delete ${assetType}.`);
        return;
      }
      const profile = (await response.json()) as CompanyProfile;
      setCompanyProfile(profile);
      setCompanyProfileStatus(`${assetType === "logo" ? "Logo" : "Letterhead"} removed.`);
      await loadCompanyProfile();
    } finally {
      setCompanyAssetUploading(null);
    }
  }

  async function saveLegalSource() {
    setLegalSourceStatus("");
    if (editingLegalSourceId !== null) {
      const response = await fetch(`${API_BASE_URL}/api/admin/legal-sources/${editingLegalSourceId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_type: legalSourceForm.document_type,
          title: legalSourceForm.title,
          document_number: emptyToNull(legalSourceForm.document_number),
          source_name: legalSourceForm.source_name,
          source_url: emptyToNull(legalSourceForm.source_url),
          adoption_date: emptyToNull(legalSourceForm.adoption_date),
          revision_date: emptyToNull(legalSourceForm.revision_date),
          language: legalSourceForm.language || "ru",
          status: legalSourceForm.status,
          official_status: legalSourceForm.official_status,
          last_checked_at: localDateTimeToIso(legalSourceForm.last_checked_at),
          next_check_due_at: localDateTimeToIso(legalSourceForm.next_check_due_at),
        }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Не удалось сохранить metadata." }));
        setLegalSourceStatus(error.detail ?? "Не удалось сохранить metadata.");
        return;
      }
      resetLegalSourceForm();
      setLegalSourceStatus("Metadata источника сохранены.");
      await loadLegalSources();
      return;
    }

    const form = new FormData();
    form.append("document_type", legalSourceForm.document_type);
    form.append("title", legalSourceForm.title);
    form.append("document_number", legalSourceForm.document_number);
    form.append("source_name", legalSourceForm.source_name);
    form.append("source_url", legalSourceForm.source_url);
    form.append("adoption_date", legalSourceForm.adoption_date);
    form.append("revision_date", legalSourceForm.revision_date);
    form.append("language", legalSourceForm.language || "ru");
    form.append("status", legalSourceForm.status);
    form.append("official_status", legalSourceForm.official_status);
    form.append("raw_text", legalSourceForm.raw_text);
    const response = await fetch(`${API_BASE_URL}/api/admin/legal-sources`, { method: "POST", body: form });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Не удалось добавить источник." }));
      setLegalSourceStatus(error.detail ?? "Не удалось добавить источник.");
      return;
    }
    resetLegalSourceForm();
    setLegalSourceStatus("Источник добавлен и проиндексирован.");
    await loadLegalSources();
  }

  async function reindexLegalSource(sourceId: number) {
    const response = await fetch(`${API_BASE_URL}/api/admin/legal-sources/${sourceId}/reindex`, { method: "POST" });
    setLegalSourceStatus(response.ok ? "Источник переиндексирован." : "Не удалось переиндексировать источник.");
    await loadLegalSources();
    if (expandedLegalSourceId === sourceId) {
      await loadLegalSourceChunks(sourceId);
    }
  }

  async function loadLegalSourceChunks(sourceId: number) {
    const response = await fetch(`${API_BASE_URL}/api/admin/legal-sources/${sourceId}/chunks`);
    if (response.ok) {
      const chunks = (await response.json()) as LegalSourceChunk[];
      setLegalSourceChunks((current) => ({ ...current, [sourceId]: chunks }));
    }
  }

  async function toggleLegalSourceChunks(sourceId: number) {
    if (expandedLegalSourceId === sourceId) {
      setExpandedLegalSourceId(null);
      return;
    }
    setExpandedLegalSourceId(sourceId);
    if (!legalSourceChunks[sourceId]) {
      const response = await fetch(`${API_BASE_URL}/api/admin/legal-sources/${sourceId}/chunks`);
      if (response.ok) {
        const chunks = (await response.json()) as LegalSourceChunk[];
        setLegalSourceChunks((current) => ({ ...current, [sourceId]: chunks }));
      }
    }
  }

  function editLegalSource(source: LegalSourceAdmin) {
    setEditingLegalSourceId(source.id);
    setLegalSourceForm({
      document_type: source.document_type,
      title: source.title,
      document_number: source.document_number ?? "",
      source_name: source.source_name,
      source_url: source.source_url ?? "",
      adoption_date: source.adoption_date ?? "",
      revision_date: source.revision_date ?? "",
      language: source.language,
      status: source.status,
      official_status: source.official_status,
      last_checked_at: isoToLocalDateTime(source.last_checked_at),
      next_check_due_at: isoToLocalDateTime(source.next_check_due_at),
      raw_text: "",
    });
  }

  function resetLegalSourceForm() {
    setEditingLegalSourceId(null);
    setLegalSourceForm({
      document_type: "cabinet_resolution",
      title: "",
      document_number: "",
      source_name: "LEX.UZ",
      source_url: "",
      adoption_date: "",
      revision_date: "",
      language: "ru",
      status: "draft",
      official_status: "official",
      last_checked_at: "",
      next_check_due_at: "",
      raw_text: "",
    });
  }

  function resetCompanyProfileForm() {
    setCompanyProfileForm({
      full_name: "",
      short_name: "",
      legal_address: "",
      actual_address: "",
      tax_id: "",
      oked: "",
      bank_name: "",
      bank_mfo: "",
      bank_account: "",
      director_name: "",
      chief_accountant_name: "",
      legal_responsible_name: "",
      phone: "",
      email: "",
      website: "",
      notes: "",
    });
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
    setChatApprovalStatus(chat.approval_status ?? "draft");
    setActiveVerdictMessageId(chat.active_verdict_message_id ?? null);
    return chat.id;
  }

  async function refreshChatStatus(nextChatId: number) {
    const response = await fetch(`${API_BASE_URL}/api/chats/${nextChatId}`).catch(() => null);
    if (response?.ok) {
      const chat = await response.json();
      setChatApprovalStatus(chat.approval_status ?? "draft");
      setActiveVerdictMessageId(chat.active_verdict_message_id ?? null);
    }
  }

  async function changeApproval(action: "approve" | "reject" | "request-approval") {
    const nextChatId = await ensureChat();
    const suffix = approvalComment ? `?comment=${encodeURIComponent(approvalComment)}` : "";
    const response = await fetch(`${API_BASE_URL}/api/chats/${nextChatId}/${action}${suffix}`, { method: "POST" });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Не удалось изменить статус согласования." }));
      setApiStatus(error.detail ?? "Не удалось изменить статус согласования.");
      return;
    }
    const chat = await response.json();
    setChatApprovalStatus(chat.approval_status ?? "draft");
    setApprovalComment("");
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
      await refreshChatStatus(nextChatId);
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
      await refreshChatStatus(nextChatId);
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
      const providersResponse = await fetch(`${API_BASE_URL}/api/admin/providers`);
      if (providersResponse.ok) {
        setProviders(await providersResponse.json());
      }
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

  function handleFileSelection(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setPendingFile(file);
    setUploadForm({
      category: "",
      sensitivity: "internal",
      counterparty: "",
      document_number: "",
      document_date: "",
    });
    event.target.value = "";
  }

  async function uploadPendingFile() {
    if (!pendingFile || isUploading) {
      return;
    }
    setIsUploading(true);
    setApiStatus("");
    try {
      const nextChatId = await ensureChat();
      const form = new FormData();
      form.append("file", pendingFile);
      form.append("sensitivity", uploadForm.sensitivity);
      form.append("chat_id", String(nextChatId));
      if (uploadForm.category) form.append("category", uploadForm.category);
      if (uploadForm.counterparty) form.append("counterparty", uploadForm.counterparty);
      if (uploadForm.document_number) form.append("document_number", uploadForm.document_number);
      if (uploadForm.document_date) form.append("document_date", uploadForm.document_date);

      const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
        method: "POST",
        body: form,
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Не удалось загрузить документ." }));
        throw new Error(error.detail ?? "Не удалось загрузить документ.");
      }
      const payload = await response.json();
      setUploadedDocuments((current) => {
        if (current.some((document) => document.id === payload.document.id)) {
          return current;
        }
        return [...current, payload.document];
      });
      setPendingFile(null);
      setApiStatus(payload.extraction_error ? `Документ сохранен, обработка: ${payload.extraction_error}` : "Документ загружен и привязан к чату.");
    } catch (error) {
      setApiStatus(error instanceof Error ? error.message : "Не удалось загрузить документ.");
    } finally {
      setIsUploading(false);
    }
  }

  async function openUploadedDocument(document: UploadedDocument) {
    setSelectedDocument(document);
    setGeneratedDocument(null);
    setIsDocumentOpen(true);
    setIsDocumentEditing(false);
    setOpenDocumentMenu(null);
    setSelectedDocumentText("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/${document.id}/content`);
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Текст документа пока недоступен." }));
        throw new Error(error.detail ?? "Текст документа пока недоступен.");
      }
      const payload = await response.json();
      setSelectedDocumentText(payload.extracted_text);
    } catch (error) {
      setSelectedDocumentText(error instanceof Error ? error.message : "Текст документа пока недоступен.");
    }
  }

  async function removeDocumentFromChat(documentId: number) {
    if (chatId !== null) {
      await fetch(`${API_BASE_URL}/api/chats/${chatId}/documents/${documentId}`, { method: "DELETE" }).catch(() => undefined);
    }
    setUploadedDocuments((current) => current.filter((document) => document.id !== documentId));
    if (selectedDocument?.id === documentId) {
      setSelectedDocument(null);
      setIsDocumentOpen(false);
    }
  }

  function closeDocumentPanel() {
    setIsDocumentOpen(false);
    setIsDocumentEditing(false);
    setOpenDocumentMenu(null);
  }

  async function saveDocumentChanges() {
    if (generatedDocument) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/generated-documents/${generatedDocument.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: documentBody }),
        });
        if (response.ok) {
          const updatedDocument = await response.json();
          setGeneratedDocument(updatedDocument);
          setDocumentBody(updatedDocument.content);
          setSavedDocumentBody(updatedDocument.content);
        }
      } catch {
        setApiStatus("Не удалось сохранить документ в backend. Изменения оставлены локально.");
      }
    } else {
      setSavedDocumentBody(documentBody);
    }
    setIsDocumentEditing(false);
    setOpenDocumentMenu(null);
  }

  async function applySelectedTemplate() {
    if (!generatedDocument?.id || !selectedTemplate) {
      return;
    }
    setTemplateStatus("");
    try {
      const payloadData = {
        template_key: selectedTemplate.template_key,
        ...(selectedTemplate.template_key === "client_debt_reminder" || selectedTemplate.template_key === "client_debt_claim"
          ? {
              ...debtTemplateFields,
              counterparty_name: debtTemplateFields.counterparty_name || undefined,
              counterparty_address: debtTemplateFields.counterparty_address || undefined,
              counterparty_tax_id: debtTemplateFields.counterparty_tax_id || undefined,
              debt_amount: debtTemplateFields.debt_amount || undefined,
              currency: debtTemplateFields.currency || undefined,
              payment_basis: debtTemplateFields.payment_basis || undefined,
              contract_number: debtTemplateFields.contract_number || undefined,
              contract_date: debtTemplateFields.contract_date || undefined,
              invoice_or_spec_number: debtTemplateFields.invoice_or_spec_number || undefined,
              due_date: debtTemplateFields.due_date || undefined,
              overdue_days: debtTemplateFields.overdue_days || undefined,
              requested_payment_deadline: debtTemplateFields.requested_payment_deadline || undefined,
              responsible_person: debtTemplateFields.responsible_person || undefined,
              additional_note: debtTemplateFields.additional_note || undefined,
              bank_details_note: debtTemplateFields.bank_details_note || undefined,
              attached_documents_note: debtTemplateFields.attached_documents_note || undefined,
            }
          : {}),
      };

      const response = await fetch(`${API_BASE_URL}/api/generated-documents/${generatedDocument.id}/apply-template`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payloadData),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Не удалось применить шаблон." }));
        throw new Error(error.detail ?? "Не удалось применить шаблон.");
      }
      const payload = await response.json();
      setGeneratedDocument(payload.document);
      if (payload.document.template_key) {
        setSelectedTemplateKey(payload.document.template_key);
      }
      setDocumentBody(payload.document.content);
      setSavedDocumentBody(payload.document.content);
      setTemplateStatus(payload.missing_placeholders?.length ? `Не заполнены поля: ${payload.missing_placeholders.join(", ")}` : "Шаблон применён.");
    } catch (error) {
      setTemplateStatus(error instanceof Error ? error.message : "Не удалось применить шаблон.");
    }
  }

  function cancelDocumentChanges() {
    setDocumentBody(savedDocumentBody);
    setIsDocumentEditing(false);
    setOpenDocumentMenu(null);
  }

  async function markAsVerdict(message: ChatMessage, messageKey: number) {
    if (!message.id) {
      setActiveVerdictMessageId(messageKey);
      setMessages((current) =>
        current.map((item, index) => ({
          ...item,
          is_verdict: (item.id ?? -index) === messageKey,
        })),
      );
      return;
    }
    try {
      const nextChatId = await ensureChat();
      const response = await fetch(`${API_BASE_URL}/api/chats/${nextChatId}/messages/${message.id}/mark-verdict`, {
        method: "POST",
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Не удалось пометить вердикт." }));
        throw new Error(error.detail ?? "Не удалось пометить вердикт.");
      }
      const updated = await response.json();
      setActiveVerdictMessageId(updated.id);
      setMessages((current) =>
        current.map((item) => ({
          ...item,
          is_verdict: item.id === updated.id,
        })),
      );
      await refreshChatStatus(nextChatId);
    } catch (error) {
      setApiStatus(error instanceof Error ? error.message : "Не удалось пометить вердикт.");
    }
  }

  async function openGeneratedDocument(message: ChatMessage, messageKey: number) {
    setSelectedDocument(null);
    setTemplateStatus("");
    if (activeVerdictMessageId !== messageKey && !message.is_verdict) {
      await markAsVerdict(message, messageKey);
    }
    if (!message.id) {
      const mockDocument: GeneratedDocument = {
        id: 0,
        chat_id: chatId ?? 0,
        verdict_message_id: 0,
        created_by_agent_id: null,
        title: "Письмо клиенту о задолженности",
        document_type: selectedTemplate?.template_key ?? "claim_letter",
        template_key: selectedTemplate?.template_key ?? null,
        content: documentBody,
        status: "draft",
      };
      setGeneratedDocument(mockDocument);
      setSavedDocumentBody(mockDocument.content);
      setDocumentBody(mockDocument.content);
      setIsDocumentOpen(true);
      return;
    }
    try {
      const nextChatId = await ensureChat();
      const response = await fetch(`${API_BASE_URL}/api/chats/${nextChatId}/documents/generate-from-verdict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_code: selectedLawyer,
          document_type: selectedTemplate?.template_key ?? "claim_letter",
          template_key: selectedTemplate?.template_key ?? null,
          title: "Письмо клиенту о задолженности",
        }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Не удалось создать документ по вердикту." }));
        throw new Error(error.detail ?? "Не удалось создать документ по вердикту.");
      }
      const document = await response.json();
      setGeneratedDocument(document);
      if (document.template_key) {
        setSelectedTemplateKey(document.template_key);
      }
      setDocumentBody(document.content);
      setSavedDocumentBody(document.content);
      setIsDocumentOpen(true);
      setIsDocumentEditing(false);
      setOpenDocumentMenu(null);
    } catch (error) {
      setApiStatus(error instanceof Error ? error.message : "Не удалось создать документ по вердикту.");
      setIsDocumentOpen(true);
    }
  }

  async function sendDocumentToChat() {
    setOpenDocumentMenu(null);
    if (generatedDocument?.id) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/generated-documents/${generatedDocument.id}/send-to-chat`, {
          method: "POST",
        });
        if (!response.ok) {
          const error = await response.json().catch(() => ({ detail: "Не удалось отправить документ в общий чат." }));
          throw new Error(error.detail ?? "Не удалось отправить документ в общий чат.");
        }
      } catch (error) {
        setApiStatus(error instanceof Error ? error.message : "Не удалось отправить документ в общий чат.");
        return;
      }
    }
    setMessages((current) => [
      ...current,
      {
        author_type: "user",
        content: `Документ отправлен в общий чат для проверки: ${generatedDocument?.title ?? selectedDocument?.original_filename ?? "Письмо клиенту"}`,
      },
    ]);
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
            <span className={`approval-status ${chatApprovalStatus}`}>{approvalStatusLabel(chatApprovalStatus)}</span>
            <div className="cost-menu-wrap">
              <button className="compact-button" onClick={() => setIsCostOpen((current) => !current)} type="button" aria-expanded={isCostOpen}>
                Расходы: ${totalCost.toFixed(6)}
              </button>
              {isCostOpen ? (
                <div className="cost-dropdown">
                  <strong>Детализация расходов</strong>
                  {costBreakdown.length ? (
                    costBreakdown.map((row) => (
                      <div className="cost-row" key={row.label}>
                        <span>{row.label}</span>
                        <small>{row.input} input / {row.output} output</small>
                        <b>${row.cost.toFixed(6)}</b>
                      </div>
                    ))
                  ) : (
                    <span className="empty-costs">Пока нет реальных расходов.</span>
                  )}
                  <div className="cost-total">
                    <span>Итого</span>
                    <b>${totalCost.toFixed(6)}</b>
                  </div>
                </div>
              ) : null}
            </div>
            <button className="icon-button" aria-label="Свернуть" type="button">
              ^
            </button>
            <button className="icon-button" aria-label="Еще" type="button">
              ...
            </button>
          </div>
        </header>

        <div className="conversation">
          {messages.map((message, index) => {
            const messageKey = message.id ?? -index;
            const isActiveVerdict = message.is_verdict || activeVerdictMessageId === messageKey;
            return message.author_type === "user" ? (
              <article className="message user-message" key={`${message.author_type}-${index}`}>
                <p>{message.content}</p>
              </article>
            ) : (
              <article className="message assistant-message" key={`${message.author_type}-${index}`}>
                <div className="message-toolbar">
                  <span className="assistant-meta">{messageLabel(message)}</span>
                  {message.author_type.startsWith("agent") ? <span className={`risk-badge ${message.risk ?? message.structured_payload?.risk ?? "yellow"}`}>{riskLabel(message.risk ?? message.structured_payload?.risk ?? "yellow")}</span> : null}
                  {message.author_type.startsWith("agent") ? (
                    <button className={isActiveVerdict ? "pill-button verdict-button active-verdict" : "pill-button verdict-button"} onClick={() => markAsVerdict(message, messageKey)} type="button">
                      {isActiveVerdict ? "Действующий вердикт" : "Пометить как вердикт"}
                    </button>
                  ) : null}
                </div>
                <h1>{message.author_type === "system" ? "Статус" : "Краткий вывод"}</h1>
                <p>{message.content}</p>
                {message.structured_payload ? <StructuredAnswerSections message={message} /> : null}
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
                    <button className="document-card document-card-button" onClick={() => openGeneratedDocument(message, messageKey)} type="button">
                      <div className="doc-icon">DOCX</div>
                      <div>
                        <strong>{generatedDocument?.title ?? "Письмо клиенту о задолженности"}</strong>
                        <span>{isActiveVerdict ? "Документ создаётся строго из активного вердикта" : "Сначала будет выбран активный вердикт"}</span>
                      </div>
                      <span className="compact-button">{generatedDocument ? "Открыть справа" : "Создать справа"}</span>
                    </button>
                    <div className="message-actions">
                      <button type="button">Копировать</button>
                      <button type="button">Нравится</button>
                      <button type="button" onClick={() => openGeneratedDocument(message, messageKey)}>Сгенерировать документ</button>
                    </div>
                  </>
                ) : null}
              </article>
            );
          })}
        </div>

        <div className="composer-wrap">
          {chatApprovalStatus === "needs_review" ? (
            <div className="red-flag-banner">
              <strong>Тема серьёзная.</strong>
              <span>Рекомендуется мнение Юриста 2 или Юриста 3 и требуется утверждение руководства.</span>
            </div>
          ) : null}
          <div className="approval-panel">
            <input
              value={approvalComment}
              onChange={(event) => setApprovalComment(event.target.value)}
              placeholder="Комментарий к согласованию"
            />
            <button type="button" className="compact-button" onClick={() => changeApproval("request-approval")}>
              На согласование
            </button>
            <button type="button" className="compact-button" onClick={() => changeApproval("approve")}>
              Утвердить
            </button>
            <button type="button" className="compact-button" onClick={() => changeApproval("reject")}>
              Отклонить
            </button>
          </div>
          {uploadedDocuments.length ? (
            <div className="uploaded-documents">
              {uploadedDocuments.map((document) => (
                <div className="uploaded-document-chip" key={document.id}>
                  <button type="button" onClick={() => openUploadedDocument(document)}>
                    <strong>{document.original_filename}</strong>
                    <span>{document.category} · {document.sensitivity} · {document.extraction_status}</span>
                  </button>
                  <button type="button" aria-label="Убрать документ из чата" onClick={() => removeDocumentFromChat(document.id)}>
                    ×
                  </button>
                </div>
              ))}
            </div>
          ) : null}
          <input
            ref={fileInputRef}
            className="hidden-file-input"
            type="file"
            accept=".pdf,.docx,.xlsx,.txt,.jpg,.jpeg,.png,.webp"
            onChange={handleFileSelection}
          />
          <form className="composer" onSubmit={handleSubmit}>
            <button type="button" className="icon-button" aria-label="Добавить файл" onClick={() => fileInputRef.current?.click()}>
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
              <strong>{selectedDocument?.original_filename ?? generatedDocument?.title ?? "Письмо клиенту о задолженности"}</strong>
              <span>{selectedDocument ? `${selectedDocument.mime_type} · ${selectedDocument.extraction_status}` : `${approvalStatusLabel(generatedDocument?.status ?? "draft")} · GeneratedDocument`}</span>
            </div>
            <div className="document-actions">
              <div className="document-action-group">
                {isDocumentEditing ? (
                  <>
                    <button className="document-icon-button" onClick={saveDocumentChanges} title="Сохранить изменения" type="button" aria-label="Сохранить изменения">
                      ✓
                    </button>
                    <button className="document-icon-button cancel-edit-button" onClick={cancelDocumentChanges} title="Отменить изменения" type="button" aria-label="Отменить изменения">
                      ×
                    </button>
                  </>
                ) : !selectedDocument ? (
                  <button className="document-icon-button" onClick={() => setIsDocumentEditing(true)} title="Редактировать документ" type="button" aria-label="Редактировать документ">
                    ✎
                  </button>
                ) : (
                  <span className="document-action-placeholder" aria-hidden="true" />
                )}
                <div className="document-menu-wrap">
                  <button className="document-icon-button" onClick={() => toggleDocumentMenu("download")} title="Скачать документ" type="button" aria-label="Скачать документ" aria-expanded={openDocumentMenu === "download"}>
                    ⇩
                  </button>
                  {openDocumentMenu === "download" ? (
                    <div className="document-dropdown">
                      {selectedDocument ? (
                        <a href={`${API_BASE_URL}/api/documents/${selectedDocument.id}/download`}>Скачать оригинал</a>
                      ) : generatedDocument?.id ? (
                        <>
                          <a href={`${API_BASE_URL}/api/generated-documents/${generatedDocument.id}/download.docx`}>Скачать Word (.docx)</a>
                          <a href={`${API_BASE_URL}/api/generated-documents/${generatedDocument.id}/download.pdf`}>Скачать PDF (.pdf)</a>
                        </>
                      ) : (
                        <>
                          <button type="button">Скачать Word (.docx)</button>
                          <button type="button">Скачать PDF (.pdf)</button>
                        </>
                      )}
                    </div>
                  ) : null}
                </div>
                <div className="document-menu-wrap">
                  <button className="document-icon-button" onClick={() => toggleDocumentMenu("reply")} title="Отправить документ в чат" type="button" aria-label="Отправить документ в чат" aria-expanded={openDocumentMenu === "reply"}>
                    ↩
                  </button>
                  {openDocumentMenu === "reply" ? (
                    <div className="document-dropdown">
                      <button type="button" onClick={sendDocumentToChat}>Отправить в общий чат</button>
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
              {selectedDocument ? (
                <>
                  <div className="document-band">ЗАГРУЖЕННЫЙ ДОКУМЕНТ</div>
                  <h2>{selectedDocument.original_filename}</h2>
                  <table>
                    <tbody>
                      <tr>
                        <th>Категория</th>
                        <td>{selectedDocument.category}</td>
                      </tr>
                      <tr>
                        <th>Предложено</th>
                        <td>{selectedDocument.suggested_category}</td>
                      </tr>
                      <tr>
                        <th>Чувствительность</th>
                        <td>{selectedDocument.sensitivity}</td>
                      </tr>
                      <tr>
                        <th>OCR / extraction</th>
                        <td>{selectedDocument.ocr_status} / {selectedDocument.extraction_status}</td>
                      </tr>
                    </tbody>
                  </table>
                  {/*
                      Применить шаблон
                  <p className="settings-hint">Печать и подпись не вставляются до внедрения ролей и защищённого доступа.</p>
                  <div className="template-toolbar">
                    <select value={selectedTemplateKey} onChange={(event) => setSelectedTemplateKey(event.target.value)} disabled={!documentTemplates.length}>
                      {documentTemplates.map((template) => (
                        <option key={template.template_key} value={template.template_key}>
                          {template.name}
                        </option>
                      ))}
                    </select>
                    <button className="compact-button" type="button" onClick={() => void applySelectedTemplate()} disabled={!generatedDocument?.id || !selectedTemplate}>
                      РџСЂРёРјРµРЅРёС‚СЊ С€Р°Р±Р»РѕРЅ
                    </button>
                  </div>
                  <p className="settings-hint">РџРµС‡Р°С‚СЊ Рё РїРѕРґРїРёСЃСЊ РЅРµ РІСЃС‚Р°РІР»СЏСЋС‚СЃСЏ РґРѕ РІРЅРµРґСЂРµРЅРёСЏ СЂРѕР»РµР№ Рё Р·Р°С‰РёС‰С‘РЅРЅРѕРіРѕ РґРѕСЃС‚СѓРїР°.</p>
                  {templateStatus ? <p className="settings-hint">{templateStatus}</p> : null}
                  <div className="template-toolbar">
                    <select value={selectedTemplateKey} onChange={(event) => setSelectedTemplateKey(event.target.value)} disabled={!documentTemplates.length}>
                      {documentTemplates.map((template) => (
                        <option key={template.template_key} value={template.template_key}>
                          {template.name}
                        </option>
                      ))}
                    </select>
                    <button className="compact-button" type="button" onClick={() => void applySelectedTemplate()} disabled={!generatedDocument?.id || !selectedTemplate}>
                      РџСЂРёРјРµРЅРёС‚СЊ С€Р°Р±Р»РѕРЅ
                    </button>
                  </div>
                  <p className="settings-hint">РџРµС‡Р°С‚СЊ Рё РїРѕРґРїРёСЃСЊ РЅРµ РІСЃС‚Р°РІР»СЏСЋС‚СЃСЏ РґРѕ РІРЅРµРґСЂРµРЅРёСЏ СЂРѕР»РµР№ Рё Р·Р°С‰РёС‰С‘РЅРЅРѕРіРѕ РґРѕСЃС‚СѓРїР°.</p>
                  {templateStatus ? <p className="settings-hint">{templateStatus}</p> : null}
                  <div className="template-toolbar">
                    <select value={selectedTemplateKey} onChange={(event) => setSelectedTemplateKey(event.target.value)} disabled={!documentTemplates.length}>
                      {documentTemplates.map((template) => (
                        <option key={template.template_key} value={template.template_key}>
                          {template.name}
                        </option>
                      ))}
                    </select>
                    <button className="compact-button" type="button" onClick={() => void applySelectedTemplate()} disabled={!generatedDocument?.id || !selectedTemplate}>
                      РџСЂРёРјРµРЅРёС‚СЊ С€Р°Р±Р»РѕРЅ
                    </button>
                  </div>
                  <p className="settings-hint">РџРµС‡Р°С‚СЊ Рё РїРѕРґРїРёСЃСЊ РЅРµ РІСЃС‚Р°РІР»СЏСЋС‚СЃСЏ РґРѕ РІРЅРµРґСЂРµРЅРёСЏ СЂРѕР»РµР№ Рё Р·Р°С‰РёС‰С‘РЅРЅРѕРіРѕ РґРѕСЃС‚СѓРїР°.</p>
                  {templateStatus ? <p className="settings-hint">{templateStatus}</p> : null}
                  <section>
                    <h3>Извлечённый текст</h3>
                    <pre className="extracted-text">{selectedDocumentText || "Загрузка текста..."}</pre>
                  </section>
                  */}
                </>
              ) : (
                <>
                  <div className="document-band">ЧЕРНОВИК</div>
                  <h2>ООО “KABEL TECH ENERGY”</h2>
                  <p className="doc-center">111116, Республика Узбекистан, Ташкентская область</p>
                  <section>
                    <h3>{generatedDocument?.title ?? "Письмо о задолженности"}</h3>
                    <div className="template-toolbar">
                      <select value={selectedTemplateKey} onChange={(event) => setSelectedTemplateKey(event.target.value)} disabled={!documentTemplates.length}>
                        {documentTemplates.map((template) => (
                          <option key={template.template_key} value={template.template_key}>
                            {template.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    {(selectedTemplateKey === "client_debt_reminder" || selectedTemplateKey === "client_debt_claim") && (
                      <div className="template-fields-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '15px' }}>
                        <label>
                          <span>Контрагент *</span>
                          <input value={debtTemplateFields.counterparty_name} onChange={e => setDebtTemplateFields(f => ({ ...f, counterparty_name: e.target.value }))} />
                        </label>
                        <label>
                          <span>Адрес контрагента</span>
                          <input value={debtTemplateFields.counterparty_address} onChange={e => setDebtTemplateFields(f => ({ ...f, counterparty_address: e.target.value }))} />
                        </label>
                        <label>
                          <span>ИНН контрагента</span>
                          <input value={debtTemplateFields.counterparty_tax_id} onChange={e => setDebtTemplateFields(f => ({ ...f, counterparty_tax_id: e.target.value }))} />
                        </label>
                        <label>
                          <span>Сумма долга *</span>
                          <input value={debtTemplateFields.debt_amount} onChange={e => setDebtTemplateFields(f => ({ ...f, debt_amount: e.target.value }))} />
                        </label>
                        <label>
                          <span>Валюта *</span>
                          <input value={debtTemplateFields.currency} onChange={e => setDebtTemplateFields(f => ({ ...f, currency: e.target.value }))} />
                        </label>
                        <label>
                          <span>Основание платежа *</span>
                          <input value={debtTemplateFields.payment_basis} onChange={e => setDebtTemplateFields(f => ({ ...f, payment_basis: e.target.value }))} />
                        </label>
                        <label>
                          <span>Договор №</span>
                          <input value={debtTemplateFields.contract_number} onChange={e => setDebtTemplateFields(f => ({ ...f, contract_number: e.target.value }))} />
                        </label>
                        <label>
                          <span>Дата договора</span>
                          <input type="date" value={debtTemplateFields.contract_date} onChange={e => setDebtTemplateFields(f => ({ ...f, contract_date: e.target.value }))} />
                        </label>
                        <label>
                          <span>Спецификация/счёт №</span>
                          <input value={debtTemplateFields.invoice_or_spec_number} onChange={e => setDebtTemplateFields(f => ({ ...f, invoice_or_spec_number: e.target.value }))} />
                        </label>
                        <label>
                          <span>Срок оплаты</span>
                          <input type="date" value={debtTemplateFields.due_date} onChange={e => setDebtTemplateFields(f => ({ ...f, due_date: e.target.value }))} />
                        </label>
                        <label>
                          <span>Дней просрочки</span>
                          <input value={debtTemplateFields.overdue_days} onChange={e => setDebtTemplateFields(f => ({ ...f, overdue_days: e.target.value }))} />
                        </label>
                        <label>
                          <span>Срок для оплаты по письму</span>
                          <input value={debtTemplateFields.requested_payment_deadline} onChange={e => setDebtTemplateFields(f => ({ ...f, requested_payment_deadline: e.target.value }))} />
                        </label>
                        <label>
                          <span>Ответственный</span>
                          <input value={debtTemplateFields.responsible_person} onChange={e => setDebtTemplateFields(f => ({ ...f, responsible_person: e.target.value }))} />
                        </label>
                        <label>
                          <span>Доп. примечание</span>
                          <input value={debtTemplateFields.additional_note} onChange={e => setDebtTemplateFields(f => ({ ...f, additional_note: e.target.value }))} />
                        </label>
                        <label>
                          <span>Банковское примечание</span>
                          <input value={debtTemplateFields.bank_details_note} onChange={e => setDebtTemplateFields(f => ({ ...f, bank_details_note: e.target.value }))} />
                        </label>
                        <label>
                          <span>Приложения</span>
                          <input value={debtTemplateFields.attached_documents_note} onChange={e => setDebtTemplateFields(f => ({ ...f, attached_documents_note: e.target.value }))} />
                        </label>
                      </div>
                    )}
                    
                    <div style={{ marginBottom: '15px' }}>
                      <button className="compact-button" type="button" onClick={() => void applySelectedTemplate()} disabled={!generatedDocument?.id || !selectedTemplate}>
                        Применить шаблон
                      </button>
                    </div>

                    <p className="settings-hint">РџРµС‡Р°С‚СЊ Рё РїРѕРґРїРёСЃСЊ РЅРµ РІСЃС‚Р°РІР»СЏСЋС‚СЃСЏ РґРѕ РІРЅРµРґСЂРµРЅРёСЏ СЂРѕР»РµР№ Рё Р·Р°С‰РёС‰С‘РЅРЅРѕРіРѕ РґРѕСЃС‚СѓРїР°.</p>
                    {templateStatus ? <p className="settings-hint">{templateStatus}</p> : null}
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
                </>
              )}
            </article>
          </div>
        </aside>
      ) : null}

      {pendingFile ? (
        <div className="modal-backdrop">
          <section className="upload-modal">
            <header className="settings-header">
              <div>
                <strong>Загрузка документа</strong>
                <span>{pendingFile.name}</span>
              </div>
              <button className="document-icon-button" onClick={() => setPendingFile(null)} type="button" aria-label="Закрыть загрузку">
                ×
              </button>
            </header>
            <div className="upload-form">
              <label>
                <span>Категория</span>
                <select value={uploadForm.category} onChange={(event) => setUploadForm((current) => ({ ...current, category: event.target.value }))}>
                  <option value="">Определить автоматически</option>
                  <option value="local_contract">Обычный договор</option>
                  <option value="import_contract">Импортный контракт</option>
                  <option value="client_debt">Долги / претензии</option>
                  <option value="tax_letter">ГНИ / налоговое письмо</option>
                  <option value="government_letter">Госорган</option>
                  <option value="hr_document">HR / кадры</option>
                  <option value="order">Приказ</option>
                  <option value="occupational_safety">Охрана труда</option>
                  <option value="certificate">Сертификат</option>
                  <option value="template">Шаблон</option>
                  <option value="other">Прочее</option>
                </select>
              </label>
              <label>
                <span>Чувствительность</span>
                <select value={uploadForm.sensitivity} onChange={(event) => setUploadForm((current) => ({ ...current, sensitivity: event.target.value as UploadForm["sensitivity"] }))}>
                  <option value="normal">Обычный</option>
                  <option value="internal">Внутренний</option>
                  <option value="sensitive">Чувствительный</option>
                </select>
              </label>
              <label>
                <span>Контрагент</span>
                <input value={uploadForm.counterparty} onChange={(event) => setUploadForm((current) => ({ ...current, counterparty: event.target.value }))} />
              </label>
              <label>
                <span>Номер документа</span>
                <input value={uploadForm.document_number} onChange={(event) => setUploadForm((current) => ({ ...current, document_number: event.target.value }))} />
              </label>
              <label>
                <span>Дата документа</span>
                <input type="date" value={uploadForm.document_date} onChange={(event) => setUploadForm((current) => ({ ...current, document_date: event.target.value }))} />
              </label>
              <div className="upload-actions">
                <button className="compact-button" type="button" onClick={() => setPendingFile(null)}>
                  Отменить
                </button>
                <button className="agent-chip active" type="button" onClick={uploadPendingFile} disabled={isUploading}>
                  {isUploading ? "Загрузка..." : "Загрузить"}
                </button>
              </div>
            </div>
          </section>
        </div>
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
              <section>
                <h2>Юридическая база</h2>
                <p className="settings-hint">
                  Для Stage 7 желательно использовать LEX.UZ, действующую редакцию, заполнить номер, дату принятия, дату редакции и URL.
                </p>
                <h3>CompanyProfile</h3>
                <p className="settings-hint">
                  Stage 8-A stores company requisites for letters, claims, and future templates. Real stamp/signature assets must not be uploaded before access control and sensitive protection are implemented.
                </p>
                <div className="legal-source-form company-profile-form">
                  <input placeholder="Full name *" value={companyProfileForm.full_name} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, full_name: event.target.value }))} />
                  <input placeholder="Short name *" value={companyProfileForm.short_name} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, short_name: event.target.value }))} />
                  <input placeholder="Legal address" value={companyProfileForm.legal_address} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, legal_address: event.target.value }))} />
                  <input placeholder="Actual address" value={companyProfileForm.actual_address} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, actual_address: event.target.value }))} />
                  <input placeholder="TIN / tax_id" value={companyProfileForm.tax_id} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, tax_id: event.target.value }))} />
                  <input placeholder="OKED" value={companyProfileForm.oked} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, oked: event.target.value }))} />
                  <input placeholder="Bank name" value={companyProfileForm.bank_name} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, bank_name: event.target.value }))} />
                  <input placeholder="Bank MFO" value={companyProfileForm.bank_mfo} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, bank_mfo: event.target.value }))} />
                  <input placeholder="Bank account" value={companyProfileForm.bank_account} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, bank_account: event.target.value }))} />
                  <input placeholder="Director name" value={companyProfileForm.director_name} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, director_name: event.target.value }))} />
                  <input placeholder="Chief accountant" value={companyProfileForm.chief_accountant_name} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, chief_accountant_name: event.target.value }))} />
                  <input placeholder="Legal responsible" value={companyProfileForm.legal_responsible_name} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, legal_responsible_name: event.target.value }))} />
                  <input placeholder="Phone" value={companyProfileForm.phone} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, phone: event.target.value }))} />
                  <input placeholder="Email" value={companyProfileForm.email} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, email: event.target.value }))} />
                  <input placeholder="Website" value={companyProfileForm.website} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, website: event.target.value }))} />
                  <label className="company-asset-field">
                    <span>Logo asset</span>
                    <strong>{companyProfile?.logo_storage_key ? "uploaded" : "not uploaded"}</strong>
                    <input
                      type="file"
                      accept=".png,.jpg,.jpeg,.webp"
                      onChange={(event) => void uploadCompanyProfileAsset("logo", event)}
                      disabled={!companyProfile || companyAssetUploading !== null}
                    />
                    {companyProfile?.logo_storage_key ? (
                      <button className="compact-button" type="button" onClick={() => void deleteCompanyProfileAsset("logo")} disabled={companyAssetUploading !== null}>
                        Remove logo
                      </button>
                    ) : null}
                  </label>
                  <label className="company-asset-field">
                    <span>Letterhead asset</span>
                    <strong>{companyProfile?.letterhead_storage_key ? "uploaded" : "not uploaded"}</strong>
                    <input
                      type="file"
                      accept=".doc,.docx,.pdf,.png,.jpg,.jpeg"
                      onChange={(event) => void uploadCompanyProfileAsset("letterhead", event)}
                      disabled={!companyProfile || companyAssetUploading !== null}
                    />
                    {companyProfile?.letterhead_storage_key ? (
                      <button className="compact-button" type="button" onClick={() => void deleteCompanyProfileAsset("letterhead")} disabled={companyAssetUploading !== null}>
                        Remove letterhead
                      </button>
                    ) : null}
                  </label>
                  <textarea placeholder="Notes" value={companyProfileForm.notes} onChange={(event) => setCompanyProfileForm((current) => ({ ...current, notes: event.target.value }))} />
                  <div className="company-profile-placeholder">
                    <strong>Sensitive assets</strong>
                    <span>Stamp/signature uploads are disabled until roles/auth and sensitive protection are implemented.</span>
                  </div>
                  <button className="agent-chip active" type="button" onClick={saveCompanyProfile}>
                    {companyAssetUploading === null ? (companyProfile ? "Save CompanyProfile" : "Create CompanyProfile") : "Uploading..."}
                  </button>
                </div>
                {companyProfileStatus ? <p className="settings-error">{companyProfileStatus}</p> : null}
                <div className="company-profile-divider" />
                <div className="legal-source-form">
                  <select value={legalSourceForm.document_type} onChange={(event) => setLegalSourceForm((current) => ({ ...current, document_type: event.target.value }))}>
                    <option value="code">Кодекс</option>
                    <option value="law">Закон</option>
                    <option value="presidential_decree">Указ Президента</option>
                    <option value="presidential_resolution">ПП — Постановление Президента</option>
                    <option value="cabinet_resolution">ПКМ — Постановление Кабинета Министров</option>
                    <option value="ministerial_order">Приказ министерства</option>
                    <option value="technical_regulation">Технический регламент</option>
                    <option value="standard">Стандарт / O‘z DSt / ГОСТ</option>
                    <option value="tax_rule">Налоговый акт</option>
                    <option value="customs_rule">Таможенный акт</option>
                    <option value="other">Другое</option>
                  </select>
                  <input placeholder="Название" value={legalSourceForm.title} onChange={(event) => setLegalSourceForm((current) => ({ ...current, title: event.target.value }))} />
                  <input placeholder="Номер: ПКМ №999" value={legalSourceForm.document_number} onChange={(event) => setLegalSourceForm((current) => ({ ...current, document_number: event.target.value }))} />
                  <input placeholder="Источник: LEX.UZ" value={legalSourceForm.source_name} onChange={(event) => setLegalSourceForm((current) => ({ ...current, source_name: event.target.value }))} />
                  <input placeholder="LEX.UZ URL" value={legalSourceForm.source_url} onChange={(event) => setLegalSourceForm((current) => ({ ...current, source_url: event.target.value }))} />
                  <input type="date" value={legalSourceForm.adoption_date} onChange={(event) => setLegalSourceForm((current) => ({ ...current, adoption_date: event.target.value }))} />
                  <input type="date" value={legalSourceForm.revision_date} onChange={(event) => setLegalSourceForm((current) => ({ ...current, revision_date: event.target.value }))} />
                  <input placeholder="Язык: ru" value={legalSourceForm.language} onChange={(event) => setLegalSourceForm((current) => ({ ...current, language: event.target.value }))} />
                  <select value={legalSourceForm.status} onChange={(event) => setLegalSourceForm((current) => ({ ...current, status: event.target.value as LegalSourceForm["status"] }))}>
                    <option value="draft">draft</option>
                    <option value="active">active</option>
                    <option value="outdated">outdated</option>
                    <option value="archived">archived</option>
                  </select>
                  <select value={legalSourceForm.official_status} onChange={(event) => setLegalSourceForm((current) => ({ ...current, official_status: event.target.value as LegalSourceForm["official_status"] }))}>
                    <option value="official">official</option>
                    <option value="non_official">non_official</option>
                    <option value="unknown">unknown</option>
                  </select>
                  <label>
                    Last checked
                    <input type="datetime-local" value={legalSourceForm.last_checked_at} onChange={(event) => setLegalSourceForm((current) => ({ ...current, last_checked_at: event.target.value }))} />
                  </label>
                  <label>
                    Next check
                    <input type="datetime-local" value={legalSourceForm.next_check_due_at} onChange={(event) => setLegalSourceForm((current) => ({ ...current, next_check_due_at: event.target.value }))} />
                  </label>
                  <textarea
                    disabled={editingLegalSourceId !== null}
                    placeholder={editingLegalSourceId === null ? "Вставьте текст действующей редакции" : "Текст источника меняется через re-upload в следующих подэтапах; здесь редактируются metadata."}
                    value={legalSourceForm.raw_text}
                    onChange={(event) => setLegalSourceForm((current) => ({ ...current, raw_text: event.target.value }))}
                  />
                  <button className="agent-chip active" type="button" onClick={saveLegalSource}>
                    {editingLegalSourceId === null ? "Добавить источник" : "Сохранить metadata"}
                  </button>
                  {editingLegalSourceId !== null ? (
                    <button className="compact-button" type="button" onClick={resetLegalSourceForm}>
                      Отмена
                    </button>
                  ) : null}
                </div>
                {legalSourceStatus ? <p className="settings-error">{legalSourceStatus}</p> : null}
                <div className="settings-list">
                  {legalSources.map((source) => (
                    <article className="settings-row legal-source-row" key={source.id}>
                      <div>
                        <strong>{legalDocumentTypeLabel(source.document_type)} {source.document_number ?? ""}</strong>
                        <span>{source.title}</span>
                        <span>Тип: {source.document_type} · status: {source.status} · official: {source.official_status} · язык: {source.language}</span>
                        <span>Принят: {source.adoption_date ?? "не указано"} · редакция: {source.revision_date ?? "не указана"} · chunks: {source.chunks_count}</span>
                        <span>Проверка: {formatDateTime(source.last_checked_at)} · следующая: {formatDateTime(source.next_check_due_at)}</span>
                        <span>
                          Источник: {source.source_name}
                          {source.source_url ? (
                            <>
                              {" · "}
                              <a href={source.source_url} rel="noreferrer" target="_blank">URL</a>
                            </>
                          ) : " · URL не указан"}
                        </span>
                        {source.needs_revision_check ? <span className="source-freshness-warning">{source.revision_warning ?? "Редакцию нужно проверить"}</span> : null}
                        {source.readiness_warning_messages.length ? (
                          <div className="readiness-warning-list">
                            {source.readiness_warning_messages.map((warning, index) => (
                              <span className="readiness-warning" key={`${source.id}-${source.readiness_warnings[index]}`}>{source.readiness_warnings[index]}: {warning}</span>
                            ))}
                          </div>
                        ) : (
                          <span className="readiness-ok">Metadata готова для проверки перед active.</span>
                        )}
                        {expandedLegalSourceId === source.id ? (
                          <div className="chunk-preview-list">
                            {(legalSourceChunks[source.id] ?? []).map((chunk) => (
                              <article className="chunk-preview" key={chunk.id}>
                                <strong>Chunk {chunk.chunk_index + 1} · {chunk.article_or_point ?? "unknown"} · {chunk.char_count} chars</strong>
                                {chunk.section_title ? <span>{chunk.section_title}</span> : null}
                                <p>{chunk.text_preview}</p>
                              </article>
                            ))}
                          </div>
                        ) : null}
                      </div>
                      <div className="legal-source-actions">
                        <button className="compact-button" type="button" onClick={() => editLegalSource(source)}>
                          Редактировать
                        </button>
                        <button className="compact-button" type="button" onClick={() => toggleLegalSourceChunks(source.id)}>
                          {expandedLegalSourceId === source.id ? "Скрыть chunks" : "Показать chunks"}
                        </button>
                        <button className="compact-button" type="button" onClick={() => reindexLegalSource(source.id)}>
                          Reindex
                        </button>
                      </div>
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
                <article className="model-row" key={`${model.model_id}-${model.provider}`}>
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

function StructuredAnswerSections({ message }: { message: ChatMessage }) {
  const payload = message.structured_payload;
  if (!payload) {
    return null;
  }
  return (
    <div className="structured-answer">
      <section>
        <h2>Что обнаружено</h2>
        {payload.findings.map((finding) => (
          <div className="finding-row" key={`${finding.title}-${finding.description}`}>
            <strong>{finding.title}</strong>
            <span>{finding.description}</span>
          </div>
        ))}
      </section>
      <section>
        <h2>Источники</h2>
        {payload.sources.map((source, index) => (
          <article className={`source-row ${source.verification_status}`} key={`${source.title}-${index}`}>
            <strong>{source.source_type === "law" ? legalSourceTitle(source) : source.title}</strong>
            {source.source_type === "law" ? (
              <span>
                {source.revision_date ? `Редакция от ${source.revision_date}` : "Редакция не указана"}
                {source.article_or_point ? ` · ${source.article_or_point}` : ""}
                {source.source_name ? ` · Источник: ${source.source_name}` : ""}
              </span>
            ) : null}
            <span>{source.quote}</span>
            <b>{source.verification_status === "confirmed" ? "Подтверждено" : "Не подтверждено"}</b>
          </article>
        ))}
        {message.source_check_status && message.source_check_status !== "confirmed" ? (
          <p className="source-warning">Точный источник не найден. Окончательный юридический вывод давать нельзя. Требуется проверка юристом или ответственным специалистом.</p>
        ) : null}
      </section>
      <section>
        <h2>Значение для завода</h2>
        <p>{payload.meaning_for_factory}</p>
      </section>
      <section>
        <h2>Рекомендуемые действия</h2>
        <ul>{payload.actions.map((action) => <li key={action}>{action}</li>)}</ul>
      </section>
      <div className="legal-grid">
        <div><span>Уверенность</span><strong>{confidenceLabel(message.confidence ?? payload.confidence)}</strong></div>
        <div><span>Согласование</span><strong>{approvalRequiredLabel(message.approval_required ?? payload.approval_required)}</strong></div>
        <div><span>Источники</span><strong>{sourceStatusLabel(message.source_check_status ?? "not_checked")}</strong></div>
      </div>
      {payload.agreement ? (
        <section>
          <h2>Согласие / спорные пункты</h2>
          <div className="agreement-grid">
            <div><strong>Согласие</strong><span>{payload.agreement.agreed_points.join("; ") || "Нет"}</span></div>
            <div><strong>Несогласие</strong><span>{payload.agreement.disagreed_points.join("; ") || "Нет"}</span></div>
            <div><strong>Нерешено</strong><span>{payload.agreement.unresolved_points.join("; ") || "Нет"}</span></div>
          </div>
        </section>
      ) : null}
    </div>
  );
}

function riskLabel(risk: "green" | "yellow" | "red"): string {
  return { green: "Зелёный риск", yellow: "Жёлтый риск", red: "Красный риск" }[risk];
}

function confidenceLabel(confidence: "high" | "medium" | "low"): string {
  return { high: "Высокая", medium: "Средняя", low: "Низкая" }[confidence];
}

function approvalRequiredLabel(value: "none" | "chief_accountant" | "director" | "external_lawyer"): string {
  return { none: "Не требуется", chief_accountant: "Главбух", director: "Директор", external_lawyer: "Внешний юрист" }[value];
}

function sourceStatusLabel(value: "not_checked" | "confirmed" | "partially_confirmed" | "unconfirmed"): string {
  return { not_checked: "Не проверено", confirmed: "Подтверждено", partially_confirmed: "Частично", unconfirmed: "Не подтверждено" }[value];
}

function legalSourceTitle(source: LegalStructuredPayload["sources"][number]): string {
  const type = legalDocumentTypeLabel(source.document_type ?? "other");
  const number = source.document_number ? ` ${source.document_number}` : "";
  return `${type}${number} · ${source.title}`;
}

function legalDocumentTypeLabel(type: string): string {
  return {
    code: "Кодекс",
    law: "Закон",
    presidential_decree: "Указ Президента",
    presidential_resolution: "ПП",
    cabinet_resolution: "ПКМ",
    ministerial_order: "Приказ",
    technical_regulation: "Техрегламент",
    standard: "Стандарт",
    sanitary_rule: "Санитарные правила",
    fire_safety_rule: "Пожарные правила",
    customs_rule: "Таможенный акт",
    tax_rule: "Налоговый акт",
    other: "Акт",
  }[type] ?? "Акт";
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function localDateTimeToIso(value: string): string | null {
  if (!value) {
    return null;
  }
  return new Date(value).toISOString();
}

function isoToLocalDateTime(value: string | null): string {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function formatDateTime(value: string | null): string {
  if (!value) {
    return "не указано";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("ru-RU");
}

function approvalStatusLabel(value: "draft" | "needs_review" | "approved" | "rejected" | "archived"): string {
  return { draft: "Черновик", needs_review: "На согласовании", approved: "Утверждено", rejected: "Отклонено", archived: "Архив" }[value];
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
