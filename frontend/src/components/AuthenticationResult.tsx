import type { AuthStatus } from '../types/auth.types'

interface Props {
  status: AuthStatus
  message?: string
  onRetry: () => void
}

export default function AuthenticationResult({
  status,
  message,
  onRetry,
}: Props) {
  const success = status === 'success'

  return (
    <section className="auth-result" role="status">
      <div className={success ? 'result-success' : 'result-error'}>
        {success ? '✓' : '!'}
      </div>

      <h2>
        {success
          ? 'Identidad autenticada'
          : status === 'expired'
            ? 'Solicitud expirada'
            : 'Autenticación no completada'}
      </h2>

      <p>
        {message ??
          (success
            ? 'RENIEC confirmó la autenticación.'
            : 'No fue posible completar la autenticación.')}
      </p>

      <button type="button" onClick={onRetry}>
        Nueva autenticación
      </button>
    </section>
  )
}