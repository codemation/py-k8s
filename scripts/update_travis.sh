var=$(cat scripts/nvar)
git_branch=$(cat scripts/cur_branch)
docker image build -f /py-k8s/setup/Dockerfile.dev --build-arg build_time_var=$var --build-arg build_time_branch=$git_branch -t 
