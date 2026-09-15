const DEFAULT_API_BASE_URL = 'https://agridoctor-4kjr.onrender.com/api';
const configuredApiUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();

export const API_BASE_URL = (configuredApiUrl || DEFAULT_API_BASE_URL).replace(/\/+$/, '');
