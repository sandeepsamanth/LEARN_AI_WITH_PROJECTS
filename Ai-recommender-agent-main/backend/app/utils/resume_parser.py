"""
Resume Parser Utility
Extracts structured data from resume files (PDF, DOCX, TXT)
"""
import re
from typing import Dict, List, Optional
from pathlib import Path
import PyPDF2
from docx2python import docx2python
from app.utils.llm import llm_service


class ResumeParser:
    """Parse resumes and extract structured information"""
    
    def __init__(self):
        self.skills_keywords = [
            "python", "javascript", "java", "react", "node", "sql", "aws",
            "docker", "kubernetes", "git", "machine learning", "ai", "nlp",
            "data science", "tensorflow", "pytorch", "django", "flask",
            "mongodb", "postgresql", "redis", "graphql", "typescript"
        ]
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            docx_content = docx2python(file_path)
            return docx_content.text
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from resume file based on extension"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def extract_skills_basic(self, text: str) -> List[str]:
        """Extract skills using keyword matching"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def parse_with_llm(self, resume_text: str) -> Dict:
        """
        Use LLM to parse resume and extract structured data
        This is more accurate than basic keyword matching
        """
        system_prompt = """You are an expert resume parser. Extract structured information from resumes.
Return a JSON object with the following fields:
- full_name: string
- email: string (if found)
- phone: string (if found)
- skills: array of skill names
- experience_years: string (e.g., "2-3 years", "5+ years")
- education_level: string (e.g., "Bachelor's", "Master's", "PhD")
- work_experience: array of objects with {company, role, duration, description}
- education: array of objects with {institution, degree, field, year}
- summary: string (professional summary if available)

Return ONLY valid JSON, no additional text."""
        
        user_prompt = f"Parse this resume and extract the information:\n\n{resume_text[:3000]}"
        
        try:
            response = llm_service.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # Extract JSON from response (handle markdown code blocks)
            import json
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            parsed_data = json.loads(response)
            return parsed_data
            
        except Exception as e:
            # Fallback to basic extraction
            return {
                "skills": self.extract_skills_basic(resume_text),
                "experience_years": None,
                "education_level": None
            }
    
    def parse(self, file_path: str, use_llm: bool = True) -> Dict:
        """
        Main parsing function
        
        Args:
            file_path: Path to resume file
            use_llm: Whether to use LLM for parsing (more accurate)
            
        Returns:
            Dictionary with parsed resume data
        """
        # Extract text
        resume_text = self.extract_text(file_path)
        
        if use_llm:
            return self.parse_with_llm(resume_text)
        else:
            return {
                "resume_text": resume_text,
                "skills": self.extract_skills_basic(resume_text)
            }


# Global instance
resume_parser = ResumeParser()







