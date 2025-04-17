docker pull myoung34/github-runner:latest

docker run -d --restart always --name github-runner \
  -e REPO_URL="https://github.com/Morawski21/personal_logs" \
  -e RUNNER_TOKEN="ANDIVZBXWLYMG56OQSOE363IACY4A" \
  -e RUNNER_NAME="synology-runner" \
  -e RUNNER_WORKDIR="/tmp/github-runner-your-repo" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  myoung34/github-runner:latest