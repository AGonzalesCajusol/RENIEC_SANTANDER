import { useEffect, useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import type { StartAuthResponse } from '../types/auth.types'

interface Props {
  transaction: StartAuthResponse
  onCancel: () => void
  onExpired: () => void
  onConfirmManual?: () => void
}

export default function AuthenticationQR({
  transaction,
  onCancel,
  onExpired,
  onConfirmManual,
}: Props) {
  const [remaining, setRemaining] = useState(transaction.expiresIn)
  const [copied, setCopied] = useState(false)

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

  // Construcción de enlaces según especificación técnica ID-Perú Sección 8.2.1
  const qrRaw = transaction.qr || ''
  const qrEncoded = encodeURIComponent(qrRaw)

  // Enlace Web-to-App Android (Sección 8.2.1.3 - Código fuente 14)
  const androidIntentUrl = `intent://idaas.reniec.com/auth/#Intent;scheme=reniec;package=pe.gob.reniec.pki.reniecidaas2;S.name=ID%20Per%C3%BA;S.data=${qrRaw};end`

  // Enlace Web-to-App iOS (Sección 8.2.1.4 - Código fuente 15)
  const iosSchemeUrl = `reniecidaas://auth?data=${qrEncoded}`

  // Enlace Cliente Windows ID-Perú DNIe (Sección 8.2.1.2)
  const windowsClienteUrl = `idaas2://launch?data=${qrRaw}`

  const copyPayload = () => {
    navigator.clipboard.writeText(qrRaw)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section className="auth-qr">
      <h2>Verificación de identidad ID-Perú</h2>
      <p>Escanea el código QR desde la aplicación oficial ID-Perú en tu móvil.</p>

      {/* Imagen QR para Desktop (Sección 8.2.1.1 - Tamaño >= 220px) */}
      <div className="qr-container" style={{ margin: '1rem 0' }}>
        <QRCodeSVG value={qrRaw} size={240} level="M" />
      </div>

      <p className="qr-timer" style={{ fontWeight: 'bold' }}>
        Tiempo restante: {minutes}:{String(seconds).padStart(2, '0')}
      </p>

      {/* Enlaces de invocación directa según dispositivo (Sección 8.2.1) */}
      <div className="platform-links" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', margin: '1rem 0' }}>
        <a
          href={androidIntentUrl}
          className="btn-platform"
          style={{ padding: '0.5rem', background: '#e32626', color: '#fff', borderRadius: '4px', textDecoration: 'none', textAlign: 'center', fontSize: '0.85rem' }}
        >
          📱 Abrir en ID-Perú (Android)
        </a>

        <a
          href={iosSchemeUrl}
          className="btn-platform"
          style={{ padding: '0.5rem', background: '#0066cc', color: '#fff', borderRadius: '4px', textDecoration: 'none', textAlign: 'center', fontSize: '0.85rem' }}
        >
          🍏 Abrir en ID-Perú (iOS)
        </a>

        <a
          href={windowsClienteUrl}
          className="btn-platform"
          style={{ padding: '0.5rem', background: '#2c3e50', color: '#fff', borderRadius: '4px', textDecoration: 'none', textAlign: 'center', fontSize: '0.85rem' }}
        >
          💻 Abrir con Cliente ID-Perú (Windows DNIe)
        </a>
      </div>

      {/* Acción explícita del usuario como respaldo (Sección 8.1.5 - Documentación) */}
      {onConfirmManual && (
        <button
          type="button"
          onClick={onConfirmManual}
          style={{ margin: '0.5rem 0', background: '#28a745', color: '#fff' }}
        >
          ✓ Ya me autentiqué en mi celular
        </button>
      )}

      <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: '#666', wordBreak: 'break-all' }}>
        <strong>Código de sesión:</strong> <code>{qrRaw.substring(0, 32)}...</code>{' '}
        <button type="button" onClick={copyPayload} style={{ padding: '2px 6px', fontSize: '0.75rem', marginLeft: '5px' }}>
          {copied ? '¡Copiado!' : 'Copiar'}
        </button>
      </div>

      <div style={{ marginTop: '1rem' }}>
        <button type="button" onClick={onCancel} style={{ background: '#eee', color: '#333' }}>
          Cancelar
        </button>
      </div>
    </section>
  )
}
