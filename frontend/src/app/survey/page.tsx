'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

export default function CompanyTypePage() {
  const router = useRouter();
  const [selectedType, setSelectedType] = useState<string>('');

  const handleCompanyTypeSelect = (type: string) => {
    setSelectedType(type);
    
    const surveyData = {
      user_id: 'test_user', // 실제로는 로그인한 사용자 정보를 사용
      company_type: type
    };
    
    alert(JSON.stringify(surveyData, null, 2));
    console.log('Company type selected:', surveyData);
    
    // 선택 후 다음 페이지로 이동 (예: 대시보드)
    setTimeout(() => {
      router.push('/dashboard');
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 tracking-tight mb-4">
              회사 유형을 선택해주세요
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              귀하의 회사 유형에 맞는 맞춤형 서비스를 제공하기 위해 
              회사 유형을 선택해주세요
            </p>
          </div>

          {/* Company Type Selection */}
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* LME Option */}
            <div 
              className={`relative group cursor-pointer transition-all duration-300 transform hover:scale-105 ${
                selectedType === 'LME' ? 'ring-4 ring-blue-500' : ''
              }`}
              onClick={() => handleCompanyTypeSelect('LME')}
            >
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-8 h-full text-white">
                <div className="text-center">
                  {/* Icon */}
                  <div className="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  
                  {/* Title */}
                  <h2 className="text-3xl font-bold mb-4">LME</h2>
                  <p className="text-xl font-semibold mb-4">Large Manufacturing Enterprise</p>
                  
                  {/* Description */}
                  <p className="text-blue-100 text-sm leading-relaxed">
                    대규모 제조업 기업으로, 연매출 1,000억원 이상 또는 
                    종업원 1,000명 이상의 기업입니다.
                  </p>
                  
                  {/* Features */}
                  <div className="mt-6 space-y-2">
                    <div className="flex items-center justify-center text-sm">
                      <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                      대규모 생산 시설 운영
                    </div>
                    <div className="flex items-center justify-center text-sm">
                      <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                      복잡한 공급망 관리
                    </div>
                    <div className="flex items-center justify-center text-sm">
                      <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                      고도화된 자동화 시스템
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Selection Indicator */}
              {selectedType === 'LME' && (
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              )}
            </div>

            {/* SME Option */}
            <div 
              className={`relative group cursor-pointer transition-all duration-300 transform hover:scale-105 ${
                selectedType === 'SME' ? 'ring-4 ring-green-500' : ''
              }`}
              onClick={() => handleCompanyTypeSelect('SME')}
            >
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-8 h-full text-white">
                <div className="text-center">
                  {/* Icon */}
                  <div className="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6" />
                    </svg>
                  </div>
                  
                  {/* Title */}
                  <h2 className="text-3xl font-bold mb-4">SME</h2>
                  <p className="text-xl font-semibold mb-4">Small & Medium Enterprise</p>
                  
                  {/* Description */}
                  <p className="text-green-100 text-sm leading-relaxed">
                    중소기업으로, 연매출 1,000억원 미만 또는 
                    종업원 1,000명 미만의 기업입니다.
                  </p>
                  
                  {/* Features */}
                  <div className="mt-6 space-y-2">
                    <div className="flex items-center justify-center text-sm">
                      <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                      유연한 운영 체계
                    </div>
                    <div className="flex items-center justify-center text-sm">
                      <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                      빠른 의사결정
                    </div>
                    <div className="flex items-center justify-center text-sm">
                      <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                      혁신적인 솔루션
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Selection Indicator */}
              {selectedType === 'SME' && (
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              )}
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-12 text-center">
            <div className="bg-gray-50 rounded-xl p-6 max-w-2xl mx-auto">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                💡 선택 가이드
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                <strong>LME</strong>는 대규모 제조업 기업으로 복잡한 생산 프로세스와 
                대용량 데이터 처리가 필요한 기업입니다.<br/>
                <strong>SME</strong>는 중소기업으로 빠른 대응과 유연한 운영이 
                중요한 기업입니다.
              </p>
            </div>
          </div>

          {/* Back Button */}
          <div className="mt-8 text-center">
            <button
              onClick={() => router.back()}
              className="inline-flex items-center px-6 py-3 text-gray-600 hover:text-gray-800 transition-colors duration-200"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              이전으로 돌아가기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
