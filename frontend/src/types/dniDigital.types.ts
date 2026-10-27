export interface DniDigitalInitResponse {
  requestId: string;
  transactionId: string;
  qrData: string;
  expiresAt: number | null;
}

export interface DniDigitalStatusResponse {
  status: 'PENDING' | 'COMPLETED' | 'EXPIRED' | 'REJECTED' | 'ERROR';
  verifiedData?: {
    CUI_DNI?: string;
    PRENOMBRES?: string;
    PRIMER_APELLIDO?: string;
    SEGUNDO_APELLIDO?: string;
    [key: string]: any;
  };
  message?: string;
}
