const LOCAL_API_BASE_URL = 'http://localhost:5001/api';
const PRODUCTION_API_BASE_URL = 'https://agridoctor-4kjr.onrender.com/api';
const configuredApiUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();
const isLocalApiUrl = configuredApiUrl.startsWith('http://localhost:')
	|| configuredApiUrl.startsWith('http://127.0.0.1:')
	|| configuredApiUrl.startsWith('https://localhost:');

const apiBaseUrl = import.meta.env.DEV
	? (configuredApiUrl || LOCAL_API_BASE_URL)
	: (configuredApiUrl && !isLocalApiUrl ? configuredApiUrl : PRODUCTION_API_BASE_URL);

export const API_BASE_URL = apiBaseUrl.replace(/\/+$/, '');
