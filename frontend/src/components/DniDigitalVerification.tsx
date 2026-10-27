import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { dniDigitalService } from '../services/dniDigitalService';
import type { DniDigitalInitResponse, DniDigitalStatusResponse } from '../types/dniDigital.types';

export const DniDigitalVerification: React.FC = () => {
  // Estados de pantalla: 1 = Solicitud, 2 = QR / Espera, 3 = Éxito
  const [screen, setScreen] = useState<'screen1' | 'screen2' | 'screen3'>('screen1');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [verifyData, setVerifyData] = useState<DniDigitalInitResponse | null>(null);
  const [verifiedResult, setVerifiedResult] = useState<DniDigitalStatusResponse['verifiedData'] | null>(null);
  const [countdown, setCountdown] = useState<number>(120);

  // Iniciar flujo (Pantalla 1 -> Pantalla 2)
  const handleStart = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await dniDigitalService.initVerification();
      setVerifyData(data);
      setCountdown(120);
      setScreen('screen2');
    } catch (err: any) {
      setError(err.message || 'Error al conectar con el servidor.');
    } finally {
      setIsLoading(false);
    }
  };

  // Reintentar o reiniciar al estado 1
  const handleReset = () => {
    setScreen('screen1');
    setVerifyData(null);
    setVerifiedResult(null);
    setError(null);
  };

  // Temporizador para la Pantalla 2
  useEffect(() => {
    if (screen !== 'screen2') return;

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setError('El código QR ha expirado. Por favor, genera uno nuevo.');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [screen]);

  // Polling de estado en segundo plano (Pantalla 2 -> Pantalla 3)
  useEffect(() => {
    if (screen !== 'screen2' || !verifyData?.requestId) return;

    let isSubscribed = true;

    const pollStatus = async () => {
      try {
        const res = await dniDigitalService.getStatus(verifyData.requestId);
        if (!isSubscribed) return;

        if (res.status === 'COMPLETED') {
          setVerifiedResult(res.verifiedData);
          setScreen('screen3');
        } else if (res.status === 'EXPIRED') {
          setError('La sesión ha expirado en el servicio de verificación.');
        } else if (res.status === 'REJECTED') {
          setError('La solicitud fue cancelada o rechazada en la aplicación Perú Pass.');
        }
      } catch (e: any) {
        console.warn('Polling error:', e.message);
      }
    };

    // Primera ejecución inmediata
    pollStatus();

    // Consulta recurrente cada 2.5 segundos
    const pollInterval = setInterval(pollStatus, 2500);

    return () => {
      isSubscribed = false;
      clearInterval(pollInterval);
    };
  }, [screen, verifyData?.requestId]);

  const formatCountdown = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div style={styles.container}>
      {/* ============================================================== */}
      {/* PANTALLA 1: SOLICITUD DE VERIFICACIÓN */}
      {/* ============================================================== */}
      {screen === 'screen1' && (
        <div style={styles.card}>
          <div style={styles.badge}>RENIEC • DNI Digital</div>
          <h2 style={styles.title}>Verificación de Identidad</h2>
          <p style={styles.description}>
            Para continuar de forma segura con tu trámite en <strong>Banco Santander</strong>, confirma tu
            identidad utilizando tu credencial digital almacenada en <strong>Perú Pass</strong>.
          </p>

          {error && <div style={styles.errorBox}>{error}</div>}

          <button
            style={styles.primaryButton}
            onClick={handleStart}
            disabled={isLoading}
          >
            {isLoading ? 'Conectando con Verify...' : 'Iniciar con DNI Digital'}
          </button>
        </div>
      )}

      {/* ============================================================== */}
      {/* PANTALLA 2: CÓDIGO QR / PERÚ PASS */}
      {/* ============================================================== */}
      {screen === 'screen2' && verifyData && (
        <div style={styles.card}>
          <div style={styles.badge}>Paso 2 • Escanea con tu App</div>
          <h2 style={styles.title}>Abre tu aplicación Perú Pass</h2>
          <p style={styles.subtitle}>
            Apunta la cámara de Perú Pass a este código QR y confirma los datos que deseas compartir.
          </p>

          <div style={styles.qrWrapper}>
            <QRCodeSVG value={verifyData.qrData} size={230} level="M" />
          </div>

          <div style={styles.timer}>
            ⏱️ Código válido por: <strong>{formatCountdown(countdown)}</strong>
          </div>

          {/* Enlace para abrir directamente si el usuario está en el celular */}
          <a
            href={verifyData.qrData}
            style={styles.deeplinkButton}
          >
            📱 Abrir directamente en Perú Pass
          </a>

          {error && (
            <div style={{ ...styles.errorBox, marginTop: 16 }}>
              {error}
              <div style={{ marginTop: 8 }}>
                <button style={styles.secondaryButton} onClick={handleReset}>
                  Generar nuevo código
                </button>
              </div>
            </div>
          )}

          <div style={styles.pollingNotice}>
            <span style={styles.spinner}></span>
            Esperando confirmación desde tu teléfono...
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* PANTALLA 3: CONFIRMACIÓN Y ÉXITO */}
      {/* ============================================================== */}
      {screen === 'screen3' && (
        <div style={styles.card}>
          <div style={styles.successIcon}>✓</div>
          <h2 style={styles.title}>¡Identidad Verificada!</h2>
          <p style={styles.description}>
            La autenticación con <strong>RENIEC Perú Pass</strong> se completó con éxito total.
          </p>

          <div style={styles.dataCard}>
            <div style={styles.dataRow}>
              <span style={styles.dataLabel}>DNI:</span>
              <span style={styles.dataValue}>{verifiedResult?.CUI_DNI || 'Verificado'}</span>
            </div>
            <div style={styles.dataRow}>
              <span style={styles.dataLabel}>Titular:</span>
              <span style={styles.dataValue}>
                {verifiedResult?.PRENOMBRES} {verifiedResult?.PRIMER_APELLIDO} {verifiedResult?.SEGUNDO_APELLIDO || ''}
              </span>
            </div>
            <div style={styles.dataRow}>
              <span style={styles.dataLabel}>Canal:</span>
              <span style={styles.dataValue}>OpenID4VP (Perú Pass)</span>
            </div>
          </div>

          <button style={styles.primaryButton} onClick={handleReset}>
            Continuar con el trámite bancario
          </button>
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '80vh',
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
    padding: 16,
  },
  card: {
    background: '#ffffff',
    borderRadius: 16,
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.03)',
    padding: '36px 32px',
    maxWidth: 460,
    width: '100%',
    textAlign: 'center',
    border: '1px solid #f0f0f0',
  },
  badge: {
    display: 'inline-block',
    background: '#fee2e2',
    color: '#dc2626',
    fontWeight: 600,
    fontSize: 12,
    padding: '4px 12px',
    borderRadius: 9999,
    marginBottom: 16,
    letterSpacing: '0.025em',
  },
  title: {
    fontSize: 22,
    fontWeight: 700,
    color: '#1f2937',
    margin: '0 0 8px 0',
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 20,
    lineHeight: 1.5,
  },
  description: {
    fontSize: 14,
    color: '#4b5563',
    lineHeight: 1.6,
    marginBottom: 24,
  },
  primaryButton: {
    backgroundColor: '#ec0000', // Rojo Santander
    color: '#ffffff',
    border: 'none',
    borderRadius: 8,
    padding: '12px 24px',
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    width: '100%',
    transition: 'background-color 0.2s',
  },
  secondaryButton: {
    backgroundColor: '#f3f4f6',
    color: '#374151',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    padding: '8px 16px',
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer',
  },
  deeplinkButton: {
    display: 'block',
    marginTop: 12,
    padding: '10px 16px',
    backgroundColor: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: 8,
    color: '#2563eb',
    fontWeight: 500,
    fontSize: 13,
    textDecoration: 'none',
  },
  qrWrapper: {
    display: 'inline-block',
    padding: 16,
    background: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: 12,
    marginBottom: 16,
  },
  timer: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 8,
  },
  pollingNotice: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 20,
    fontSize: 12,
    color: '#9ca3af',
  },
  spinner: {
    width: 14,
    height: 14,
    border: '2px solid #e5e7eb',
    borderTopColor: '#ec0000',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    display: 'inline-block',
  },
  errorBox: {
    background: '#fef2f2',
    border: '1px solid #fecaca',
    color: '#991b1b',
    padding: '10px 14px',
    borderRadius: 8,
    fontSize: 13,
    marginBottom: 16,
    textAlign: 'left',
  },
  successIcon: {
    width: 64,
    height: 64,
    borderRadius: '50%',
    backgroundColor: '#dcfce7',
    color: '#15803d',
    fontSize: 32,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 16px auto',
    fontWeight: 700,
  },
  dataCard: {
    background: '#f9fafb',
    borderRadius: 10,
    padding: '14px 18px',
    textAlign: 'left',
    marginBottom: 24,
    border: '1px solid #e5e7eb',
  },
  dataRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '6px 0',
    fontSize: 13,
    borderBottom: '1px solid #f3f4f6',
  },
  dataLabel: {
    color: '#6b7280',
    fontWeight: 500,
  },
  dataValue: {
    color: '#111827',
    fontWeight: 600,
  },
};
