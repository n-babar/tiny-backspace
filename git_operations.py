import os
import tempfile
import git
from git import Repo
import subprocess
from typing import Optional

class GitOperations:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.sandbox_dir = None
        
    def clone_repo(self, repo_url: str) -> str:
        """Clone a repository into a temporary sandbox directory"""
        # Create a temporary directory for the sandbox
        self.sandbox_dir = tempfile.mkdtemp(prefix="tiny_backspace_")
        
        # Clone the repository
        try:
            repo = Repo.clone_from(repo_url, self.sandbox_dir)
            return self.sandbox_dir
        except Exception as e:
            raise Exception(f"Failed to clone repository: {e}")
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch for the changes"""
        if not self.sandbox_dir:
            raise Exception("No repository cloned")
            
        try:
            repo = Repo(self.sandbox_dir)
            # Create and checkout new branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            return True
        except Exception as e:
            raise Exception(f"Failed to create branch: {e}")
    
    def commit_changes(self, commit_message: str) -> bool:
        """Commit all changes in the repository"""
        if not self.sandbox_dir:
            raise Exception("No repository cloned")
            
        try:
            repo = Repo(self.sandbox_dir)
            # Add all changes
            repo.index.add('*')
            # Commit changes
            repo.index.commit(commit_message)
            return True
        except Exception as e:
            raise Exception(f"Failed to commit changes: {e}")
    
    def push_branch(self, branch_name: str) -> bool:
        """Push the branch to the remote repository"""
        if not self.sandbox_dir:
            raise Exception("No repository cloned")
            
        try:
            repo = Repo(self.sandbox_dir)
            # Push the branch
            origin = repo.remote(name='origin')
            origin.push(branch_name)
            return True
        except Exception as e:
            raise Exception(f"Failed to push branch: {e}")
    
    def create_pull_request(self, repo_url: str, branch_name: str, title: str, body: str) -> str:
        """Create a pull request using GitHub CLI"""
        if not self.github_token:
            raise Exception("GitHub token required for PR creation")
            
        try:
            # Set GitHub token for gh CLI
            env = os.environ.copy()
            env['GH_TOKEN'] = self.github_token
            
            # Extract repo owner and name from URL
            # Assuming format: https://github.com/owner/repo
            parts = repo_url.rstrip('/').split('/')
            owner = parts[-2]
            repo_name = parts[-1]
            
            # Create PR using gh CLI
            cmd = [
                'gh', 'pr', 'create',
                '--repo', f'{owner}/{repo_name}',
                '--head', branch_name,
                '--title', title,
                '--body', body
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=self.sandbox_dir)
            
            if result.returncode == 0:
                # Extract PR URL from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if 'https://github.com' in line and '/pull/' in line:
                        return line.strip()
                return result.stdout.strip()
            else:
                raise Exception(f"Failed to create PR: {result.stderr}")
                
        except Exception as e:
            raise Exception(f"Failed to create pull request: {e}")
    
    def cleanup(self):
        """Clean up the sandbox directory"""
        if self.sandbox_dir and os.path.exists(self.sandbox_dir):
            import shutil
            shutil.rmtree(self.sandbox_dir)
            self.sandbox_dir = None 