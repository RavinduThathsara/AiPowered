import { useEffect, useState } from 'react'
import { Link, NavLink, Route, Routes } from 'react-router-dom'
import { ArrowRight, Camera, HeartHandshake, Info, Languages, Menu, MessageCircle, Mic, ShieldCheck, Sparkles, Square, X } from 'lucide-react'
import { addConversationMessage, createConversation, deleteConversation, getConversation, listConversations, translateSignToVoice, translateVoiceToSign } from './api'

const nav = [['Home', '/'], ['Voice to Sign', '/voice-to-sign'], ['Sign to Voice', '/sign-to-voice'], ['History', '/history'], ['About', '/about']]

function Layout() {
  const [open, setOpen] = useState(false)
  return <div className="shell"><header><div className="container nav"><Link to="/" className="brand" onClick={() => setOpen(false)}><span className="logo"><MessageCircle size={20} /></span>SignBridge</Link><button className="menu" aria-label={open ? 'Close menu' : 'Open menu'} aria-expanded={open} onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button><nav className={open ? 'mobile-nav' : ''} aria-label="Primary navigation"><ul>{nav.map(([label, to]) => <li key={to}><NavLink to={to} end={to === '/'} onClick={() => setOpen(false)}>{label}</NavLink></li>)}</ul></nav></div></header><main><Routes><Route path="/" element={<Home />} /><Route path="/voice-to-sign" element={<VoiceToSign />} /><Route path="/sign-to-voice" element={<SignToVoice />} /><Route path="/history" element={<History />} /><Route path="/about" element={<About />} /></Routes></main><footer><div className="container footer-content"><span><HeartHandshake size={16} /> Built with accessibility at the center.</span><span>SignBridge · Phase 1 frontend demo</span></div></footer></div>
}

function Language({ value, onChange }) {
  return <label className="language"><Languages size={18} /><span><small>Sign language</small><select value={value} onChange={e => onChange(e.target.value)}><option value="ASL">American Sign Language (ASL)</option><option value="SLSL">Sri Lankan Sign Language (SLSL)</option></select></span></label>
}

function Home() {
  const [language, setLanguage] = useState('ASL')
  return <><section className="hero"><div className="container hero-grid"><div><p className="eyebrow"><Sparkles size={15} /> Communication without barriers</p><h1>A bridge between <em>every voice.</em></h1><p className="lead">SignBridge is a thoughtfully designed starting point for two-way communication between spoken language and sign language.</p><div className="actions"><Link className="button primary" to="/voice-to-sign">Try Voice to Sign <ArrowRight size={17} /></Link><Link className="button secondary" to="/sign-to-voice">Explore Sign to Voice</Link></div><p className="trust"><ShieldCheck size={18} /> Designed for privacy, clarity, and access</p></div><div className="preview"><span>DEMO PREVIEW</span><div className="preview-icon"><Mic size={32} /></div><h2>Your conversation, connected.</h2><p>A calm, clear interface for what comes next.</p><small>ASL / SLSL ready · Phase 1 foundation</small></div></div></section><section className="container section"><div className="section-heading"><div><p className="eyebrow">Choose your direction</p><h2>Communication, your way.</h2></div><Language value={language} onChange={setLanguage} /></div><div className="cards"><Feature icon={Mic} title="Voice to Sign Language" text="A future-ready space to turn spoken words into clear, visual sign language communication." to="/voice-to-sign" /><Feature icon={Camera} title="Sign Language to Voice" text="A welcoming camera interface prepared for sign recognition and spoken output in a later phase." to="/sign-to-voice" /></div></section></>
}

function Feature({ icon: Icon, title, text, to }) { return <article className="card"><span className="card-icon"><Icon size={22} /></span><h3>{title}</h3><p>{text}</p><Link to={to}>Explore demo <ArrowRight size={16} /></Link></article> }

