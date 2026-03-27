import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom"
import PostingsPage from "./pages/PostingsPage"
import ChatPage from "./pages/ChatPage"
import RecommendPage from "./pages/RecommendPage"
import "./index.css"

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <span className="nav-brand">부산 공고 봇</span>
          <div className="nav-links">
            <NavLink to="/" end>공고</NavLink>
            <NavLink to="/chat">챗봇</NavLink>
            <NavLink to="/recommend">추천</NavLink>
          </div>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<PostingsPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/recommend" element={<RecommendPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
