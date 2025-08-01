'use client';

import { useState } from 'react';

export default function Home() {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (inputValue.trim()) {
      alert(`입력하신 내용: ${inputValue}`);
      setInputValue(''); // 입력 필드 초기화
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // 기본 submit 방지
      if (inputValue.trim()) {
        alert(`입력하신 내용: ${inputValue}`);
        setInputValue('');
      }
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-4">
      {/* 메인 컨테이너 */}
      <div className="w-full max-w-2xl mx-auto">
        {/* 상단 질문 */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-medium text-gray-900 mb-2">
            무슨 작업을 하고 계세요?
          </h1>
        </div>

        {/* 입력 필드 */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-center bg-white border border-gray-300 rounded-2xl px-4 py-3 shadow-sm hover:border-gray-400 transition-colors">
            {/* 왼쪽 아이콘들 */}
            <div className="flex items-center space-x-3 mr-3">
              <button type="button" className="text-gray-600 hover:text-gray-800 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
              
              <button type="button" className="text-gray-600 hover:text-gray-800 transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              
              <span className="text-sm text-gray-600 font-medium">도구</span>
            </div>

            {/* 입력 필드 */}
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="무엇이든 물어보세요"
              className="flex-1 bg-transparent outline-none text-gray-900 placeholder-gray-500 text-base"
            />

            {/* 오른쪽 아이콘들 */}
            <div className="flex items-center space-x-3 ml-3">
              <button 
                type="submit"
                className="text-gray-600 hover:text-gray-800 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </button>
              
              <button 
                type="button"
                className="text-gray-600 hover:text-gray-800 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              </button>
            </div>
          </div>
        </form>

        {/* 추가 정보 */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            EriPotter AI 어시스턴트가 도와드립니다
          </p>
        </div>
      </div>
    </div>
  );
}
