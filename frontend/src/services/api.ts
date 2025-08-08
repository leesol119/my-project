import axios from 'axios';

// Railway에 배포된 gateway 서비스 URL을 기본값으로 설정
const RAILWAY_GATEWAY_URL = 'https://eripotter-gateway-production.up.railway.app';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || RAILWAY_GATEWAY_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,  // CORS credentials 비활성화
});

// 요청 인터셉터 추가 (로깅용)
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API 요청:', config.method?.toUpperCase(), config.url, config.data);
    console.log('📍 API Base URL:', config.baseURL);
    console.log('🌐 Full URL:', (config.baseURL || '') + (config.url || ''));
    return config;
  },
  (error) => {
    console.error('❌ API 요청 오류:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 추가 (로깅용)
api.interceptors.response.use(
  (response) => {
    console.log('✅ API 응답:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API 응답 오류:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export default api;
