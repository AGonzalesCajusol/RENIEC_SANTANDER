import { useState } from 'react'
import AuthenticationPage from './pages/AuthenticationPage'
import { DniDigitalVerification } from './components/DniDigitalVerification'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState<'dni_digital' | 'ciba'>('dni_digital')

  return (
    <div>
      {/* Selector de flujo para pruebas */}
      <header style={{
        display: 'flex',
        justifyContent: 'center',
        gap: 12,
        padding: '12px 16px',
        backgroundColor: '#f8fafc',
        borderBottom: '1px solid #e2e8f0'
      }}>
        <button
          onClick={() => setActiveTab('dni_digital')}
          style={{
            padding: '8px 16px',
            borderRadius: 6,
            fontWeight: 600,
            fontSize: 13,
            cursor: 'pointer',
            border: activeTab === 'dni_digital' ? '2px solid #ec0000' : '1px solid #cbd5e1',
            backgroundColor: activeTab === 'dni_digital' ? '#fee2e2' : '#ffffff',
            color: activeTab === 'dni_digital' ? '#ec0000' : '#475569'
          }}
        >
          📱 Flujo DNI Digital (Perú Pass - 3 Pantallas)
        </button>
        <button
          onClick={() => setActiveTab('ciba')}
          style={{
            padding: '8px 16px',
            borderRadius: 6,
            fontWeight: 600,
            fontSize: 13,
            cursor: 'pointer',
            border: activeTab === 'ciba' ? '2px solid #ec0000' : '1px solid #cbd5e1',
            backgroundColor: activeTab === 'ciba' ? '#fee2e2' : '#ffffff',
            color: activeTab === 'ciba' ? '#ec0000' : '#475569'
          }}
        >
          🔑 Flujo ID-Perú CIBA
        </button>
      </header>

      {activeTab === 'dni_digital' ? <DniDigitalVerification /> : <AuthenticationPage />}
    </div>
  )
}

export default App