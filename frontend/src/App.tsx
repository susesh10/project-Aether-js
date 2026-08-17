import { useState, useRef, type ChangeEvent, type KeyboardEvent} from "react"

function App() {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)
  const [message, setMessage] = useState("")
  const [chat, setChat] = useState<{ role: string; content: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleInput = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)

    // Auto-grow
    e.target.style.height = "auto"
    e.target.style.height = `${e.target.scrollHeight}px`
  }

  const sendMessage = async () => {
   if (isLoading) return
   if (message.trim() === "") return
 
   const currentMessage = message   // 1. save first
 
   // 2. clear input + reset height
   setMessage("")
   if (textareaRef.current) {
     textareaRef.current.style.height = "auto"
   }
 
   // 3. show user message
   setChat(prev => [...prev, { role: "user", content: currentMessage }])
   setIsLoading(true)
 
   try {
     const response = await fetch("http://localhost:8000/chat", {
       method: "POST",
       headers: {
         "Content-Type": "application/json"
       },
       body: JSON.stringify({ message: currentMessage })
     })
 
     const data = await response.json()
     setChat(prev => [...prev, { role: "assistant", content: data.reply }])
   } catch (error) {
     console.error("Error sending message:", error)
     setChat(prev => [
       ...prev,
       { role: "assistant", content: "Sorry, something went wrong." }
     ])
   }
 
   setIsLoading(false)
 }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const resetChat = async () => {
    setChat([])
    await fetch("http://localhost:8000/clear-history", {
      method: "POST"
    })
  }

  return (
    <div className="app">
      {/* Left Sidebar */}
      <div className="sidebar">
        <button className="sidebar-btn" title="Akari">
          A
        </button>

        <button
          className="sidebar-btn"
          title="Reset chat"
          onClick={resetChat}
        >
          B
        </button>

        <button className="sidebar-btn" title="Chat history">
          C
        </button>
      </div>

      {/* Main Area */}
      <div className="main">
        {chat.map((msg, index) => (
          <p key={index} className={msg.role}>
            {msg.content}
          </p>
        ))}

        {isLoading && <p className="assistant">Akari is thinking...</p>}
      </div>

      {/* Input Area */}
      <div className="input-bar">
        <textarea
          ref = {textareaRef}
          value={message}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Talk to Akari..."
          rows={1}
        />

        <div className="input-actions">
          <button className="voice-btn" title="Voice input">
            🎤
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