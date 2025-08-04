# 모든 명령어 앞에 'make' 를 붙여서 실행해야 함
# 🔧 공통 명령어
up:
	docker-compose -f service/docker-compose.yml up -d --build

down:
	docker-compose -f service/docker-compose.yml down

logs:
	docker-compose -f service/docker-compose.yml logs -f

restart:
	docker-compose -f service/docker-compose.yml down && docker-compose -f service/docker-compose.yml up -d --build

ps:
	docker-compose -f service/docker-compose.yml ps

# 🚀 마이크로서비스별 명령어

## gateway
build-gateway:
	docker-compose -f service/docker-compose.yml build gateway

up-gateway:
	docker-compose -f service/docker-compose.yml up -d gateway

down-gateway:
	docker-compose -f service/docker-compose.yml stop gateway

logs-gateway:
	docker-compose -f service/docker-compose.yml logs -f gateway

restart-gateway:
	docker-compose -f service/docker-compose.yml stop gateway && docker-compose -f service/docker-compose.yml up -d gateway

## assesment-service
build-assesment:
	docker-compose -f service/docker-compose.yml build assesment-service

up-assesment:
	docker-compose -f service/docker-compose.yml up -d assesment-service

down-assesment:
	docker-compose -f service/docker-compose.yml stop assesment-service

logs-assesment:
	docker-compose -f service/docker-compose.yml logs -f assesment-service

restart-assesment:
	docker-compose -f service/docker-compose.yml stop assesment-service && docker-compose -f service/docker-compose.yml up -d assesment-service

## chatbot-service
build-chatbot:
	docker-compose -f service/docker-compose.yml build chatbot-service

up-chatbot:
	docker-compose -f service/docker-compose.yml up -d chatbot-service

down-chatbot:
	docker-compose -f service/docker-compose.yml stop chatbot-service

logs-chatbot:
	docker-compose -f service/docker-compose.yml logs -f chatbot-service

restart-chatbot:
	docker-compose -f service/docker-compose.yml stop chatbot-service && docker-compose -f service/docker-compose.yml up -d chatbot-service

## monitoring-service
build-monitoring:
	docker-compose -f service/docker-compose.yml build monitoring-service

up-monitoring:
	docker-compose -f service/docker-compose.yml up -d monitoring-service

down-monitoring:
	docker-compose -f service/docker-compose.yml stop monitoring-service

logs-monitoring:
	docker-compose -f service/docker-compose.yml logs -f monitoring-service

restart-monitoring:
	docker-compose -f service/docker-compose.yml stop monitoring-service && docker-compose -f service/docker-compose.yml up -d monitoring-service

## report-service
build-report:
	docker-compose -f service/docker-compose.yml build report-service

up-report:
	docker-compose -f service/docker-compose.yml up -d report-service

down-report:
	docker-compose -f service/docker-compose.yml stop report-service

logs-report:
	docker-compose -f service/docker-compose.yml logs -f report-service

restart-report:
	docker-compose -f service/docker-compose.yml stop report-service && docker-compose -f service/docker-compose.yml up -d report-service

## request-service
build-request:
	docker-compose -f service/docker-compose.yml build request-service

up-request:
	docker-compose -f service/docker-compose.yml up -d request-service

down-request:
	docker-compose -f service/docker-compose.yml stop request-service

logs-request:
	docker-compose -f service/docker-compose.yml logs -f request-service

restart-request:
	docker-compose -f service/docker-compose.yml stop request-service && docker-compose -f service/docker-compose.yml up -d request-service

## response-service
build-response:
	docker-compose -f service/docker-compose.yml build response-service

up-response:
	docker-compose -f service/docker-compose.yml up -d response-service

down-response:
	docker-compose -f service/docker-compose.yml stop response-service

logs-response:
	docker-compose -f service/docker-compose.yml logs -f response-service

restart-response:
	docker-compose -f service/docker-compose.yml stop response-service && docker-compose -f service/docker-compose.yml up -d response-service

## redis
up-redis:
	docker-compose -f service/docker-compose.yml up -d redis

down-redis:
	docker-compose -f service/docker-compose.yml stop redis

logs-redis:
	docker-compose -f service/docker-compose.yml logs -f redis

restart-redis:
	docker-compose -f service/docker-compose.yml stop redis && docker-compose -f service/docker-compose.yml up -d redis

## n8n
build-n8n:
	docker-compose -f service/docker-compose.yml build n8n

up-n8n:
	docker-compose -f service/docker-compose.yml up -d n8n

down-n8n:
	docker-compose -f service/docker-compose.yml stop n8n

logs-n8n:
	docker-compose -f service/docker-compose.yml logs -f n8n

restart-n8n:
	docker-compose -f service/docker-compose.yml stop n8n && docker-compose -f service/docker-compose.yml up -d n8n

# 🧹 정리 명령어
clean:
	docker-compose -f service/docker-compose.yml down -v --remove-orphans
	docker system prune -f

clean-all:
	docker-compose -f service/docker-compose.yml down -v --remove-orphans
	docker system prune -af
	docker volume prune -f

# 📊 상태 확인
status:
	docker-compose -f service/docker-compose.yml ps
	docker-compose -f service/docker-compose.yml top

# 🔍 디버깅
shell-gateway:
	docker-compose -f service/docker-compose.yml exec gateway /bin/bash

shell-assesment:
	docker-compose -f service/docker-compose.yml exec assesment-service /bin/bash

shell-chatbot:
	docker-compose -f service/docker-compose.yml exec chatbot-service /bin/bash

shell-monitoring:
	docker-compose -f service/docker-compose.yml exec monitoring-service /bin/bash

shell-report:
	docker-compose -f service/docker-compose.yml exec report-service /bin/bash

shell-request:
	docker-compose -f service/docker-compose.yml exec request-service /bin/bash

shell-response:
	docker-compose -f service/docker-compose.yml exec response-service /bin/bash 