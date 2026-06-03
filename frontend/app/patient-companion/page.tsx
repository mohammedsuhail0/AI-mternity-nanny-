"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ArrowRight, Baby, HeartPulse, PlayCircle, Wind } from "lucide-react";

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  text: string;
  actionLabel?: string | null;
  actionUrl?: string | null;
  pending?: boolean;
};

type ChatTurn = {
  role: "assistant" | "user";
  content: string;
};

type AttachmentItem = {
  name: string;
  content?: string;
  mime_type?: string;
};

type CompanionReply = {
  reply: string;
  safety_note: string;
  suggested_prompts: string[];
  action_label?: string | null;
  action_url?: string | null;
};

type CompanionChatRequest = {
  message: string;
  history: ChatTurn[];
  attachments: AttachmentItem[];
  journey: {
    stage_title: string;
    stage_detail: string;
    stage_label: string;
  };
};

type JourneyStage = {
  title: string;
  detail: string;
  status: "done" | "active" | "upcoming";
  label: string;
  exercise: string;
  duration: string;
  videoQuery: string;
  image: string;
};

const quickPrompts = [
  "What should I eat today?",
  "Is it safe to walk in pregnancy?",
  "Can I take this medicine?",
  "How do I understand my report?",
  "When should I seek urgent care?",
  "Show my pregnancy roadmap",
  "How healthy does my journey look?",
];

const roadmapStages: JourneyStage[] = [
  {
    title: "First steps",
    label: "Weeks 1-12",
    detail: "Confirm care plan, safe medicines, and daily basics.",
    status: "done",
    exercise: "Breathing reset",
    duration: "6 min",
    videoQuery: "prenatal breathing exercise beginners",
    image: "https://images.unsplash.com/photo-1512291313931-7de3622c0f7d?auto=format&fit=crop&w=900&q=80",
  },
  {
    title: "Early checks",
    label: "Weeks 13-20",
    detail: "Monitor nausea, blood pressure, and first screenings.",
    status: "done",
    exercise: "Gentle walk",
    duration: "12 min",
    videoQuery: "pregnancy walking workout gentle",
    image: "https://images.unsplash.com/photo-1506629905607-cf1e655f2ec6?auto=format&fit=crop&w=900&q=80",
  },
  {
    title: "Growth phase",
    label: "Weeks 21-32",
    detail: "Track baby movement, fetal heart rate, and report trends.",
    status: "active",
    exercise: "Prenatal yoga flow",
    duration: "15 min",
    videoQuery: "prenatal yoga gentle stretch",
    image: "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80",
  },
  {
    title: "Delivery prep",
    label: "Weeks 33+",
    detail: "Set the hospital plan and review warning signs.",
    status: "upcoming",
    exercise: "Labor prep mobility",
    duration: "10 min",
    videoQuery: "pregnancy labor prep mobility",
    image: "https://images.unsplash.com/photo-1511174511562-5f7f18b874f8?auto=format&fit=crop&w=900&q=80",
  },
];

const healthSignals = [
  { label: "Stability", value: "Steady", tone: "text-emerald-700" },
  { label: "Follow-up", value: "Routine", tone: "text-sky-700" },
  { label: "Safety", value: "Watch for red flags", tone: "text-amber-700" },
];

const emergencyCall = "tel:911";

