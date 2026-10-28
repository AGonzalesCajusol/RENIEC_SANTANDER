import { useEffect, useState } from 'react'
import { authService } from '../services/authService'
import type { AuthStatusResponse } from '../types/auth.types'

interface Options {
  transactionId: string | null
  enabled: boolean
  interval: number
}

export function useAuthStatus({
  transactionId,
  enabled,
  interval,
}: Options) {
  const [result, setResult] = useState<AuthStatusResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Limpiar el resultado previo cada vez que cambie o se limpie el transactionId
  useEffect(() => {
    setResult(null)
    setError(null)
  }, [transactionId])

  useEffect(() => {
    if (!enabled || !transactionId) return

    let active = true
    let timer: ReturnType<typeof setTimeout> | undefined

    const checkStatus = async () => {
      try {
        const response = await authService.getAuthStatus(transactionId)

        if (!active) return

        setResult(response)
        setError(null)

        if (response.status === 'pending') {
          timer = setTimeout(checkStatus, Math.max(interval, 5) * 1000)
        }
      } catch (err) {
        if (!active) return

        setError(
          err instanceof Error
            ? err.message
            : 'No se pudo consultar el estado.'
        )

        timer = setTimeout(checkStatus, Math.max(interval, 5) * 1000)
      }
    }

    // Evitamos consultar inmediatamente tras generar el QR.
    timer = setTimeout(checkStatus, Math.max(interval, 5) * 1000)

    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [transactionId, enabled, interval])

  return { result, error }
}
