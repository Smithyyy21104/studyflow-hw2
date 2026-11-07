#!/usr/bin/env bash
set -Eeuo pipefail

: "${DOCKERHUB_USERNAME:?Set DOCKERHUB_USERNAME through GitHub Actions secrets}"
: "${IMAGE_TAG:?Set IMAGE_TAG to the Git commit image tag}"

IMAGE="${DOCKERHUB_USERNAME}/studyflow-hw3:${IMAGE_TAG}"
CONTAINER="studyflow-hw3"
BACKUP="${CONTAINER}-previous"
VOLUME="studyflow-hw3-data"
HOST_PORT="${HOST_PORT:-8000}"
DEPLOY_VERSION="${DEPLOY_VERSION:-${IMAGE_TAG}}"

if ! command -v docker >/dev/null 2>&1; then
  echo 'ERROR: Docker is not installed on the deployment runner.' >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo 'ERROR: Docker daemon is not running. Open Docker Desktop.' >&2
  exit 1
fi

# Do not stop the working application until the new image is downloaded.
docker pull "$IMAGE"
docker volume create "$VOLUME" >/dev/null

# Clean an older backup from a previously successful deployment.
if docker container inspect "$BACKUP" >/dev/null 2>&1; then
  docker rm -f "$BACKUP" >/dev/null
fi

HAD_OLD=0
if docker container inspect "$CONTAINER" >/dev/null 2>&1; then
  HAD_OLD=1
  docker stop "$CONTAINER" >/dev/null
  docker rename "$CONTAINER" "$BACKUP"
fi

rollback() {
  echo 'Deployment failed; attempting rollback.' >&2
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
  if [ "$HAD_OLD" -eq 1 ]; then
    docker rename "$BACKUP" "$CONTAINER"
    docker start "$CONTAINER" >/dev/null
    echo 'Rollback: previous container restarted.' >&2
  fi
}
trap rollback ERR

docker run -d \
  --name "$CONTAINER" \
  --restart unless-stopped \
  --publish "127.0.0.1:${HOST_PORT}:8000" \
  --mount "type=volume,src=${VOLUME},dst=/data" \
  --env TASKS_DB_PATH=/data/studyflow.sqlite3 \
  --env "DEPLOY_VERSION=${DEPLOY_VERSION}" \
  "$IMAGE" >/dev/null

OK=0
for attempt in $(seq 1 35); do
  if curl --fail --silent --max-time 3 "http://127.0.0.1:${HOST_PORT}/health" >/dev/null; then
    OK=1
    break
  fi
  sleep 2
done

if [ "$OK" -ne 1 ]; then
  echo 'ERROR: New application failed health check.' >&2
  docker logs "$CONTAINER" >&2 || true
  false
fi

# A failed health check above rolls back via the ERR trap.
trap - ERR
if [ "$HAD_OLD" -eq 1 ]; then
  docker rm -f "$BACKUP" >/dev/null
fi

echo "Deployed image: $IMAGE"
echo "Service: http://127.0.0.1:${HOST_PORT}/"
echo "Health: http://127.0.0.1:${HOST_PORT}/health"
