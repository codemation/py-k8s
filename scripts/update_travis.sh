var=$(cat nvar)
git_branch=$(cat cur_branch)
docker image build -f setup/Dockerfile.dev --build-arg build_time_var=$var --build-arg build_time_branch=$git_branch -t joshjamison/ignition setup/