const maternityHeroArt =
  "data:image/svg+xml;charset=utf-8," +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" fill="none">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#fff1f2"/>
          <stop offset="55%" stop-color="#fde2e4"/>
          <stop offset="100%" stop-color="#f8b4c6"/>
        </linearGradient>
      </defs>
      <rect width="1200" height="900" rx="48" fill="url(#bg)"/>
      <circle cx="930" cy="210" r="150" fill="#fff" fill-opacity="0.32"/>
      <circle cx="230" cy="710" r="220" fill="#fff" fill-opacity="0.16"/>
      <path d="M220 585c90-135 222-175 340-118 91 44 140 131 156 191 13 50 9 103-27 147-37 44-97 65-163 57-82-11-168-56-238-112-67-54-116-116-68-165z" fill="#ffffff" fill-opacity="0.38"/>
      <path d="M548 355c52-40 127-34 171 14 45 49 53 122 22 181-27 53-86 87-152 87-61 0-111-27-142-72-33-47-36-110-7-160 16-28 43-36 61-50 18-14 29-39 47-50z" fill="#fff" fill-opacity="0.72"/>
      <path d="M585 270c24 0 44 20 44 44s-20 44-44 44-44-20-44-44 20-44 44-44zm0 22c-12 0-22 10-22 22s10 22 22 22 22-10 22-22-10-22-22-22z" fill="#db2777" fill-opacity="0.9"/>
      <path d="M865 520c36 0 66 29 66 66 0 18-7 34-18 46-10 11-24 20-39 20-37 0-66-29-66-66s29-66 57-66z" fill="#fff" fill-opacity="0.7"/>
      <path d="M874 536c-3 0-5 2-5 5v18h-18c-3 0-5 2-5 5s2 5 5 5h18v18c0 3 2 5 5 5s5-2 5-5v-18h18c3 0 5-2 5-5s-2-5-5-5h-18v-18c0-3-2-5-5-5z" fill="#db2777"/>
      <text x="88" y="124" fill="#7c2d12" font-family="Georgia, serif" font-size="54" font-weight="700">Maternity Journey</text>
      <text x="88" y="178" fill="#9f1239" font-family="Arial, sans-serif" font-size="30">steady care, gentle guidance, safe movement</text>
    </svg>
  `);

const supportArt =
  "data:image/svg+xml;charset=utf-8," +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 700" fill="none">
      <defs>
        <linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#fff7ed"/>
          <stop offset="100%" stop-color="#fde68a"/>
        </linearGradient>
      </defs>
      <rect width="900" height="700" rx="40" fill="url(#bg2)"/>
      <circle cx="700" cy="170" r="110" fill="#fff" fill-opacity="0.35"/>
      <path d="M220 470c34-86 117-141 216-141 101 0 188 57 223 146 13 33 13 67 0 99-17 41-57 71-105 74-82 5-157-31-215-89-58-59-104-118-119-89z" fill="#fff" fill-opacity="0.45"/>
      <path d="M418 255c55 0 99 44 99 99s-44 99-99 99-99-44-99-99 44-99 99-99z" fill="#f472b6" fill-opacity="0.78"/>
      <path d="M468 315c-10-19-38-19-48 0-16 30 3 73 24 96 21-23 40-66 24-96z" fill="#fff" fill-opacity="0.9"/>
      <path d="M432 342c8-7 20-7 28 0 8 7 8 19 0 26-8 7-20 7-28 0-8-7-8-19 0-26z" fill="#be185d"/>
      <text x="62" y="104" fill="#7c2d12" font-family="Georgia, serif" font-size="44" font-weight="700">Calm support</text>
      <text x="62" y="154" fill="#9f1239" font-family="Arial, sans-serif" font-size="26">warm care for every stage</text>
    </svg>
  `);

const highlightStrip = [
  { label: "24x7 companion", icon: HeartPulse },
  { label: "Gentle guidance", icon: Wind },
  { label: "Stage-based tracks", icon: Baby },
  { label: "Exercise videos", icon: PlayCircle },
];

