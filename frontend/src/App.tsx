import { useState, useRef, type ChangeEvent, type KeyboardEvent } from "react"

function App() {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)
  const [message, setMessage] = useState("")
  const [chat, setChat] = useState<{ role: string; content: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [currentReply, setCurrentReply] = useState("")

  const handleInput = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
    e.target.style.height = "auto"
    e.target.style.height = `${e.target.scrollHeight}px`
  }

  const playBackendSpeech = async (text: string) => {
    if (!text.trim()) return

    try {
      const response = await fetch("http://localhost:8000/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      })

      if (!response.ok) {
        console.error("Speech request failed")
        return
      }

      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)

      setIsSpeaking(true)

      await new Promise<void>((resolve) => {
        audio.onended = () => {
          setIsSpeaking(false)
          URL.revokeObjectURL(audioUrl)
          resolve()
        }
        audio.onerror = () => {
          setIsSpeaking(false)
          URL.revokeObjectURL(audioUrl)
          resolve()
        }
        audio.play().catch(() => {
          setIsSpeaking(false)
          URL.revokeObjectURL(audioUrl)
          resolve()
        })
      })
    } catch (error) {
      console.error("Speech playback error:", error)
      setIsSpeaking(false)
    }
  }

  const sendMessage = async () => {
    if (isLoading) return
    if (message.trim() === "") return

    const currentMessage = message
    setMessage("")
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }

    setChat((prev) => [...prev, { role: "user", content: currentMessage }])
    setIsLoading(true)
    setCurrentReply("")

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: currentMessage }),
      })

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.status}`)
      }

      const data = await response.json()
      const reply = data.reply || "..."

      setChat((prev) => [...prev, { role: "assistant", content: reply }])
      setCurrentReply(reply)
      setIsLoading(false)
      await playBackendSpeech(reply)
    } catch (error) {
      console.error("Error sending message:", error)
      const fallback = "Sorry, something went wrong."
      setChat((prev) => [...prev, { role: "assistant", content: fallback }])
      setCurrentReply(fallback)
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startListening = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Try Chrome.")
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = "en-US"
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onerror = () => setIsListening(false)

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      setMessage(transcript)
    }

    recognition.start()
  }

  const resetChat = async () => {
    setChat([])
    setCurrentReply("")
    setHistoryOpen(false)
    await fetch("http://localhost:8000/clear-history", { method: "POST" })
  }

  return (
    <div className="app">
      {/* Icon rail */}
      <div className="sidebar">
        <button className="sidebar-btn" title="Akari">
          A
        </button>

        <button className="sidebar-btn" title="Reset chat" onClick={resetChat}>
          B
        </button>

        <button
          className={`sidebar-btn ${historyOpen ? "active" : ""}`}
          title="Chat history"
          onClick={() => setHistoryOpen((v) => !v)}
        >
          C
        </button>
      </div>

      {/* History side panel */}
      {historyOpen && (
        <div className="history-panel">
          <div className="history-header">
            <span>Chat history</span>
            <button
              className="history-close"
              onClick={() => setHistoryOpen(false)}
              title="Close"
            >
              ✕
            </button>
          </div>

          <div className="history-list">
            {chat.length === 0 && (
              <p className="history-empty">No messages yet.</p>
            )}
            {chat.map((msg, index) => (
              <div key={index} className={`history-msg ${msg.role}`}>
                <span className="history-role">
                  {msg.role === "user" ? "You" : "Akari"}
                </span>
                <p>{msg.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main stage */}
      <div className="main-stage">
        <div className="stage-center">
          <div
            className={`voice-orb ${isSpeaking ? "speaking" : ""} ${
              isLoading && !isSpeaking ? "thinking" : ""
            }`}
          >
            <div className="wave-ring" aria-hidden="true">
              {Array.from({ length: 24 }).map((_, i) => (
                <span
                  key={i}
                  className="wave-bar"
                  style={{ ["--i" as string]: i }}
                />
              ))}
            </div>
            <div className="orb-core" />
          </div>

          <div className="current-line">
            {isLoading && (
              <p className="line-text muted">Akari is thinking...</p>
            )}
            {!isLoading && currentReply && (
              <p className="line-text">{currentReply}</p>
            )}
            {!isLoading && !currentReply && (
              <p className="line-text muted">Talk to Akari...</p>
            )}
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="input-bar">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Talk to Akari..."
          rows={1}
        />

        <div className="input-actions">
          <button
            className="voice-btn"
            title={isListening ? "Listening..." : "Voice input"}
            onClick={startListening}
            disabled={isLoading || isListening}
          >
            {isListening ? "⏺" : "🎤"}
          </button>
          <button
            className="send-btn"
            title="Send message"
            onClick={sendMessage}
            disabled={isLoading}
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  )
}

export default App