import { useEffect, useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import type { StartAuthResponse } from '../types/auth.types'

interface Props {
  transaction: StartAuthResponse
  onCancel: () => void
  onExpired: () => void
}

export default function AuthenticationQR({
  transaction,
  onCancel,
  onExpired,
}: Props) {
  const [remaining, setRemaining] = useState(transaction.expiresIn)

  useEffect(() => {
    const expiresAt = Date.now() + transaction.expiresIn * 1000

    const timer = window.setInterval(() => {
      const seconds = Math.max(
        0,
        Math.ceil((expiresAt - Date.now()) / 1000)
      )

      setRemaining(seconds)

      if (seconds === 0) {
        window.clearInterval(timer)
        onExpired()
      }
    }, 1000)

    return () => window.clearInterval(timer)
  }, [transaction, onExpired])

  const minutes = Math.floor(remaining / 60)
  const seconds = remaining % 60

  return (
    <section className="auth-qr">
      <h2>Verificación de identidad</h2>
      <p>Escanea el código utilizando la aplicación ID-Perú.</p>

      <div className="qr-container">
        <QRCodeSVG value={transaction.qr} size={220} />
      </div>

      <p className="qr-timer">
        Tiempo restante: {minutes}:{String(seconds).padStart(2, '0')}
      </p>

      <p className="qr-notice">
        Modo demostración. Este QR no es válido para RENIEC.
      </p>

      <button type="button" onClick={onCancel}>
        Cancelar
      </button>
    </section>
  )
}