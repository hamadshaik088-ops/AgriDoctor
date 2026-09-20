const LOCAL_API_BASE_URL = 'http://localhost:5001/api';
const PRODUCTION_API_BASE_URL = 'https://agridoctor-4kjr.onrender.com/api';
const configuredApiUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();

export const API_BASE_URL = (configuredApiUrl || (import.meta.env.DEV ? LOCAL_API_BASE_URL : PRODUCTION_API_BASE_URL)).replace(/\/+$/, '');
