"use client";

import {
  ArrowRight,
  ArrowUp,
  Check,
  ChevronDown,
  DoorOpen,
  ExternalLink,
  IndianRupee,
  LibraryBig,
  Menu,
  MessageSquareText,
  Moon,
  Percent,
  Plus,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Sun,
  X,
} from "lucide-react";
import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";

type Message = {
  id: number;
  role: "user" | "assistant";
  text: string;
  source?: string;
  refusal?: boolean;
  refusalType?: string;
};

type MockAnswer = {
  text: string;
  source: string;
};

const EXAMPLES = [
  {
    label: "Expense Ratio",
    question: "What is the expense ratio of Parag Parikh Flexi Cap Fund?",
    icon: Percent,
  },
  {
    label: "Exit Load",
    question: "What is the exit load for HDFC Mid Cap Fund?",
    icon: DoorOpen,
  },
  {
    label: "SIP Amount",
    question:
      "What is the minimum SIP amount for ICICI Prudential Technology Fund?",
    icon: IndianRupee,
  },
  {
    label: "Fund Cost",
    question: "What is the expense ratio of HDFC Mid Cap Fund?",
    icon: Percent,
  },
];

const FUND_GROUPS = [
  {
    name: "Parag Parikh",
    shortName: "PPFAS",
    funds: [
      "Long Term Value Fund",
      "ELSS Tax Saver Fund",
      "Large Cap Fund",
      "Conservative Hybrid Fund",
      "Liquid Fund",
    ],
  },
  {
    name: "HDFC",
    shortName: "HDFC",
    funds: [
      "Silver ETF FoF",
      "Mid Cap Fund",
      "Equity Fund",
      "Defence Fund",
      "Small Cap Fund",
      "Gold ETF Fund of Fund",
      "Nifty 50 Index Fund",
    ],
  },
  {
    name: "ICICI Prudential",
    shortName: "ICICI Prudential",
    funds: [
      "Large Cap Fund",
      "Silver ETF FoF",
      "Dynamic Plan",
      "Technology Fund",
    ],
  },
  {
    name: "Motilal Oswal",
    shortName: "Motilal Oswal",
    funds: [
      "Focused Midcap 30 Fund",
      "Large and Midcap Fund",
      "Small Cap Fund",
      "Focused Multicap 35 Fund",
    ],
  },
];

const RESEARCH_TOPICS = [
  "NAV & AUM",
  "Costs & exit loads",
  "Minimum SIP",
  "Fund managers",
  "Benchmarks",
  "Lock-in periods",
];

const DEFAULT_RECENT_CHAT = "What is the exit load for HDFC Mid Cap Fund?";

