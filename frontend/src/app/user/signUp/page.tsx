'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

export default function SignUpPage() {
  const router = useRouter();

  // Form state management
  const [userData, setUserData] = useState({
    user_id: '',
    user_pw: '',
    company_id: ''
  });

  // Form input handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUserData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Sign up form submission
  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // JSON 형태로 alert 창에 표시
    const signUpData = {
      user_id: userData.user_id,
      user_pw: parseInt(userData.user_pw), // bigint로 변환
      company_id: userData.company_id || null // null 허용
    };
    
    alert(JSON.stringify(signUpData, null, 2));

    try {
      console.log('🚀 Railway Gateway로 회원가입 시도:', signUpData);
      
      // 직접 axios를 사용하여 Railway gateway로 요청
      const response = await axios.post('https://my-project-production-0a50.up.railway.app/signup', signUpData, {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: false,
      });
      
      console.log('✅ Railway Gateway 회원가입 응답:', response.data);
      alert('회원가입 성공! 로그인 페이지로 이동합니다.');
      
      // 로그인 페이지로 이동
      router.push('/user/login');
      
    } catch (error: any) {
      console.error('❌ Railway Gateway 회원가입 오류:', error);
      alert('회원가입 실패: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl px-8 py-12">
          {/* Sign Up Title */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
              Sign Up
            </h1>
            <p className="text-gray-600 mt-2">새 계정을 만들어보세요</p>
          </div>

          {/* Sign Up Form */}
          <div className="space-y-6">
            {/* User ID Input */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                User ID *
              </label>
              <input
                type="text"
                name="user_id"
                value={userData.user_id}
                onChange={handleInputChange}
                placeholder="사용자 ID를 입력하세요"
                className="w-full px-4 py-3 text-lg text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 transition-all duration-300"
                required
              />
            </div>

            {/* Password Input */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password *
              </label>
              <input
                type="number"
                name="user_pw"
                value={userData.user_pw}
                onChange={handleInputChange}
                placeholder="비밀번호를 입력하세요 (숫자)"
                className="w-full px-4 py-3 text-lg text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 transition-all duration-300"
                required
              />
              <p className="text-xs text-gray-500 mt-1">비밀번호는 숫자로 입력해주세요</p>
            </div>

            {/* Company ID Input */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company ID
              </label>
              <input
                type="text"
                name="company_id"
                value={userData.company_id}
                onChange={handleInputChange}
                placeholder="회사 ID를 입력하세요 (선택사항)"
                className="w-full px-4 py-3 text-lg text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 transition-all duration-300"
              />
            </div>

            {/* Sign Up Button */}
            <button
              type="submit"
              onClick={handleSignUp}
              className="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm mt-8"
            >
              Sign Up
            </button>

            {/* Login Link */}
            <div className="text-center mt-6">
              <p className="text-gray-600">
                이미 계정이 있으신가요?{' '}
                <button
                  onClick={() => router.push('/user/login')}
                  className="text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200"
                >
                  로그인하기
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
