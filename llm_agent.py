"""
LLM-Enhanced Coding Agent for Tiny Backspace

This module provides an enhanced coding agent that can optionally use real LLM APIs
while maintaining compatibility with the existing rule-based approach.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM integration"""
    provider: str = "openai"  # "openai", "anthropic", or "rule_based"
    api_key: Optional[str] = None
    model: str = "gpt-4"
    max_tokens: int = 4000
    temperature: float = 0.1

class LLMCodingAgent:
    """
    Enhanced coding agent that can use real LLM APIs or fall back to rule-based approach
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config if config is not None else LLMConfig()
        self._setup_llm()
    
    def _setup_llm(self):
        """Setup LLM client based on configuration"""
        if self.config.provider == "openai":
            try:
                import openai
                if self.config.api_key:
                    openai.api_key = self.config.api_key
                else:
                    # Try to get from environment
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        openai.api_key = api_key
                    else:
                        logger.warning("OpenAI API key not found, falling back to rule-based approach")
                        self.config.provider = "rule_based"
            except ImportError:
                logger.warning("OpenAI not installed, falling back to rule-based approach")
                self.config.provider = "rule_based"
        
        elif self.config.provider == "anthropic":
            try:
                import anthropic
                if self.config.api_key:
                    self.anthropic_client = anthropic.Anthropic(api_key=self.config.api_key)
                else:
                    # Try to get from environment
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                    if api_key:
                        self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                    else:
                        logger.warning("Anthropic API key not found, falling back to rule-based approach")
                        self.config.provider = "rule_based"
            except ImportError:
                logger.warning("Anthropic not installed, falling back to rule-based approach")
                self.config.provider = "rule_based"
    
    def analyze_code(self, repo_path: str, prompt: str) -> Dict:
        """Analyze code using LLM or fall back to rule-based approach"""
        if self.config.provider == "rule_based":
            from coding_agent import CodingAgent
            agent = CodingAgent(repo_path)
            return agent.analyze_repository()
        try:
            return self._analyze_with_llm(repo_path, prompt)
        except Exception as e:
            logger.error(f"LLM analysis failed for prompt '{prompt}': {e}", exc_info=True)
            from coding_agent import CodingAgent
            agent = CodingAgent(repo_path)
            # Optionally, add a field to indicate fallback was used
            result = agent.analyze_repository()
            result['llm_fallback'] = True
            result['llm_error'] = str(e)
            return result
    
    def _analyze_with_llm(self, repo_path: str, prompt: str) -> Dict:
        """Analyze code using LLM"""
        # Get repository structure and key files
        repo_info = self._get_repo_info(repo_path)
        
        if self.config.provider == "openai":
            return self._analyze_with_openai(repo_info, prompt)
        elif self.config.provider == "anthropic":
            return self._analyze_with_anthropic(repo_info, prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
    
    def _analyze_with_openai(self, repo_info: Dict, prompt: str) -> Dict:
        """Analyze code using OpenAI API (v1.x)"""
        import openai
        # Determine API key
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
        system_prompt = self._build_analysis_system_prompt()
        user_prompt = self._build_analysis_user_prompt(repo_info, prompt)
        response = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        content = response.choices[0].message.content or ""
        return self._parse_llm_analysis_response(content, repo_info)
    
    def _analyze_with_anthropic(self, repo_info: Dict, prompt: str) -> Dict:
        """Analyze code using Anthropic API"""
        system_prompt = self._build_analysis_system_prompt()
        user_prompt = self._build_analysis_user_prompt(repo_info, prompt)
        
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Anthropic's response.content is a list of MessageBlock objects.
        # Each block may have a 'text' attribute, but not all do.
        # Concatenate all text from blocks that have a 'text' attribute.
        content = "".join(getattr(block, "text", "") for block in response.content)
        return self._parse_llm_analysis_response(content, repo_info)
    
    def _build_analysis_system_prompt(self) -> str:
        """Build system prompt for code analysis"""
        return """You are an expert code analyzer. Your task is to analyze a codebase and determine what changes need to be made to implement a given prompt.

