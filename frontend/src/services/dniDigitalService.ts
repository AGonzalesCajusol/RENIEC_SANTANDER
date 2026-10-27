import { apiRequest } from './apiClient';
import type { DniDigitalInitResponse, DniDigitalStatusResponse } from '../types/dniDigital.types';

export const dniDigitalService = {
  async initVerification(purpose = 'ONBOARDING_DIGITAL'): Promise<DniDigitalInitResponse> {
    return apiRequest<DniDigitalInitResponse>('/api/dni-digital/init', {
      method: 'POST',
      body: JSON.stringify({ documentType: 'DNI', purpose }),
    });
  },

  async getStatus(requestId: string): Promise<DniDigitalStatusResponse> {
    return apiRequest<DniDigitalStatusResponse>(
      `/api/dni-digital/status/${encodeURIComponent(requestId)}`,
      { method: 'GET' }
    );
  },
};
