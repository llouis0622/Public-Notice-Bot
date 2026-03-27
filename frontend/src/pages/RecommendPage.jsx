import { useState } from "react"
import { postRecommend } from "../api"

const CATEGORY_OPTIONS = ["일자리", "창업", "교육", "복지", "문화", "주거"]

export default function RecommendPage() {
  const [age, setAge] = useState("")
  const [region, setRegion] = useState("")
  const [categories, setCategories] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const toggleCategory = (c) => {
    setCategories((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    )
  }

  const submit = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await postRecommend({
        age: age ? Number(age) : null,
        region: region || null,
        categories,
      })
      setResults(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h2>맞춤 추천</h2>
      <div className="profile-form">
        <label>
          나이
          <input
            type="number"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            placeholder="예: 25"
            min={1}
            max={100}
          />
        </label>
        <label>
          지역
          <input
            type="text"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            placeholder="예: 부산 해운대구"
          />
        </label>
        <div className="category-select">
          <span>관심 분야</span>
          <div className="tag-group">
            {CATEGORY_OPTIONS.map((c) => (
              <button
                key={c}
                className={categories.includes(c) ? "active" : ""}
                onClick={() => toggleCategory(c)}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
        <button className="submit-btn" onClick={submit} disabled={loading}>
          {loading ? "분석 중..." : "추천받기"}
        </button>
      </div>

      {error && <p className="status error">{error}</p>}

      {results !== null && (
        <ul className="postings-list">
          {results.length === 0 && <p className="status">조건에 맞는 공고가 없습니다.</p>}
          {results.map((p) => (
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
      )}
    </div>
  )
}
