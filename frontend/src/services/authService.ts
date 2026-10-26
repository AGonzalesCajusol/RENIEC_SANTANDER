import { apiRequest } from './apiClient'
import type {
  StartAuthRequest,
  StartAuthResponse,
  AuthStatusResponse,
  AuthResultResponse,
} from '../types/auth.types'

const MOCK_MODE = import.meta.env.VITE_USE_MOCK !== 'false'

const delay = (ms: number) =>
  new Promise<void>((resolve) => setTimeout(resolve, ms))

export const authService = {
  async startAuth(
    request: StartAuthRequest
  ): Promise<StartAuthResponse> {
    if (!/^\d{8}$/.test(request.dni)) {
      throw new Error('El DNI debe contener exactamente 8 dígitos.')
    }

    if (MOCK_MODE) {
      await delay(500)

      return {
        transactionId: crypto.randomUUID(),
        qr: 'MOCK_QR_NO_VALIDO_PARA_RENIEC',
        expiresIn: 600,
        interval: 5,
      }
    }

    return apiRequest<StartAuthResponse>('/api/auth/start', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  async getAuthStatus(
    transactionId: string
  ): Promise<AuthStatusResponse> {
    if (MOCK_MODE) {
      await delay(300)

      return {
        transactionId,
        status: 'pending',
        message: 'Esperando autenticación del ciudadano.',
      }
    }

    return apiRequest<AuthStatusResponse>(
      `/api/auth/${encodeURIComponent(transactionId)}/status`
    )
  },

  async getAuthResult(
    transactionId: string
  ): Promise<AuthResultResponse> {
    if (MOCK_MODE) {
      await delay(300)

      return {
        transactionId,
        status: 'pending',
        message: 'La autenticación todavía no ha finalizado.',
      }
    }

    return apiRequest<AuthResultResponse>(
      `/api/auth/${encodeURIComponent(transactionId)}/result`
    )
  },
}

export const mockAuthResult = (
  transactionId: string,
  status: 'success' | 'rejected' | 'expired'
): AuthStatusResponse => ({
  transactionId,
  status,
  message:
    status === 'success'
      ? 'Autenticación de prueba completada.'
      : status === 'rejected'
        ? 'Autenticación de prueba rechazada.'
        : 'La solicitud de prueba ha expirado.',
})
