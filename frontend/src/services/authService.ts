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

    interface BackendStartResponse {
      message: string
      qr?: string | null
      auth_req_id?: string | null
      transactionId?: string
      expiresIn?: number
      interval?: number
    }

    const payload = {
      login_hint: request.dni,
      acr_values: request.method,
    }

    const response = await apiRequest<BackendStartResponse>('/api/auth/start', {
      method: 'POST',
      body: JSON.stringify(payload),
    })

    return {
      transactionId: response.auth_req_id || response.transactionId || crypto.randomUUID(),
      qr: response.qr || 'idperu://auth-iniciada',
      expiresIn: response.expiresIn || 600,
      interval: response.interval || 5,
    }
  },

  async getAuthStatus(
    transactionId: string,
    checkReniec: boolean = false
  ): Promise<AuthStatusResponse> {
    if (MOCK_MODE) {
      await delay(300)

      return {
        transactionId,
        status: 'pending',
        message: 'Esperando autenticación del ciudadano.',
      }
    }

    interface BackendStatusResponse {
      auth_req_id: string
      status: string
      message?: string
      transactionId?: string
    }

    const queryParam = checkReniec ? '?check_reniec=true' : ''
    const data = await apiRequest<BackendStatusResponse>(
      `/api/auth/${encodeURIComponent(transactionId)}/status${queryParam}`
    )

    // Normalizar estados del backend (PENDING, APPROVED, REJECTED, EXPIRED)
    // hacia los tipos esperados por el frontend (pending, success, rejected, expired)
    let mappedStatus: AuthStatusResponse['status'] = 'pending'
    const s = data.status.toUpperCase()
    if (s === 'APPROVED' || s === 'SUCCESS') {
      mappedStatus = 'success'
    } else if (s === 'REJECTED') {
      mappedStatus = 'rejected'
    } else if (s === 'EXPIRED') {
      mappedStatus = 'expired'
    } else if (s === 'PENDING') {
      mappedStatus = 'pending'
    } else {
      mappedStatus = 'error'
    }

    return {
      transactionId: data.transactionId || data.auth_req_id || transactionId,
      status: mappedStatus,
      message: data.message,
    }
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
