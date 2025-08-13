FROM node:18-alpine

WORKDIR /app

# pnpm 설치
RUN npm install -g pnpm

# 패키지 파일 복사
COPY package*.json pnpm-lock.yaml ./

# 의존성 설치
RUN pnpm install

# 소스 코드 복사
COPY . .

# Next.js 빌드
RUN pnpm run build

# 포트 노출
EXPOSE 3000

# 개발 모드로 실행
CMD ["pnpm", "run", "dev"] 