You should:
1. Identify the key files that need to be modified
2. Understand the current code structure
3. Determine the specific changes required
4. Consider dependencies and potential side effects

Respond with a JSON object containing:
{
    "files_to_modify": ["list", "of", "file", "paths"],
    "analysis": "detailed analysis of what needs to be changed",
    "approach": "high-level approach to implementing the changes",
    "dependencies": ["list", "of", "dependencies", "to", "check"],
    "risks": ["potential", "risks", "or", "considerations"]
}"""
    
    def _build_analysis_user_prompt(self, repo_info: Dict, prompt: str) -> str:
        """Build user prompt for code analysis"""
        return f"""Please analyze this codebase and determine how to implement the following prompt:

PROMPT: {prompt}

REPOSITORY STRUCTURE:
{json.dumps(repo_info, indent=2)}

Please provide your analysis in the specified JSON format."""
    
    def _parse_llm_analysis_response(self, content: str, repo_info: Dict) -> Dict:
        """Parse LLM response into analysis object"""
        try:
            # Try to extract JSON from the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Convert to the format expected by the existing system
                return {
                    "files": repo_info.get("files", []),
                    "file_types": repo_info.get("file_types", {}),
                    "main_files": repo_info.get("main_files", []),
                    "dependencies": data.get("dependencies", []),
                    "llm_analysis": data.get("analysis", ""),
                    "files_to_modify": data.get("files_to_modify", []),
                    "approach": data.get("approach", ""),
                    "risks": data.get("risks", [])
                }
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
        
        # Fallback to basic analysis
        return {
            "files": repo_info.get("files", []),
            "file_types": repo_info.get("file_types", {}),
            "main_files": repo_info.get("main_files", []),
            "dependencies": [],
            "llm_analysis": content,
            "files_to_modify": [],
            "approach": "LLM analysis failed, using fallback",
            "risks": ["LLM parsing failed"]
        }
    
    def modify_code(self, repo_path: str, analysis: Dict, prompt: str) -> List[Dict]:
        """Modify code using LLM or fall back to rule-based approach"""
        if self.config.provider == "rule_based":
            from coding_agent import CodingAgent
            agent = CodingAgent(repo_path)
            return agent.generate_changes(prompt)
        try:
            return self._modify_with_llm(repo_path, analysis, prompt)
        except Exception as e:
            logger.error(f"LLM modification failed for prompt '{prompt}': {e}", exc_info=True)
            from coding_agent import CodingAgent
            agent = CodingAgent(repo_path)
            # Optionally, add a field to indicate fallback was used
            changes = agent.generate_changes(prompt)
            for change in changes:
                change['llm_fallback'] = True
                change['llm_error'] = str(e)
            return changes
    
    def _modify_with_llm(self, repo_path: str, analysis: Dict, prompt: str) -> List[Dict]:
        """Modify code using LLM"""
        if self.config.provider == "openai":
            return self._modify_with_openai(repo_path, analysis, prompt)
        elif self.config.provider == "anthropic":
            return self._modify_with_anthropic(repo_path, analysis, prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
    
    def _modify_with_openai(self, repo_path: str, analysis: Dict, prompt: str) -> List[Dict]:
        """Modify code using OpenAI API (v1.x)"""
        import openai
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
        modifications = []
        files_to_modify = analysis.get("files_to_modify", [])
        for file_path in files_to_modify:
            full_path = os.path.join(repo_path, file_path)
            if not os.path.exists(full_path):
                continue
            with open(full_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            system_prompt = self._build_modification_system_prompt()
            user_prompt = self._build_modification_user_prompt(
                file_path, current_content, analysis, prompt
            )
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            content = response.choices[0].message.content or ""
            new_content = self._extract_code_from_llm_response(content, current_content)
            if new_content != current_content:
                modifications.append({
                    'type': 'edit',
                    'file': file_path,
                    'old_content': current_content,
                    'new_content': new_content,
                    'description': f'Modified by LLM to implement: {prompt}'
                })
        return modifications
    
    def _modify_with_anthropic(self, repo_path: str, analysis: Dict, prompt: str) -> List[Dict]:
        """Modify code using Anthropic API"""
        modifications = []
        files_to_modify = analysis.get("files_to_modify", [])
        
        for file_path in files_to_modify:
            full_path = os.path.join(repo_path, file_path)
            if not os.path.exists(full_path):
                continue
            
            with open(full_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            system_prompt = self._build_modification_system_prompt()
            user_prompt = self._build_modification_user_prompt(
                file_path, current_content, analysis, prompt
            )
            
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            content = (
                getattr(response.content[0], "text", None)
                if hasattr(response.content[0], "text") and isinstance(getattr(response.content[0], "text", None), str)
                else str(response.content[0]) if response.content and len(response.content) > 0 else ""
            )
            new_content = self._extract_code_from_llm_response(str(content) or "", current_content)
            
            if new_content != current_content:
                modifications.append({
                    'type': 'edit',
                    'file': file_path,
                    'old_content': current_content,
                    'new_content': new_content,
                    'description': f'Modified by LLM to implement: {prompt}'
                })
        
        return modifications
    
    def _build_modification_system_prompt(self) -> str:
        """Build system prompt for code modification"""
        return """You are an expert code modifier. Your task is to modify existing code to implement a given feature or fix.