export default function PatientCompanionPage() {
  const storageKey = "ai-maternal-companion-chat";
  const attachmentsInputRef = useRef<HTMLInputElement | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Hi, I’m your pregnancy companion. Ask me about food, exercise, medicines, symptoms, or report results, and I’ll explain things in simple language.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [tips, setTips] = useState<string[]>(quickPrompts);
  const [activeStage, setActiveStage] = useState(2);
  const [attachments, setAttachments] = useState<AttachmentItem[]>([]);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const currentStage = roadmapStages[activeStage];

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved) as { messages?: ChatMessage[]; attachments?: AttachmentItem[]; activeStage?: number };
        if (Array.isArray(parsed.messages) && parsed.messages.length) {
          setMessages(parsed.messages);
        }
        if (Array.isArray(parsed.attachments)) {
          setAttachments(parsed.attachments);
        }
        if (typeof parsed.activeStage === "number") {
          setActiveStage(Math.min(Math.max(parsed.activeStage, 0), roadmapStages.length - 1));
        }
      }
    } catch {
      // Ignore storage errors.
    }
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem(
        storageKey,
        JSON.stringify({ messages, attachments, activeStage })
      );
    } catch {
      // Ignore storage errors.
    }
  }, [messages, attachments, activeStage]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function submitMessage(text?: string) {
    const message = (text ?? input).trim();
    if (!message || loading) return;

    const assistantId = `assistant-${Date.now()}`;
    const history = messages
      .filter((entry) => entry.role === "assistant" || entry.role === "user")
      .filter((entry) => !entry.pending)
      .map((entry) => ({ role: entry.role, content: entry.text }))

    setMessages((current) => [
      ...current,
      { id: `user-${Date.now()}`, role: "user", text: message },
      { id: assistantId, role: "assistant", text: "Thinking…", pending: true },
    ]);
    setInput("");
    setLoading(true);

    try {
      const requestBody: CompanionChatRequest = {
        message,
        history,
        attachments,
        journey: {
          stage_title: currentStage.title,
          stage_detail: currentStage.detail,
          stage_label: currentStage.label,
        },
      };

      const res = await api.post<CompanionReply>("/companion/chat", requestBody);
      setMessages((current) => [
        ...current.map((entry) =>
          entry.id === assistantId
            ? {
                ...entry,
                text: res.data.reply,
                actionLabel: res.data.action_label ?? null,
                actionUrl: res.data.action_url ?? null,
                pending: false,
              }
            : entry
        ),
      ]);
      setTips(res.data.suggested_prompts.length ? res.data.suggested_prompts : quickPrompts);
    } catch {
      setMessages((current) => [
        ...current.map((entry) =>
          entry.id === assistantId
            ? {
                ...entry,
                text: "I’m having trouble reaching the assistant right now. Please try again in a moment, or contact your maternity care team if this feels urgent.",
                pending: false,
              }
            : entry
        ),
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleAttachmentChange(event: React.ChangeEvent<HTMLInputElement>) {
    const fileList = Array.from(event.target.files ?? []);
    if (!fileList.length) return;

    const nextAttachments: AttachmentItem[] = [];

    for (const file of fileList.slice(0, 3)) {
      const isTextLike = file.type.startsWith("text/") || [".txt", ".md", ".csv", ".json", ".log"].some((extension) => file.name.toLowerCase().endsWith(extension));

      if (isTextLike) {
        const content = await file.text();
        nextAttachments.push({
          name: file.name,
          content: content.slice(0, 6000),
          mime_type: file.type || "text/plain",
        });
      } else {
        nextAttachments.push({
          name: file.name,
          mime_type: file.type || "application/octet-stream",
        });
      }
    }

    setAttachments((current) => [...current, ...nextAttachments].slice(-5));
    event.target.value = "";
  }

  return (
    <div className="min-h-screen bg-[#f4efe9] pb-24 pt-3 text-slate-950 lg:bg-[radial-gradient(circle_at_top,_rgba(244,114,182,0.12),_transparent_30%),linear-gradient(135deg,#f4efe9_0%,#fbf7f3_50%,#eef2ff_100%)] lg:pb-8">
      <div className="mx-auto grid w-full max-w-7xl gap-4 px-3 pb-4 sm:px-4 lg:grid-cols-[280px_minmax(0,1fr)] lg:gap-6 lg:px-6 xl:px-8">
        <aside className="hidden lg:flex lg:flex-col lg:gap-4 lg:rounded-[2rem] lg:border lg:border-white/80 lg:bg-white/85 lg:p-5 lg:shadow-[0_18px_50px_-35px_rgba(15,23,42,0.35)] lg:backdrop-blur-md">
          <div className="rounded-[1.5rem] bg-[#111827] p-5 text-white shadow-sm">
            <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-rose-200">AI Maternal Monitor</p>
            <h2 className="mt-2 text-2xl font-semibold font-display">Adaptive companion</h2>
            <p className="mt-3 text-sm leading-6 text-white/75">The mobile view keeps the app shell. Desktop switches to a workspace layout with a side rail and wider content zones.</p>
          </div>

          <div className="grid gap-3">
            <a href="#chat-panel" className="rounded-[1.2rem] bg-primary-600 px-4 py-4 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700">
              Jump to chat
            </a>
            <a href="#movement-plan" className="rounded-[1.2rem] border border-slate-200 bg-white px-4 py-4 text-sm font-semibold text-slate-800 shadow-sm transition hover:border-primary-300 hover:text-primary-700">
              Open plan
            </a>
            <button type="button" onClick={() => attachmentsInputRef.current?.click()} className="rounded-[1.2rem] border border-rose-200 bg-rose-50 px-4 py-4 text-left text-sm font-semibold text-rose-700 shadow-sm transition hover:bg-rose-100">
              Add files
            </button>
            <a href={emergencyCall} className="rounded-[1.2rem] border border-amber-200 bg-amber-50 px-4 py-4 text-sm font-semibold text-amber-900 shadow-sm transition hover:bg-amber-100">
              Emergency help
            </a>
          </div>

          <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.25em] text-slate-500">Desktop layout</p>
            <p className="mt-2 text-sm leading-6 text-slate-700">Three zones appear automatically: guidance, roadmap, and chat. The bottom dock stays only on mobile.</p>
          </div>

          <div className="rounded-[1.5rem] border border-slate-200 bg-white p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Quick focus</p>
            <div className="mt-3 grid gap-2 text-sm text-slate-700">
              <span>Food guidance</span>
              <span>Exercise guidance</span>
              <span>Medicine questions</span>
              <span>Report reading</span>
            </div>
          </div>
        </aside>

        <main className="flex min-w-0 flex-col gap-4">
        <header className="rounded-[2rem] border border-white/70 bg-[#111827] px-4 py-4 text-white shadow-[0_20px_50px_-24px_rgba(15,23,42,0.6)]">
          <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.28em] text-white/70">
            <span>AI Maternal Monitor</span>
            <span>9:41</span>
          </div>
          <div className="mt-3 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-rose-200">Patient companion</p>
              <h1 className="mt-1 text-2xl font-semibold leading-tight text-white font-display">Maternity care in your pocket</h1>
            </div>
            <div className="rounded-full bg-emerald-400/20 px-3 py-1 text-xs font-semibold text-emerald-200">Online</div>
          </div>
          <div className="mt-4 flex gap-2 overflow-x-auto pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            {highlightStrip.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="inline-flex shrink-0 items-center gap-2 rounded-full bg-white/10 px-3 py-2 text-xs font-medium text-white/90 backdrop-blur">
                  <Icon className="h-3.5 w-3.5 text-rose-200" />
                  {item.label}
                </div>
              );
            })}
          </div>
        </header>

        <div className="grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)] lg:items-start">
          <div className="flex flex-col gap-4">
            <section className="overflow-hidden rounded-[2rem] border border-white/70 bg-gradient-to-br from-white via-[#fff8f4] to-[#ffeef3] p-4 shadow-[0_22px_60px_-35px_rgba(190,24,93,0.45)]">
              <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
                <div className="relative overflow-hidden rounded-[1.75rem] border border-white/70 bg-slate-950">
                  <Image src={maternityHeroArt} alt="Expectant mother resting in a calm maternity setting" width={1200} height={900} className="aspect-[4/3] w-full object-cover opacity-95" priority />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/30 to-transparent" />
                  <div className="absolute inset-x-0 bottom-0 p-4 text-white">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-rose-200">Today’s rhythm</p>
                    <p className="mt-2 text-2xl font-semibold leading-tight font-display">Small steps, steady care, and clear movement guidance.</p>
                  </div>
                </div>

                <div className="grid gap-4">
                  <div className="grid grid-cols-2 gap-3 xl:grid-cols-1">
                    <Link href="#chat-panel" className="rounded-[1.4rem] bg-primary-600 px-4 py-4 text-center text-sm font-semibold text-white shadow-sm transition active:scale-[0.99]">
                      Chat now
                    </Link>
                    <Link href="#movement-plan" className="rounded-[1.4rem] border border-slate-200 bg-white px-4 py-4 text-center text-sm font-semibold text-slate-800 shadow-sm transition active:scale-[0.99]">
                      View plan
                    </Link>
                  </div>

                  <div className="grid grid-cols-2 gap-3 xl:grid-cols-1">
                    {healthSignals.map((signal) => (
                      <div key={signal.label} className="rounded-[1.3rem] bg-white p-4 shadow-sm ring-1 ring-slate-100">
                        <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">{signal.label}</p>
                        <p className={`mt-1 text-sm font-semibold ${signal.tone}`}>{signal.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            <section className="grid gap-4 rounded-[2rem] border border-white/70 bg-white/92 p-4 shadow-[0_18px_50px_-35px_rgba(15,23,42,0.35)]">
              <div className="rounded-[1.5rem] bg-[#111827] p-5 text-white shadow-sm sm:p-6">
                <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-rose-200">Live companion</p>
                <h2 className="mt-2 text-2xl font-semibold font-display sm:text-[2.1rem]">Made for a phone screen.</h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-white/75">Bigger taps, stacked cards, and a bottom-focused flow make it feel like a real app on mobile.</p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                {[['Food', 'Meals, hydration, cravings, and what to avoid.'],['Exercise', 'Safe movement, walking, stretching, and rest signals.'],['Medicine', 'What a medication is generally used for and questions to ask.'],['Reports', 'Plain-language help reading blood pressure, FHR, and scan notes.']].map(([title, detail]) => (
                  <button key={title} type="button" className="rounded-[1.3rem] border border-slate-200 bg-slate-50 px-4 py-4 text-left shadow-sm transition hover:border-rose-200 hover:bg-rose-50/70">
                    <p className="text-sm font-semibold text-slate-950">{title}</p>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{detail}</p>
                  </button>
                ))}
              </div>
            </section>

            <section id="chat-panel">
              <Card className="overflow-hidden border border-slate-200 bg-white shadow-[0_18px_50px_-35px_rgba(15,23,42,0.4)]" variant="default">
                <CardHeader>
                  <CardTitle>Chat with your pregnancy companion</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 rounded-[1.5rem] bg-slate-50 p-4">
                    <div className="flex flex-wrap items-center gap-3">
                      <button type="button" onClick={() => attachmentsInputRef.current?.click()} className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-primary-300 hover:text-primary-700">
                        Add files
                      </button>
                      <input ref={attachmentsInputRef} type="file" className="hidden" multiple onChange={handleAttachmentChange} />
                      <span className="text-xs text-slate-500">Attach notes or text files for the companion to read.</span>
                    </div>

                    {attachments.length ? (
                      <div className="flex flex-wrap gap-2">
                        {attachments.map((file) => (
                          <span key={file.name + (file.mime_type ?? "")} className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
                            {file.name}
                          </span>
                        ))}
                      </div>
                    ) : null}

                    <div className="flex gap-2 overflow-x-auto pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                      {tips.map((tip) => (
                        <button key={tip} type="button" onClick={() => submitMessage(tip)} className="shrink-0 rounded-full border border-slate-200 bg-white px-4 py-3 text-xs font-semibold text-slate-700 shadow-sm transition hover:border-primary-300 hover:text-primary-700">
                          {tip}
                        </button>
                      ))}
                    </div>

                    <div className="max-h-[48vh] space-y-3 overflow-y-auto rounded-[1.4rem] border border-slate-200 bg-white p-4 shadow-sm lg:max-h-[56vh]">
                      {messages.map((message) => (
                        <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                          <div className="max-w-[85%] space-y-2">
                            <div className={`whitespace-pre-wrap rounded-[1.25rem] px-4 py-3 text-sm leading-6 shadow-sm ${message.role === "user" ? "bg-primary-600 text-white" : message.pending ? "bg-slate-100 text-slate-500 animate-pulse" : "bg-slate-100 text-slate-800"}`}>
                              {message.text}
                            </div>
                            {message.actionLabel && message.actionUrl ? (
                              <a href={message.actionUrl} className="inline-flex rounded-full bg-rose-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-rose-700">
                                {message.actionLabel}
                              </a>
                            ) : null}
                          </div>
                        </div>
                      ))}
                      <div ref={bottomRef} />
                    </div>

                    <form
                      className="space-y-3 rounded-[1.4rem] bg-white p-3 shadow-sm ring-1 ring-slate-100"
                      onSubmit={(event) => {
                        event.preventDefault();
                        submitMessage();
                      }}
                    >
                      <textarea
                        value={input}
                        onChange={(event) => setInput(event.target.value)}
                        rows={4}
                        placeholder="Ask about diet, exercise, medicines, symptoms, or your report..."
                        className="w-full rounded-[1.4rem] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none ring-0 transition placeholder:text-slate-400 focus:border-primary-400"
                      />
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <p className="text-xs text-slate-500">This assistant gives educational guidance and does not replace medical care.</p>
                        <Button type="submit" loading={loading} className="px-5">
                          Send
                        </Button>
                      </div>
                    </form>
                  </div>
                </CardContent>
              </Card>
            </section>
          </div>

          <div className="flex flex-col gap-4">
            <section id="movement-plan" className="grid gap-4">
              <Card className="overflow-hidden border border-slate-200 bg-white shadow-[0_18px_50px_-35px_rgba(15,23,42,0.4)]" variant="default">
            <CardHeader>
              <CardTitle>Journey roadmap</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {roadmapStages.map((stage, index) => {
                  const isActive = activeStage === index;
                  return (
                    <button
                      key={stage.title}
                      type="button"
                      onClick={() => setActiveStage(index)}
                      className={`flex gap-4 rounded-[1.35rem] border p-4 text-left transition active:scale-[0.995] ${isActive ? "border-primary-300 bg-primary-50 shadow-sm" : "border-slate-100 bg-white hover:border-rose-200 hover:bg-rose-50/50"}`}
                    >
                      <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${stage.status === "done" ? "bg-emerald-100 text-emerald-700" : stage.status === "active" ? "bg-primary-600 text-white" : "bg-slate-200 text-slate-600"}`}>
                        {index + 1}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="font-semibold text-slate-950">{stage.title}</p>
                          <span className="rounded-full bg-white px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-rose-600 shadow-sm">{stage.label}</span>
                        </div>
                        <p className="mt-1 text-sm leading-6 text-slate-600">{stage.detail}</p>
                        <div className="mt-3 flex flex-wrap gap-2 text-xs font-medium text-slate-600">
                          <span className="rounded-full bg-white px-3 py-1 shadow-sm">{stage.exercise}</span>
                          <span className="rounded-full bg-white px-3 py-1 shadow-sm">{stage.duration}</span>
                          {isActive ? <span className="rounded-full bg-primary-600 px-3 py-1 text-white shadow-sm">Selected now</span> : null}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </CardContent>
              </Card>
            </section>

            <Card className="overflow-hidden border border-slate-200 bg-white shadow-[0_18px_50px_-35px_rgba(15,23,42,0.4)]" variant="default">
              <CardHeader subtitle={`${currentStage.label} • ${currentStage.exercise}`}>Movement video track</CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid gap-4 rounded-[1.35rem] border border-slate-100 bg-gradient-to-br from-white to-rose-50 p-4">
                    <div className="relative overflow-hidden rounded-[1.25rem]">
                      <Image src={currentStage.image} alt={currentStage.title} width={900} height={700} className="h-full min-h-[220px] w-full object-cover" />
                    </div>
                    <div className="flex flex-col justify-between gap-4">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-rose-700">Suggested movement</p>
                        <h3 className="mt-2 font-display text-3xl text-slate-950">{currentStage.exercise}</h3>
                        <p className="mt-3 text-sm leading-6 text-slate-600">{currentStage.detail}</p>
                      </div>
                      <div className="rounded-2xl border border-white bg-white p-4 shadow-sm">
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Search on YouTube</p>
                        <p className="mt-1 text-sm text-slate-700">{currentStage.videoQuery}</p>
                      </div>
                    </div>
                  </div>

                  <div className="overflow-hidden rounded-[1.35rem] border border-slate-200 bg-slate-950 shadow-lg">
                    <div className="relative">
                      <Image src={currentStage.image} alt={`${currentStage.title} exercise guidance`} width={900} height={600} className="aspect-video w-full object-cover opacity-90" />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-950/70 via-slate-950/20 to-transparent" />
                      <div className="absolute inset-x-0 bottom-0 p-5 text-white">
                        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-rose-200">Watch the track</p>
                        <p className="mt-2 text-2xl font-semibold font-display">{currentStage.exercise}</p>
                        <p className="mt-1 max-w-xl text-sm text-slate-100">{currentStage.detail}</p>
                        <div className="mt-4 flex flex-wrap gap-3">
                          <a
                            href={`https://www.youtube.com/results?search_query=${encodeURIComponent(currentStage.videoQuery)}`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-rose-50"
                          >
                            Open on YouTube
                            <PlayCircle className="h-4 w-4" />
                          </a>
                          <span className="rounded-full bg-white/15 px-4 py-2 text-sm font-medium text-white backdrop-blur">{currentStage.duration}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid gap-3 rounded-[1.35rem] border border-slate-100 bg-rose-50/70 p-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Suggested movement</p>
                      <p className="mt-1 font-semibold text-slate-950">{currentStage.exercise}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Video query</p>
                      <p className="mt-1 text-sm text-slate-700">{currentStage.videoQuery}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Duration</p>
                      <p className="mt-1 font-semibold text-slate-950">{currentStage.duration}</p>
                    </div>
                  </div>

                  <div className="space-y-3 rounded-[1.35rem] border border-slate-100 bg-white p-4">
                    {roadmapStages.map((stage, index) => (
                      <button
                        key={stage.title}
                        type="button"
                        onClick={() => setActiveStage(index)}
                        className={`flex w-full items-center justify-between rounded-[1.1rem] border px-4 py-3 text-left transition active:scale-[0.995] ${activeStage === index ? "border-primary-300 bg-primary-50" : "border-slate-100 bg-slate-50 hover:border-rose-200 hover:bg-rose-50/60"}`}
                      >
                        <div>
                          <p className="font-semibold text-slate-950">{stage.title}</p>
                          <p className="text-sm text-slate-600">{stage.exercise}</p>
                        </div>
                        <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-600 shadow-sm">Watch</span>
                      </button>
                    ))}
                  </div>

                  <div className="flex flex-wrap gap-3">
                    <a
                      href={`https://www.youtube.com/results?search_query=${encodeURIComponent(currentStage.videoQuery)}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                    >
                      Search this track on YouTube
                      <PlayCircle className="h-4 w-4" />
                    </a>
                    <div className="rounded-full bg-emerald-100 px-4 py-3 text-sm font-semibold text-emerald-700">Safe, gentle, stage-based suggestions</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-white/70 bg-white/90 px-4 py-3 backdrop-blur-md lg:hidden">
              <div className="mx-auto grid max-w-[430px] grid-cols-4 gap-2 lg:max-w-none">
                <a href="#movement-plan" className="rounded-[1rem] bg-slate-950 px-3 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.2em] text-white">
                  Plan
                </a>
                <a href="#chat-panel" className="rounded-[1rem] bg-primary-600 px-3 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.2em] text-white">
                  Chat
                </a>
                <button type="button" onClick={() => attachmentsInputRef.current?.click()} className="rounded-[1rem] bg-rose-100 px-3 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.2em] text-rose-700">
                  Files
                </button>
                <a href={emergencyCall} className="rounded-[1rem] bg-amber-100 px-3 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.2em] text-amber-900">
                  Help
                </a>
              </div>
            </nav>
          </div>
        </div>
      </main>
      </div>
    </div>
  );
}