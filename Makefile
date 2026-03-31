.PHONY: build run clean

.DEFAULT_GOAL := help
build: # Build the Docker image
	docker build -t nepali-devblogs .


run: # Run the container (default port: 8070)
	docker run -d -p 8070:80 --name nepali-devblogs nepali-devblogs


stop: # Stop and remove the container
	docker stop nepali-devblogs 2>/dev/null || true
	docker rm nepali-devblogs 2>/dev/null || true

clean: # Clean temporary files
	@rm -rf $(TMP_PATH) __pycache__ .pytest_cache
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete
	@rm -rf build dist

help: # Show this help
	@egrep -h '\s#\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'