function SourceMark({
  variant = "header",
}: {
  variant?: "header" | "hero" | "assistant";
}) {
  return (
    <span className={`source-mark source-mark-${variant}`} aria-hidden="true">
      <span className="source-sheet source-sheet-back" />
      <span className="source-sheet source-sheet-mid" />
      <span className="source-sheet source-sheet-front">
        <i />
        <i />
      </span>
      <span className="source-check">
        <Check size={9} strokeWidth={3} />
      </span>
    </span>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [disclaimerVisible, setDisclaimerVisible] = useState(true);
  const [dark, setDark] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedAmc, setExpandedAmc] = useState("HDFC");
  const [coverageOpen, setCoverageOpen] = useState(false);
  const [recentChatTitle, setRecentChatTitle] = useState(DEFAULT_RECENT_CHAT);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Suppress react-hooks/set-state-in-effect warning by putting it in a timeout or handling it outside
    const savedRecentChat = window.localStorage.getItem("mf-faq-recent-chat");
    if (savedRecentChat) setRecentChatTitle(savedRecentChat);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }, [dark]);

  useEffect(() => {
    if (!coverageOpen) return;

    function closeOnEscape(event: globalThis.KeyboardEvent) {
      if (event.key === "Escape") setCoverageOpen(false);
    }

    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [coverageOpen]);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  function resizeTextarea() {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 104)}px`;
  }

  async function submitQuestion(rawQuestion?: string) {
    const question = (rawQuestion ?? input).trim();
    if (!question || loading) return;

    if (!messages.some((message) => message.role === "user")) {
      setRecentChatTitle(question);
      window.localStorage.setItem("mf-faq-recent-chat", question);
    }

    const userMessage: Message = {
      id: Math.random(),
      role: "user",
      text: question,
    };
    setMessages((current) => [...current, userMessage]);
    setCoverageOpen(false);
    setInput("");
    setLoading(true);
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question }),
      });
      const data = await res.json();
      
      setMessages((current) => [
        ...current,
        {
          id: Math.random(),
          role: "assistant",
          text: data.text,
          source: data.refusal ? undefined : data.source_url,
          refusal: data.refusal,
          refusalType: data.type,
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((current) => [
        ...current,
        {
          id: Math.random(),
          role: "assistant",
          text: "Sorry, I am having trouble connecting to the server.",
          refusal: true,
          refusalType: "error",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    submitQuestion();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitQuestion();
    }
  }

  function startNewChat() {
    if (loading) return;
    setMessages([]);
    setInput("");
    setSidebarOpen(false);
    setCoverageOpen(false);
    window.setTimeout(() => textareaRef.current?.focus(), 0);
  }

  return (
    <main className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "is-open" : ""}`}>
        <div className="sidebar-brand-row">
          <div className="brand sidebar-brand" aria-label="Mutual Fund FAQ Assistant">
            <SourceMark />
            <span className="brand-copy">
              <strong>Fund Query</strong>
              <small>Source-backed facts</small>
            </span>
          </div>
          <button
            className="sidebar-close"
            type="button"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        </div>

        <button
          className="new-chat-button"
          type="button"
          onClick={startNewChat}
          disabled={loading}
        >
          <Plus size={17} strokeWidth={2.2} />
          New chat
        </button>

        <nav className="sidebar-nav" aria-label="Research workspace">
          <section className="sidebar-section">
            <div className="sidebar-section-label">RECENT</div>
            <button
              className={`recent-chat ${messages.length ? "is-active" : ""}`}
              type="button"
              aria-current={messages.length ? "page" : undefined}
              onClick={() => {
                if (messages.length) return;
                setInput(recentChatTitle);
                setSidebarOpen(false);
                window.setTimeout(() => textareaRef.current?.focus(), 0);
              }}
            >
              <MessageSquareText size={15} />
              <span>
                <strong>{recentChatTitle}</strong>
                <small>{messages.length ? "Current chat" : "Last conversation"}</small>
              </span>
              {messages.length > 0 && <i aria-label="Active" />}
            </button>
          </section>

          <section className="sidebar-section coverage-section">
            <div className="sidebar-section-heading">
              <span className="sidebar-section-label">SCHEME COVERAGE</span>
              <small>20 total</small>
            </div>
            <div className="fund-groups">
              {FUND_GROUPS.map((group) => {
                const isExpanded = expandedAmc === group.name;
                return (
                  <div className={`fund-group ${isExpanded ? "is-expanded" : ""}`} key={group.name}>
                    <button
                      className="fund-group-button"
                      type="button"
                      onClick={() => setExpandedAmc(isExpanded ? "" : group.name)}
                      aria-expanded={isExpanded}
                    >
                      <span className="fund-group-icon">
                        <LibraryBig size={14} />
                      </span>
                      <span>
                        <strong>{group.shortName}</strong>
                        <small>{group.funds.length} schemes</small>
                      </span>
                      <ChevronDown size={15} className="fund-chevron" />
                    </button>
                    {isExpanded && (
                      <div className="fund-list">
                        {group.funds.map((fund) => (
                          <button
                            type="button"
                            key={fund}
                            onClick={() => {
                              setInput(`Tell me the key facts about ${group.name} ${fund}.`);
                              setSidebarOpen(false);
                              window.setTimeout(() => textareaRef.current?.focus(), 0);
                            }}
                          >
                            <i aria-hidden="true" />
                            <span>{fund}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        </nav>

        <div className="sidebar-footnote">
          <ShieldCheck size={15} />
          <span>
            <strong>Facts-only workspace</strong>
            <small>No advice or recommendations</small>
          </span>
        </div>
      </aside>

      <button
        className={`sidebar-scrim ${sidebarOpen ? "is-visible" : ""}`}
        type="button"
        onClick={() => setSidebarOpen(false)}
        aria-label="Close navigation"
        tabIndex={sidebarOpen ? 0 : -1}
      />

      <div className="app-main">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="topbar-leading">
            <button
              className="menu-button"
              type="button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation"
            >
              <Menu size={19} />
            </button>
            <div className="mobile-brand brand" aria-label="Mutual Fund FAQ Assistant">
              <SourceMark />
              <span className="brand-copy">
                <strong>Fund Query</strong>
              </span>
            </div>
            <div className="chat-context">
              <strong>{messages.length ? "Current chat" : "New chat"}</strong>
            </div>
          </div>
          <div className="header-actions">
            <span className="index-status">
              <ShieldCheck size={13} /> Facts verified
            </span>
            <button
              className="icon-button"
              type="button"
              onClick={() => setDark((value) => !value)}
              aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
            >
              {dark ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </div>
      </header>

      <section
        className={`disclaimer ${disclaimerVisible ? "is-visible" : "is-hidden"}`}
        aria-hidden={!disclaimerVisible}
      >
        <div className="disclaimer-inner">
          <ShieldAlert size={17} aria-hidden="true" />
          <p>
            <strong>Facts only.</strong> This assistant does not offer investment
            advice, opinions, or recommendations.
          </p>
          <button
            type="button"
            onClick={() => setDisclaimerVisible(false)}
            aria-label="Dismiss disclaimer"
          >
            <X size={17} />
          </button>
        </div>
      </section>

      <div className="conversation" ref={scrollRef} aria-live="polite">
        {messages.length === 0 && !loading ? (
          <section className="welcome" aria-labelledby="welcome-title">
            <div className="welcome-intro">
              <div className="intro-copy">
                <div className="eyebrow">
                  <span aria-hidden="true" /> FACTUAL FUND QUERY
                </div>
                <h1 id="welcome-title">What would you like to know?</h1>
                <p className="welcome-copy">
                  Clear, factual answers about 20 mutual fund schemes-grounded
                  in tracked source pages, without opinions or recommendations.
                </p>
                <div className={`coverage-shell ${coverageOpen ? "is-open" : ""}`}>
                  <div className="coverage-row" aria-label="Coverage information">
                    <span className="coverage-live"><i /> Live index</span>
                    <span><b>20</b> schemes</span>
                    <span><b>4</b> AMCs</span>
                    <button
                      className="coverage-trigger"
                      type="button"
                      onClick={() => setCoverageOpen((value) => !value)}
                      aria-expanded={coverageOpen}
                      aria-controls="research-coverage-panel"
                      aria-label="Research coverage"
                    >
                      <span className="coverage-trigger-label coverage-trigger-long">Research coverage</span>
                      <span className="coverage-trigger-label coverage-trigger-short">Coverage</span>
                      <ChevronDown size={13} />
                    </button>
                  </div>

                  {coverageOpen && (
                    <>
                      <button
                        className="coverage-backdrop"
                        type="button"
                        onClick={() => setCoverageOpen(false)}
                        aria-label="Close research coverage"
                      />
                      <section
                        className="coverage-panel"
                        id="research-coverage-panel"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="coverage-panel-title"
                      >
                        <div className="coverage-panel-header">
                          <div>
                            <span className="coverage-panel-live"><i /> Knowledge base live</span>
                            <h2 id="coverage-panel-title">Research coverage</h2>
                          </div>
                          <button
                            type="button"
                            onClick={() => setCoverageOpen(false)}
                            aria-label="Close research coverage"
                          >
                            <X size={17} />
                          </button>
                        </div>
                        <p className="coverage-panel-copy">
                          Factual scheme details available from tracked source pages.
                        </p>
                        <div className="coverage-topic-grid">
                          {RESEARCH_TOPICS.map((topic) => (
                            <span key={topic}><Check size={12} /> {topic}</span>
                          ))}
                        </div>
                        <div className="coverage-panel-footer">
                          <ShieldCheck size={15} />
                          <span>
                            <strong>Facts only</strong>
                            <small>No advice or recommendations</small>
                          </span>
                        </div>
                      </section>
                    </>
                  )}
                </div>
              </div>

            </div>
            <div className="example-section">
              <div className="example-section-heading">
                <div>
                  <span>QUICK START</span>
                  <p>Popular facts to explore</p>
                </div>
                <span>Choose a question to begin</span>
              </div>
              <div className="example-grid">
                {EXAMPLES.map((example, index) => {
                  const ExampleIcon = example.icon;
                  return (
                    <button
                      className="example-card"
                      type="button"
                      key={example.label}
                      style={{ animationDelay: `${180 + index * 90}ms` }}
                      onClick={() => submitQuestion(example.question)}
                    >
                      <span className="example-card-top">
                        <span className="example-icon">
                          <ExampleIcon size={15} strokeWidth={2.15} />
                        </span>
                        <span className="example-label">{example.label}</span>
                        <span className="example-number">0{index + 1}</span>
                      </span>
                      <span className="example-question">{example.question}</span>
                      <span className="example-card-footer">
                        View sourced fact
                        <span className="example-arrow">
                          <ArrowRight size={15} />
                        </span>
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </section>
        ) : (
          <section className="thread" aria-label="Conversation">
            <div className="thread-heading">
              <span>Conversation</span>
              <button
                type="button"
                onClick={startNewChat}
                disabled={loading}
              >
                New chat
              </button>
            </div>
            {messages.map((message) =>
              message.role === "user" ? (
                <div className="message user-message" key={message.id}>
                  <p>{message.text}</p>
                </div>
              ) : (
                <div className="message assistant-message" key={message.id}>
                  <SourceMark variant="assistant" />
                  {message.refusal ? (
                    <div className="refusal-card">
                      <div className="refusal-title">
                        {message.refusalType === "pii_refusal" ? (
                          <><ShieldCheck size={17} /> Privacy boundary</>
                        ) : message.refusalType === "error" ? (
                          <><ShieldAlert size={17} /> Connection error</>
                        ) : (
                          <><ShieldAlert size={17} /> Facts-only boundary</>
                        )}
                      </div>
                      <p>{message.text}</p>
                      {message.refusalType !== "pii_refusal" && message.refusalType !== "error" && (
                        <a
                          href="https://www.amfiindia.com/investor-corner/knowledge-center"
                          target="_blank"
                          rel="noreferrer"
                        >
                          Learn more at AMFI <ArrowRight size={14} />
                        </a>
                      )}
                    </div>
                  ) : (
                    <div className="assistant-content">
                      <div className="assistant-label">Fund information</div>
                      <p className="answer-text">{message.text}</p>
                      <div className="citation">
                        <div className="citation-main">
                          <span className="source-dot" />
                          <span className="source-label">Source</span>
                          <a href={message.source} target="_blank" rel="noreferrer">
                            Groww scheme page <ExternalLink size={13} />
                          </a>
                        </div>
                        <p>Last updated from sources: 2026-07-14</p>
                      </div>
                    </div>
                  )}
                </div>
              ),
            )}
            {loading && (
              <div className="message assistant-message loading-message">
                <SourceMark variant="assistant" />
                <div className="typing-pill" role="status">
                  <span className="typing-dots" aria-hidden="true">
                    <i />
                    <i />
                    <i />
                  </span>
                  <em>Searching knowledge base...</em>
                </div>
              </div>
            )}
          </section>
        )}
      </div>

      <footer className="composer-wrap">
        <form className="composer" onSubmit={handleSubmit}>
          <div className="textarea-shell">
            <span className="composer-mark" aria-hidden="true">
              <Sparkles size={15} strokeWidth={2.1} />
            </span>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(event) => {
                setInput(event.target.value);
                resizeTextarea();
              }}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder="Ask a question about mutual funds..."
              aria-label="Ask a question about mutual funds"
            />
            <button
              className="send-button"
              type="submit"
              disabled={!input.trim() || loading}
              aria-label="Send question"
            >
              <ArrowUp size={18} strokeWidth={2.4} />
            </button>
          </div>
          <p>AI can make mistakes. Always verify with official sources.</p>
        </form>
      </footer>
      </div>
    </main>
  );
}
