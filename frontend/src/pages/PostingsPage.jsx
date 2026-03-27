import { useState, useEffect } from "react"
import { getPostings } from "../api"

const CATEGORIES = ["", "일자리", "창업", "교육", "복지", "문화", "주거"]

export default function PostingsPage() {
  const [postings, setPostings] = useState([])
  const [category, setCategory] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getPostings(category || null)
      .then(setPostings)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [category])

  return (
    <div className="page">
      <h2>공고 목록</h2>
      <div className="filter-bar">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            className={category === c ? "active" : ""}
            onClick={() => setCategory(c)}
          >
            {c || "전체"}
          </button>
        ))}
      </div>
      {loading && <p className="status">불러오는 중...</p>}
      {error && <p className="status error">{error}</p>}
      {!loading && !error && postings.length === 0 && (
        <p className="status">공고가 없습니다.</p>
      )}
      <ul className="postings-list">
        {postings.map((p) => (
          <li key={p.id} className="posting-card">
            <a href={p.url} target="_blank" rel="noreferrer">
              <strong>{p.title}</strong>
            </a>
            <div className="meta">
              <span className="tag">{p.category}</span>
              <span className="source">{p.source}</span>
              {p.deadline_at && (
                <span className="deadline">마감: {p.deadline_at.slice(0, 10)}</span>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
