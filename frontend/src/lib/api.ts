import axios from 'axios';

// Use the local backend URL for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

console.log(`API Base URL set to: ${API_BASE_URL}`);

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased timeout to 30 seconds to allow for AI processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('better-auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle responses globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error); // Log all API errors for debugging

    // Handle specific error cases
    if (error.response?.status === 401) {
      console.warn('Authentication failed - clearing token and redirecting to login');
      // Redirect to login or clear auth state
      localStorage.removeItem('better-auth-token');
      localStorage.removeItem('better-auth-user');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      console.warn('Forbidden access - clearing token and redirecting to login');
      localStorage.removeItem('better-auth-token');
      localStorage.removeItem('better-auth-user');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export default api;