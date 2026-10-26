export type AuthMethod = 'face_mobile' | 'pki_dnie'

export type AuthStatus =
  | 'pending'
  | 'success'
  | 'rejected'
  | 'expired'
  | 'error'

export interface StartAuthRequest {
  dni: string
  method: AuthMethod
}

export interface StartAuthResponse {
  transactionId: string
  qr: string
  expiresIn: number
  interval: number
}

export interface AuthStatusResponse {
  transactionId: string
  status: AuthStatus
  message?: string
}

export interface AuthResultResponse {
  transactionId: string
  status: AuthStatus
  documentNumber?: string
  authenticatedAt?: string
  message?: string
}