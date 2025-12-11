import { useState, useRef, useEffect, useCallback, memo } from 'react'
import { Send, Trash2, AlertCircle, CheckCircle, Database, TrendingUp } from 'lucide-react'
import ClaimTable from './components/ClaimTable'
import AnalyticsChart from './components/AnalyticsChart'

// Professional Results Panel
const ResultsPanel = memo(({ sources }) => {
  if (!sources || sources.length === 0) return null;

  const claims = sources.map(s => s.metadata);

  // Calculate summary stats
  const stats = {
    total: claims.length,
    denied: claims.filter(c => c.status === 'Denied').length,
    approved: claims.filter(c => c.status === 'Approved').length,
    pending: claims.filter(c => c.status === 'Pending').length,
    totalAmount: claims.reduce((sum, c) => sum + (parseFloat(c.claim_amount) || 0), 0)
  };

  return (
    <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700/50 rounded-2xl overflow-hidden shadow-xl">
      {/* Results Header with Stats */}
      <div className="bg-slate-900/60 px-6 py-4 border-b border-slate-700/50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Database size={20} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">Query Results</h3>
              <p className="text-slate-400 text-xs">{stats.total} records found</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp size={16} className="text-cyan-400" />
            <span className="text-cyan-400 text-sm font-medium">
              ${stats.totalAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>

        {/* Quick Stats Bar */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3 text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <CheckCircle size={14} className="text-emerald-400" />
              <span className="text-emerald-400 text-xs font-medium">Approved</span>
            </div>
            <span className="text-white text-xl font-bold">{stats.approved}</span>
          </div>
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <AlertCircle size={14} className="text-red-400" />
              <span className="text-red-400 text-xs font-medium">Denied</span>
            </div>
            <span className="text-white text-xl font-bold">{stats.denied}</span>
          </div>
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl px-4 py-3 text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <AlertCircle size={14} className="text-amber-400" />
              <span className="text-amber-400 text-xs font-medium">Pending</span>
            </div>
            <span className="text-white text-xl font-bold">{stats.pending}</span>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="p-6">
        <div className="grid grid-cols-1 xl:grid-cols-[380px_1fr] gap-6">
          <AnalyticsChart claims={claims} />
          <ClaimTable claims={claims} />
        </div>
      </div>
    </div>
  );
});

ResultsPanel.displayName = 'ResultsPanel';

// Memoized Message Bubble
const MessageBubble = memo(({ msg }) => {
  const hasResults = msg.sources && msg.sources.length > 0;

  return (
    <div className="space-y-4 animate-fadeIn">
      {/* Message bubble - different styles based on context */}
      <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
        <div className={`shadow-lg
          ${msg.role === 'user'
            ? 'max-w-[80%] px-5 py-3 text-sm bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 text-white rounded-2xl rounded-tr-md'
            : hasResults
              ? 'px-4 py-2 bg-slate-800/60 border border-slate-700/30 text-slate-400 rounded-xl text-sm'
              : 'max-w-[85%] px-6 py-5 bg-slate-800/90 border border-slate-700/50 text-slate-100 rounded-2xl rounded-tl-md backdrop-blur-sm text-base leading-relaxed'
          }`}
        >
          <div className="whitespace-pre-wrap">{msg.content}</div>
        </div>
      </div>

      {/* Only show results panel when there are actual results */}
      {hasResults && <ResultsPanel sources={msg.sources} />}
    </div>
  );
});

MessageBubble.displayName = 'MessageBubble';

// Main component
const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { id: 1, role: 'ai', content: "👋 Hello! I'm your Claims Intelligence Assistant.\n\nI can help you analyze claims data, find patterns in denials, and answer questions about patients, providers, and treatments.\n\nTry asking:\n• \"Show all denied claims\"\n• \"Find claims for cardiology\"\n• \"What are the top denial reasons?\"" }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const MAX_MESSAGES = 20;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) setError('Backend is not responding correctly.');
      } catch (e) {
        setError('Unable to connect to backend.');
      }
    };
    checkHealth();
  }, [API_URL]);

  const handleSend = useCallback(async () => {
    if (!input.trim()) return
    setError(null)

    const userMsg = { id: Date.now(), role: 'user', content: input }

    setMessages(prev => [...prev, userMsg].slice(-MAX_MESSAGES))
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg.content })
      })

      if (!response.ok) throw new Error(`Server error: ${response.status}`)

      const data = await response.json()

      const aiMsg = {
        id: Date.now() + 1,
        role: 'ai',
        content: data.answer,
        sources: data.context || []
      }

      setMessages(prev => [...prev, aiMsg].slice(-MAX_MESSAGES))
    } catch (error) {
      setError(error.message || "Couldn't reach the backend.")
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'ai',
        content: "Sorry, I couldn't process your request. Please try again."
      }])
    } finally {
      setIsLoading(false)
    }
  }, [input, API_URL])

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  const handleClearHistory = useCallback(() => {
    setMessages([
      { id: Date.now(), role: 'ai', content: "🔄 Chat cleared. How can I help you analyze claims data?" }
    ]);
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center p-4">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-cyan-600/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-7xl h-[95vh] bg-slate-900/70 backdrop-blur-2xl border border-slate-700/40 rounded-3xl shadow-2xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="px-8 py-5 border-b border-slate-700/40 bg-slate-950/40 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
                <Database size={22} className="text-white" />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-400 rounded-full border-2 border-slate-900 animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                Claims Intelligence
              </h1>
              <p className="text-xs text-slate-500">Powered by RAG & LLM</p>
            </div>
          </div>
          <button
            onClick={handleClearHistory}
            className="flex items-center gap-2 px-4 py-2 text-xs text-slate-400 hover:text-white hover:bg-slate-800/50 rounded-xl transition-all border border-transparent hover:border-slate-700/50"
          >
            <Trash2 size={14} />
            Clear Chat
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="px-8 py-3 bg-red-500/10 border-b border-red-500/20 flex justify-between items-center">
            <span className="text-red-300 text-sm flex items-center gap-2">
              <AlertCircle size={16} />
              {error}
            </span>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-1.5 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-white text-xs transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800/80 border border-slate-700/50 px-6 py-4 rounded-2xl rounded-tl-md flex items-center gap-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-slate-400 text-sm">Analyzing claims data...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input Area */}
        <div className="px-8 py-6 bg-slate-950/40 border-t border-slate-700/40">
          <div className="flex gap-4">
            <input
              className="flex-1 bg-slate-800/60 border border-slate-700/50 rounded-2xl px-6 py-4 text-white text-sm placeholder-slate-500 outline-none focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/10 transition-all"
              placeholder="Ask about claims, denials, patients, or providers..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading}
              className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm rounded-2xl transition-all hover:shadow-xl hover:shadow-indigo-500/30 hover:-translate-y-0.5 flex items-center gap-2"
            >
              <Send size={18} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