You should:
1. Understand the current code structure
2. Make minimal, focused changes
3. Maintain code style and conventions
4. Ensure the code remains functional
5. Add appropriate comments if needed

Respond with ONLY the complete modified code file. Do not include explanations, markdown, or code blocks."""
    
    def _build_modification_user_prompt(self, file_path: str, current_content: str, analysis: Dict, prompt: str) -> str:
        """Build user prompt for code modification"""
        return f"""Please modify the following code file to implement the given prompt:

FILE: {file_path}
PROMPT: {prompt}
ANALYSIS: {analysis.get('llm_analysis', '')}
APPROACH: {analysis.get('approach', '')}

CURRENT CODE:
{current_content}

Please provide the complete modified code file."""
    
    def _extract_code_from_llm_response(self, content: str, original_content: str) -> str:
        """Extract code from LLM response, handling various formats"""
        # Remove markdown code blocks if present
        if "```" in content:
            lines = content.split('\n')
            code_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)
            
            if code_lines:
                return '\n'.join(code_lines)
        
        # If no code blocks, assume the entire response is code
        return content.strip()
    
    def _get_repo_info(self, repo_path: str) -> Dict:
        """Get repository information for LLM analysis"""
        info = {
            "structure": {},
            "key_files": [],
            "file_contents": {},
            "files": [],
            "file_types": {},
            "main_files": []
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            rel_root = os.path.relpath(root, repo_path)
            if rel_root == '.':
                rel_root = ''
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(rel_root, file) if rel_root else file
                full_path = os.path.join(root, file)
                
                # Add to structure
                if rel_root not in info["structure"]:
                    info["structure"][rel_root] = []
                info["structure"][rel_root].append(file)
                
                # Add to files list
                info["files"].append(file_path)
                
                # Add to file types
                _, ext = os.path.splitext(file)
                if ext not in info["file_types"]:
                    info["file_types"][ext] = []
                info["file_types"][ext].append(file_path)
                
                # Add key files (Python, JavaScript, etc.)
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs')):
                    info["key_files"].append(file_path)
                    
                    # Read file content for small files
                    try:
                        if os.path.getsize(full_path) < 10000:  # 10KB limit
                            with open(full_path, 'r', encoding='utf-8') as f:
                                info["file_contents"][file_path] = f.read()
                    except Exception:
                        pass
                
                # Identify main files
                if file in ['main.py', 'app.py', 'index.js', 'package.json', 'requirements.txt', 'README.md']:
                    info["main_files"].append(file_path)
        
        return info 