import { useState, useRef, useEffect } from "react"
import { postChat } from "../api"

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const send = async () => {
    const query = input.trim()
    if (!query || loading) return
    setInput("")
    setMessages((prev) => [...prev, { role: "user", text: query }])
    setLoading(true)
    try {
      const { answer } = await postChat(query)
      setMessages((prev) => [...prev, { role: "bot", text: answer }])
    } catch (e) {
      setMessages((prev) => [...prev, { role: "bot", text: `오류: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="page chat-page">
      <h2>챗봇</h2>
      <div className="chat-window">
        {messages.length === 0 && (
          <p className="status">공고·제도에 대해 무엇이든 물어보세요.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="bubble bot typing">...</div>}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-bar">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="질문 입력 (Enter로 전송)"
          rows={2}
        />
        <button onClick={send} disabled={loading || !input.trim()}>
          전송
        </button>
      </div>
    </div>
  )
}
