const DEFAULT_API_BASE_URL = 'https://agridoctor-4kjr.onrender.com/api';
const configuredApiUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();
const isLocalApiUrl = configuredApiUrl.startsWith('http://localhost:')
	|| configuredApiUrl.startsWith('http://127.0.0.1:')
	|| configuredApiUrl.startsWith('https://localhost:');

export const API_BASE_URL = (import.meta.env.DEV && isLocalApiUrl ? configuredApiUrl : DEFAULT_API_BASE_URL).replace(/\/+$/, '');
