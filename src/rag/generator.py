SYSTEM_PROMPT = (
    "당신은 부산 지역 공고·제도 정보를 안내하는 챗봇입니다. "
    "아래 참고 자료를 바탕으로 사용자 질문에 정확하고 간결하게 답하세요. "
    "참고 자료에 없는 내용은 모른다고 답하세요."
)


class Generator:
    model = "gpt-4o-mini"

    def __init__(self, client):
        self.client = client

    def generate(self, query, chunks):
        context = self._build_context(chunks)
        user_message = f"[참고 자료]\n{context}\n\n[질문]\n{query}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content

    def _build_context(self, chunks):
        if not chunks:
            return "(관련 자료 없음)"
        parts = []
        for i, chunk in enumerate(chunks, 1):
            chunk_type = chunk.get("chunk_type", "기타")
            content = chunk.get("content", "")
            parts.append(f"{i}. [{chunk_type}] {content}")
        return "\n".join(parts)