function Workspace({ mode }) {
  const voice = mode === 'voice'
  const [language, setLanguage] = useState('ASL')
  const [active, setActive] = useState(false)
  const [input, setInput] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [saved, setSaved] = useState(false)
  const noun = voice ? 'recording' : 'camera'
  function toggleRecording() {
    if (!voice) {
      setActive(value => !value)
      return
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser. You can type the spoken text instead.')
      return
    }
    if (active) {
      setActive(false)
      return
    }
    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'
    recognition.onstart = () => {
      setActive(true)
      setError('')
    }
    recognition.onresult = event => {
      const transcript = event.results[0][0].transcript
      setInput(current => current ? `${current} ${transcript}` : transcript)
    }
    recognition.onerror = event => {
      setError(`Speech recognition failed: ${event.error}. You can type the spoken text instead.`)
    }
    recognition.onend = () => setActive(false)
    recognition.start()
  }
  async function handleTranslate() {
    const values = voice ? input.trim() : input.split(',').map(sign => sign.trim()).filter(Boolean)
    if ((voice && !values) || (!voice && values.length === 0)) {
      setError(voice ? 'Enter text before translating.' : 'Enter signs separated by commas.')
      return
    }
    setLoading(true)
    setError('')
    setSaved(false)
    try {
      const translation = voice ? await translateVoiceToSign(values, language) : await translateSignToVoice(values, language)
      setResult(translation)
      const conversation = conversationId
        ? { id: conversationId }
        : await createConversation(voice ? 'Voice to Sign conversation' : 'Sign to Voice conversation', language)
      if (!conversationId) setConversationId(conversation.id)
      await addConversationMessage(conversation.id, 'user', voice ? values : values.join(', '))
      await addConversationMessage(conversation.id, 'assistant', voice ? translation.sign_sequence.join(' · ') : translation.generated_text)
      setSaved(true)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }
  return <div className="container page"><p className="eyebrow">{voice ? 'Voice to sign' : 'Sign to voice'}</p><h1>{voice ? 'Let your words be seen.' : 'A clearer way to be heard.'}</h1><p className="lead page-lead">{voice ? 'Speak or type text to preview the voice-to-sign backend contract.' : 'Enter recognized signs to preview the sign-to-voice backend contract.'}</p><Language value={language} onChange={setLanguage} /><div className="workspace"><section className="panel"><h2>{voice ? 'Spoken input' : 'Recognized signs'}</h2><p className="muted">{voice ? 'Use your browser microphone or type until speech capture is connected.' : 'Separate signs with commas until camera recognition is connected.'}</p><textarea className="input" value={input} onChange={event => setInput(event.target.value)} placeholder={voice ? 'Hello, how are you?' : 'HELLO, HOW, ARE, YOU'} rows="4" /><div className="button-row">{voice && <button className="button secondary" onClick={toggleRecording}>{active ? 'Stop recording' : 'Start recording'}</button>}<button className="button primary" disabled={loading} onClick={handleTranslate}>{loading ? 'Translating...' : 'Translate'}</button><button className="button secondary" onClick={() => { setInput(''); setResult(null); setError(''); setSaved(false) }}>Clear</button></div>{error && <p className="error" role="alert">{error}</p>}</section><div className="stack"><Placeholder title={voice ? `${language} sign output` : 'Generated voice'} icon={voice ? Info : Mic} text={result ? voice ? result.sign_sequence.join(' · ') : result.generated_text : voice ? 'Translation output will appear here.' : 'Generated transcript will appear here.'} /><Placeholder title="Conversation history" icon={MessageCircle} text={saved ? 'Translation saved to the current conversation.' : conversationId ? 'Ready to save the next translation.' : 'A conversation will be created after the first translation.'} /></div></div><div className="notice" role="status"><Info size={18} /> Browser speech recognition is available where supported. Real sign-language recognition and AI providers are not connected yet.</div></div>
}

function Placeholder({ title, icon: Icon, text }) { return <section className="panel"><h2><span className="mini-icon"><Icon size={18} /></span>{title}</h2><div className="placeholder">{text}</div></section> }
function VoiceToSign() { return <Workspace mode="voice" /> }
function SignToVoice() { return <Workspace mode="sign" /> }
function History() {
  const [conversations, setConversations] = useState([])
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function loadConversations() {
    setLoading(true)
    setError('')
    try {
      setConversations(await listConversations())
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  async function openConversation(id) {
    try {
      setSelected(await getConversation(id))
      setError('')
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  async function removeConversation(id) {
    try {
      await deleteConversation(id)
      setConversations(items => items.filter(item => item.id !== id))
      if (selected?.id === id) setSelected(null)
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  useEffect(() => { loadConversations() }, [])
  return <div className="container page"><p className="eyebrow">Conversation history</p><h1>Your conversations, kept clear.</h1><p className="lead page-lead">Reopen saved translation sessions or remove them from local history.</p>{error && <p className="error" role="alert">{error}</p>}{loading ? <div className="panel"><p className="muted">Loading conversations...</p></div> : conversations.length === 0 ? <div className="panel"><p className="muted">No conversations saved yet. Start a translation to create one.</p></div> : <div className="history-layout"><section className="history-list">{conversations.map(conversation => <article className="history-item" key={conversation.id}><button className="history-select" onClick={() => openConversation(conversation.id)}><strong>{conversation.title}</strong><small>{conversation.sign_language} · {conversation.message_count} messages</small></button><button className="delete-button" aria-label={`Delete ${conversation.title}`} onClick={() => removeConversation(conversation.id)}>Delete</button></article>)}</section>{selected && <section className="panel transcript"><h2>{selected.title}</h2><p className="muted">{selected.sign_language} · {selected.messages.length} messages</p>{selected.messages.map(message => <div className={`message ${message.role}`} key={message.id}><small>{message.role}</small><p>{message.content}</p></div>)}</section>}</div>}</div>
}
function About() { return <div className="container page"><p className="eyebrow">About SignBridge</p><h1>Technology that listens, watches, and makes room.</h1><p className="lead page-lead">SignBridge is an AI-powered communication concept for Deaf and Hard of Hearing people. We are starting with a thoughtful frontend foundation for spoken language to sign and sign language to voice.</p><div className="about-grid">{[['Accessible', 'Clear contrast, visible focus states, responsive layouts, and semantic controls are part of the foundation.'], ['Human-centered', 'The experience supports communication with dignity, choice, and clarity at every step.'], ['AI-ready', 'The separated frontend foundation leaves room for future capabilities to be added responsibly.']].map(([title, text]) => <article className="card" key={title}><h3>{title}</h3><p>{text}</p></article>)}</div><div className="about-note"><ShieldCheck /><div><h2>An honest Phase 1 foundation</h2><p>The current experience deliberately does not perform speech recognition, sign translation, gesture recognition, or voice generation. Each area is clearly marked as a demo placeholder.</p></div></div></div> }

export default Layout
