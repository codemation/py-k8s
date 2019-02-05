var=$(cat var)
python inc_var.py

from=$var
to=$(cat nvar)
mv setup/setup_v0.$from.sh setup/setup_v0.$to.sh
var=$(cat nvar)
git add setup; 
git add ignition;
git add scripts;
if [ $# -eq 1 ]
  then
    echo "adding commit - $1"
    git commit -m "$1"
else
  git commit -m "setup_v0.$var"
fi
git commit -m "setup_v0.$var"
rm -f nvar; rm -f var;
echo $var >> var
rm -f cur_branch
git status | grep "On branch" | awk {'print $3'} >> cur_branch
git_branch=$(cat cur_branch)
git push orgin $git_branch 
echo "current branch is $git_branch"
docker image build -f /stuff/py-k8s/setup/Dockerfile.dev --build-arg build_time_var=$var --build-arg build_time_branch=$git_branch -t joshjamison/ignition setup/
