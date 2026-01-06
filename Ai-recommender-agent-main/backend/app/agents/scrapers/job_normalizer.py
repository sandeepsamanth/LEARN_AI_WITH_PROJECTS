"""
Job normalizer
Converts scraped job data to unified schema
"""
from typing import Dict, List
from app.utils.embeddings import embedding_generator
from datetime import datetime
import re


def normalize_job(job: Dict, source: str) -> Dict:
    """
    Normalize scraped job data to unified schema
    
    Args:
        job: Raw job data from scraper
        source: Source name (indeed, remoteok, etc.)
        
    Returns:
        Normalized job dictionary
    """
    # Extract skills from description
    skills = extract_skills_from_text(job.get("description", ""))
    
    # Extract salary if present
    salary_info = extract_salary(job.get("description", "") + " " + job.get("salary", ""))
    
    # Determine job type
    job_type = determine_job_type(job.get("title", "") + " " + job.get("description", ""))
    
    # Generate embeddings
    description_text = job.get("description", "")
    title_text = job.get("title", "")
    
    description_embedding = None
    title_embedding = None
    
    if description_text:
        try:
            description_embedding = embedding_generator.generate_embedding(description_text)
            # pgvector stores arrays directly, no JSON conversion needed
        except:
            description_embedding = None
    
    if title_text:
        try:
            title_embedding = embedding_generator.generate_embedding(title_text)
            # pgvector stores arrays directly, no JSON conversion needed
        except:
            title_embedding = None
    
    normalized = {
        "title": job.get("title", "").strip(),
        "company": job.get("company", "").strip(),
        "location": job.get("location", "Remote").strip(),
        "description": description_text.strip(),
        "job_type": job_type,
        "experience_level": determine_experience_level(job.get("title", "") + " " + description_text),
        "salary_min": salary_info.get("min"),
        "salary_max": salary_info.get("max"),
        "salary_currency": salary_info.get("currency", "USD"),
        "required_skills": skills,
        "source": source,
        "source_url": job.get("source_url", ""),
        "posted_date": parse_date(job.get("published", "") or job.get("posted_date", "")),
        "application_url": job.get("source_url", ""),
        "description_embedding": description_embedding,
        "title_embedding": title_embedding,
        "job_metadata": {
            "original_data": {k: v for k, v in job.items() if k not in ["title", "company", "location", "description"]}
        }
    }
    
    return normalized


def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from job description"""
    common_skills = [
        # Programming Languages
        "python", "javascript", "java", "typescript", "c++", "c#", "go", "rust",
        "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "perl",
        # Web Frameworks
        "react", "vue", "angular", "node.js", "nodejs", "express", "expressjs",
        "django", "flask", "fastapi", "spring", "asp.net", "laravel", "rails",
        # Databases
        "sql", "mysql", "postgresql", "mongodb", "redis", "cassandra", "elasticsearch",
        "dynamodb", "oracle", "sqlite", "mariadb",
        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform",
        "ansible", "ci/cd", "github actions", "gitlab",
        # AI/ML
        "machine learning", "ml", "artificial intelligence", "ai", "deep learning",
        "neural networks", "tensorflow", "pytorch", "keras", "scikit-learn",
        "pandas", "numpy", "nlp", "natural language processing", "computer vision",
        "llm", "large language models", "generative ai", "gpt", "transformer",
        "prompt engineering", "rag", "retrieval augmented generation", "embeddings",
        # Blockchain
        "blockchain", "ethereum", "solidity", "smart contracts", "web3", "defi",
        # Data Science
        "data science", "data analysis", "data engineering", "big data", "spark",
        "hadoop", "kafka", "airflow",
        # Other Tools
        "git", "github", "graphql", "rest api", "microservices", "agile", "scrum"
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    # Extract skills (check for exact matches and variations)
    for skill in common_skills:
        # Check for skill in text (as whole word or part of phrase)
        if skill in text_lower:
            # Normalize skill name (title case for consistency)
            normalized = skill.title()
            # Handle special cases
            if skill == "node.js" or skill == "nodejs":
                normalized = "Node.js"
            elif skill == "c++":
                normalized = "C++"
            elif skill == "c#":
                normalized = "C#"
            elif skill == "ai" or skill == "artificial intelligence":
                normalized = "AI"
            elif skill == "ml" or skill == "machine learning":
                normalized = "Machine Learning"
            elif skill == "llm" or skill == "large language models":
                normalized = "LLM"
            elif skill == "rag" or skill == "retrieval augmented generation":
                normalized = "RAG"
            elif skill == "ci/cd":
                normalized = "CI/CD"
            elif skill == "scikit-learn":
                normalized = "Scikit-Learn"
            
            found_skills.append(normalized)
    
    return list(set(found_skills))


def extract_salary(text: str) -> Dict:
    """Extract salary information from text"""
    # Patterns for salary extraction
    patterns = [
        r'\$(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:k|K)?)',
        r'\$(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*/\s*yr',
        r'(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*-\s*(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*USD',
    ]
    
    salary_min = None
    salary_max = None
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                min_val = parse_salary_value(match.group(1))
                max_val = parse_salary_value(match.group(2)) if len(match.groups()) > 1 else min_val
                salary_min = min(min_val, max_val)
                salary_max = max(min_val, max_val)
                break
            except:
                continue
    
    return {
        "min": salary_min,
        "max": salary_max,
        "currency": "USD"
    }


def parse_salary_value(value: str) -> float:
    """Parse salary value (handles 'k' suffix)"""
    value = value.replace(",", "").replace("$", "").strip()
    if value.lower().endswith("k"):
        return float(value[:-1]) * 1000
    return float(value)


def determine_job_type(text: str) -> str:
    """Determine job type from text"""
    text_lower = text.lower()
    
    if "intern" in text_lower or "internship" in text_lower:
        return "internship"
    elif "part-time" in text_lower or "part time" in text_lower:
        return "part-time"
    elif "contract" in text_lower or "freelance" in text_lower:
        return "contract"
    else:
        return "full-time"


def determine_experience_level(text: str) -> str:
    """Determine experience level from text"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["senior", "lead", "principal", "architect"]):
        return "senior"
    elif any(word in text_lower for word in ["mid", "middle", "intermediate", "2-5", "3-5"]):
        return "mid"
    elif any(word in text_lower for word in ["junior", "entry", "graduate", "0-2", "1-2"]):
        return "entry"
    else:
        return "mid"  # Default


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime"""
    if not date_str:
        return None
    
    try:
        # Try common date formats
        from dateutil import parser
        return parser.parse(date_str)
    except:
        return None







