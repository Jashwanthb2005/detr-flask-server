git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --list

git branch            # List branches
git branch <name>     # Create branch
git checkout <name>   # Switch branch
git switch <name>     # (newer syntax)
git merge <branch>    # Merge into current branch
git branch -d <name>  # Delete branch

git remote -v
git remote add origin <url>
git push -u origin main
git push              # Push changes
git pull              # Fetch + merge
git fetch             # Fetch only

git log
git log --oneline --graph --all
git diff                  # Changes unstaged
git diff --staged         # Changes staged
