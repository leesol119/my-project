import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080', // 기본값 설정
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
