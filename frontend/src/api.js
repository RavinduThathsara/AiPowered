const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

async function request(path, options) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail || `Request failed (${response.status})`)
  }

  return response.status === 204 ? null : response.json()
}

export function translateVoiceToSign(text, signLanguage) {
  return request('/voice-to-sign', {
    method: 'POST',
    body: JSON.stringify({ text, sign_language: signLanguage }),
  })
}

export function translateSignToVoice(signSequence, signLanguage) {
  return request('/sign-to-voice', {
    method: 'POST',
    body: JSON.stringify({ sign_sequence: signSequence, sign_language: signLanguage }),
  })
}

export function createConversation(title, signLanguage) {
  return request('/conversations', {
    method: 'POST',
    body: JSON.stringify({ title, sign_language: signLanguage }),
  })
}

export function addConversationMessage(conversationId, role, content) {
  return request(`/conversations/${conversationId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ role, content }),
  })
}

export function listConversations() {
  return request('/conversations')
}

export function getConversation(conversationId) {
  return request(`/conversations/${conversationId}`)
}

export function deleteConversation(conversationId) {
  return request(`/conversations/${conversationId}`, { method: 'DELETE' })
}
