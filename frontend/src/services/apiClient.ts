const API_URL = (
  import.meta.env.VITE_API_URL || 'http://localhost:3000'
).replace(/\/+$/, '')

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    let message = `Error HTTP ${response.status}`

    try {
      const data: any = await response.json()

      if (typeof data === 'object' && data !== null) {
        // FastAPI suele responder con 'detail' en HTTPException y validaciones
        if (typeof data.detail === 'string') {
          message = data.detail
        } else if (Array.isArray(data.detail) && data.detail.length > 0) {
          // Errores de validación Pydantic (lista de errores)
          message = data.detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ')
        } else if (typeof data.mensaje === 'string') {
          message = data.mensaje
        } else if (typeof data.message === 'string') {
          message = data.message
        } else if (typeof data.error_description === 'string') {
          message = data.error_description
        } else if (typeof data.error === 'string') {
          message = data.error
        }
      }
    } catch {
      // Si no es JSON, intentar leer texto plano
      try {
        const text = await response.text()
        if (text && text.trim().length > 0) {
          message = text
        }
      } catch {
        // Mantener mensaje HTTP predeterminado
      }
    }

    throw new Error(message)
  }

  return (await response.json()) as T
}
