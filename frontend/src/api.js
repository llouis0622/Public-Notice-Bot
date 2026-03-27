async function request(method, path, body) {
  const options = { method, headers: { "Content-Type": "application/json" } }
  if (body !== undefined) options.body = JSON.stringify(body)
  const res = await fetch(path, options)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export const getPostings = (category, limit = 50) => {
  const params = new URLSearchParams()
  if (category) params.set("category", category)
  params.set("limit", limit)
  return request("GET", `/postings?${params}`)
}

export const postChat = (query) => request("POST", "/chat", { query })

export const postRecommend = (profile) => request("POST", "/recommend", profile)
