import { useAuthStatus } from '../hooks/useAuthStatus'
import { useCallback, useState } from 'react'
import AuthenticationQR from '../components/AuthenticationQR'
import AuthenticationResult from '../components/AuthenticationResult'
import { authService, mockAuthResult } from '../services/authService'
import type {
  AuthMethod,
  AuthStatus,
  StartAuthResponse,
} from '../types/auth.types'

type PageState = 'form' | 'loading' | 'qr' | 'result'

export default function AuthenticationPage() {
  const [dni, setDni] = useState('')
  const [method, setMethod] = useState<AuthMethod>('face_mobile')
  const [pageState, setPageState] = useState<PageState>('form')
  const [transaction, setTransaction] = useState<StartAuthResponse | null>(null)
  const [resultStatus, setResultStatus] = useState<AuthStatus>('pending')
  const [resultMessage, setResultMessage] = useState('')
  const [error, setError] = useState('')

  const { result: authStatus, error: statusError } = useAuthStatus({
    transactionId: transaction?.transactionId ?? null,
    enabled: pageState === 'qr',
    interval: transaction?.interval ?? 5,
  })



  const backendFinished =
    pageState === 'qr' &&
    authStatus !== null &&
    authStatus.status !== 'pending'

  const visibleState = backendFinished ? 'result' : pageState

  const reset = useCallback(() => {
    setPageState('form')
    setTransaction(null)
    setResultStatus('pending')
    setResultMessage('')
    setError('')
  }, [])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!/^\d{8}$/.test(dni)) {
      setError('El DNI debe contener exactamente 8 dígitos.')
      return
    }

    setError('')
    setPageState('loading')

    try {
      const response = await authService.startAuth({ dni, method })
      setTransaction(response)
      setPageState('qr')
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Error al iniciar autenticación.'
      )
      setPageState('form')
    }
  }

  const simulateResult = (status: 'success' | 'rejected') => {
    if (!transaction) return

    const result = mockAuthResult(transaction.transactionId, status)

    setResultStatus(result.status)
    setResultMessage(result.message ?? '')
    setPageState('result')
  }

  const handleExpired = useCallback(() => {
    setResultStatus('expired')
    setResultMessage('El tiempo disponible para autenticarse ha finalizado.')
    setPageState('result')
  }, [])

  return (
    <main className="auth-page">
      <section className="auth-card">
        <header className="auth-header">
          <span className="auth-label">SANTANDER · RENIEC</span>
          <h1>Validación de identidad</h1>
          <p>Prototipo de integración con ID-Perú.</p>
        </header>

        {pageState === 'form' && (
          <form onSubmit={handleSubmit} className="auth-form">
            <label htmlFor="dni">Número de DNI</label>
            <input
              id="dni"
              type="text"
              inputMode="numeric"
              maxLength={8}
              autoComplete="off"
              placeholder="Ingrese su DNI"
              value={dni}
              onChange={(event) => {
                setDni(event.target.value.replace(/\D/g, ''))
                setError('')
              }}
            />

            <label htmlFor="method">Método de autenticación</label>
            <select
              id="method"
              value={method}
              onChange={(event) =>
                setMethod(event.target.value as AuthMethod)
              }
            >
              <option value="face_mobile">Biometría facial</option>
              <option value="pki_dnie">DNI electrónico</option>
            </select>

            {error && <p className="auth-error" role="alert">{error}</p>}

            <button type="submit">Iniciar autenticación</button>
          </form>
        )}

        {pageState === 'loading' && (
          <p role="status">Iniciando autenticación...</p>
        )}

        {visibleState === 'qr' && transaction && (
          <>
            <AuthenticationQR
              transaction={transaction}
              onCancel={reset}
              onExpired={handleExpired}
            />

            {statusError && (
              <p className="auth-error" role="alert">
                Error consultando estado: {statusError}
              </p>
            )}

            <div className="mock-controls">
              <p>Controles de prueba (sin conexión a RENIEC)</p>

              <button
                type="button"
                onClick={() => simulateResult('success')}
              >
                Simular éxito
              </button>

              <button
                type="button"
                onClick={() => simulateResult('rejected')}
              >
                Simular rechazo
              </button>
            </div>
          </>
        )}

        {visibleState === 'result' && (
          <AuthenticationResult
            status={backendFinished ? authStatus.status : resultStatus}
            message={backendFinished ? authStatus.message : resultMessage}
            onRetry={reset}
          />
        )}

        <p className="auth-footer">
          Entorno de demostración · Sin conexión a RENIEC
        </p>
      </section>
    </main>
  )
}