import axios from 'axios';

// Railway에 배포된 gateway 서비스 URL
const RAILWAY_GATEWAY_URL = process.env.NEXT_PUBLIC_RAILWAY_GATEWAY_URL || 'https://my-project-production-0a50.up.railway.app';

// 환경변수가 설정되지 않았을 때 경고
if (!process.env.NEXT_PUBLIC_RAILWAY_GATEWAY_URL) {
  console.warn('⚠️ NEXT_PUBLIC_RAILWAY_GATEWAY_URL 환경변수가 설정되지 않았습니다!');
  console.warn('Vercel 대시보드에서 환경변수를 설정해주세요.');
}

const api = axios.create({
  baseURL: RAILWAY_GATEWAY_URL,
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
