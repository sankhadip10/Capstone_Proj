.PHONY: docker-dev docker-test docker-reset docker-logs docker-shell

# Development
docker-dev:
	@bash scripts/docker-dev.sh

# Testing
docker-test:
	@bash scripts/docker-test.sh

# Load testing
docker-loadtest:
	@bash scripts/docker-loadtest.sh

# Reset environment
docker-reset:
	@bash scripts/docker-reset.sh

# View logs
docker-logs:
	docker-compose logs -f web

# Django shell
docker-shell:
	docker-compose exec web python manage.py shell

# Database shell
docker-db:
	docker-compose exec mysql mysql -u root -p storefront3

# Redis CLI
docker-redis:
	docker-compose exec redis redis-cli

# Cache inspection
docker-cache:
	docker-compose exec web python manage.py inspect_cache

# Warm cache
docker-cache-warm:
	docker-compose --profile cache run --rm cache-warmer