import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL, // 환경변수에서 가져오기
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
