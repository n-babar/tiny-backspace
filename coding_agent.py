import os
import re
from typing import List, Dict, Tuple
import json

class CodingAgent:
    def __init__(self, sandbox_dir: str):
        self.sandbox_dir = sandbox_dir
        
    def analyze_repository(self) -> Dict:
        """Analyze the repository structure and identify key files"""
        analysis = {
            'files': [],
            'file_types': {},
            'main_files': [],
            'dependencies': []
        }
        
        for root, dirs, files in os.walk(self.sandbox_dir):
            # Skip .git directory
            if '.git' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.sandbox_dir)
                
                # Get file extension
                _, ext = os.path.splitext(file)
                if ext not in analysis['file_types']:
                    analysis['file_types'][ext] = []
                analysis['file_types'][ext].append(rel_path)
                
                # Identify main files
                if file in ['main.py', 'app.py', 'index.js', 'package.json', 'requirements.txt', 'README.md']:
                    analysis['main_files'].append(rel_path)
                
                analysis['files'].append(rel_path)
        
        return analysis
    
    def read_file(self, file_path: str) -> str:
        """Read a file from the sandbox"""
        full_path = os.path.join(self.sandbox_dir, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {e}")
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to a file in the sandbox"""
        full_path = os.path.join(self.sandbox_dir, file_path)
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise Exception(f"Failed to write file {file_path}: {e}")
    
    def find_files_by_pattern(self, pattern: str) -> List[str]:
        """Find files matching a pattern"""
        matching_files = []
        for root, dirs, files in os.walk(self.sandbox_dir):
            if '.git' in root:
                continue
            for file in files:
                if re.search(pattern, file):
                    rel_path = os.path.relpath(os.path.join(root, file), self.sandbox_dir)
                    matching_files.append(rel_path)
        return matching_files
    
    def generate_changes(self, prompt: str) -> List[Dict]:
        """Generate code changes based on the prompt"""
        # This is a simplified agent that makes basic changes
        # In a real implementation, this would use an LLM to analyze and generate code
        
        changes = []
        analysis = self.analyze_repository()
        
        # Simple rule-based changes based on common patterns
        if 'validation' in prompt.lower() or 'input' in prompt.lower():
            changes.extend(self._add_input_validation(analysis))
        
        if 'error' in prompt.lower() or 'exception' in prompt.lower():
            changes.extend(self._add_error_handling(analysis))
            
        if 'test' in prompt.lower():
            changes.extend(self._add_tests(analysis))
        
        # Handle file creation requests
        if any(keyword in prompt.lower() for keyword in ['add', 'create', 'new file', 'function']):
            changes.extend(self._handle_file_creation(prompt, analysis))
        
        return changes
    
    def _add_input_validation(self, analysis: Dict) -> List[Dict]:
        """Add input validation to Python files"""
        changes = []
        
        for file_path in analysis['file_types'].get('.py', []):
            if 'test' not in file_path.lower():
                try:
                    content = self.read_file(file_path)
                    
                    # Simple validation: add basic type hints and validation
                    if 'def ' in content and 'request' in content.lower():
                        # This is a very simplified example
                        new_content = content.replace(
                            'def ',
                            'from typing import Dict, Any\n\ndef '
                        )
                        
                        changes.append({
                            'type': 'edit',
                            'file': file_path,
                            'old_content': content,
                            'new_content': new_content,
                            'description': f'Added type hints to {file_path}'
                        })
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return changes
    
    def _add_error_handling(self, analysis: Dict) -> List[Dict]:
        """Add error handling to Python files"""
        changes = []
        
        for file_path in analysis['file_types'].get('.py', []):
            if 'test' not in file_path.lower():
                try:
                    content = self.read_file(file_path)
                    
                    # Simple error handling: wrap main functions in try-catch
                    if 'def ' in content and 'return' in content:
                        # This is a very simplified example
                        lines = content.split('\n')
                        new_lines = []
                        
                        for line in lines:
                            if line.strip().startswith('def ') and ':' in line:
                                new_lines.append(line)
                                new_lines.append('    try:')
                                new_lines.append('        pass  # TODO: Add actual function body')
                                new_lines.append('    except Exception as e:')
                                new_lines.append('        print(f"Error: {e}")')
                                new_lines.append('        return {"error": str(e)}')
                            else:
                                new_lines.append(line)
                        
                        new_content = '\n'.join(new_lines)
                        
                        changes.append({
                            'type': 'edit',
                            'file': file_path,
                            'old_content': content,
                            'new_content': new_content,
                            'description': f'Added error handling to {file_path}'
                        })
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return changes
    
    def _add_tests(self, analysis: Dict) -> List[Dict]:
        """Add basic tests"""
        changes = []
        
        for file_path in analysis['file_types'].get('.py', []):
            if 'test' not in file_path.lower() and 'main' in file_path.lower():
                test_file = file_path.replace('.py', '_test.py')
                
                test_content = f'''import unittest
from {file_path.replace('.py', '')} import *

class Test{file_path.replace('.py', '').title().replace('_', '')}(unittest.TestCase):
    def test_basic_functionality(self):
        # TODO: Add actual tests
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
'''
                
                changes.append({
                    'type': 'create',
                    'file': test_file,
                    'content': test_content,
                    'description': f'Created test file {test_file}'
                })
        
        return changes
    
    def _handle_file_creation(self, prompt: str, analysis: Dict) -> List[Dict]:
        """Handle requests to create new files"""
        changes = []
        
        # Check if asking for Python file
        if 'python' in prompt.lower() or 'py' in prompt.lower():
            if 'hello' in prompt.lower() or 'function' in prompt.lower():
                # Create a simple Python file with a hello function
                python_content = '''def hello(name="World"):
    """A simple hello function"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello())
    print(hello("Python"))
'''
                
                changes.append({
                    'type': 'create',
                    'file': 'hello.py',
                    'content': python_content,
                    'description': 'Created hello.py with a hello function'
                })
        
        # Check if asking for README
        if 'readme' in prompt.lower():
            readme_content = '''# Project Description

This is a sample project created by Tiny Backspace.

## Features
- Sample functionality
- Easy to use

## Usage
Run the main script to see the output.

## Contributing
Feel free to contribute to this project!
'''
            
            changes.append({
                'type': 'create',
                'file': 'README.md',
                'content': readme_content,
                'description': 'Created README.md with project description'
            })
        
        return changes
    
    def apply_changes(self, changes: List[Dict]) -> List[str]:
        """Apply the generated changes to the repository"""
        applied_changes = []
        
        for change in changes:
            try:
                if change['type'] == 'edit':
                    self.write_file(change['file'], change['new_content'])
                    applied_changes.append(f"Edited {change['file']}: {change['description']}")
                    
                elif change['type'] == 'create':
                    self.write_file(change['file'], change['content'])
                    applied_changes.append(f"Created {change['file']}: {change['description']}")
                    
            except Exception as e:
                applied_changes.append(f"Failed to apply change to {change['file']}: {e}")
        
        return applied_changes 