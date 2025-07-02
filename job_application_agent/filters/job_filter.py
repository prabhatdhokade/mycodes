import re
from datetime import datetime, timedelta
from config.profile_config import USER_PROFILE
from utils.logger import get_logger

logger = get_logger('JobFilter')

class JobFilter:
    def __init__(self, profile=None):
        self.profile = profile or USER_PROFILE
        self.min_score_threshold = 0.4  # Minimum score to consider a job suitable
        
    def calculate_job_suitability(self, job_data):
        """
        Calculate suitability score for a job based on user profile
        Returns a score between 0 and 1
        """
        score = 0.0
        max_score = 0.0
        reasons = []
        
        # Title matching (30% weight)
        title_score, title_reasons = self._score_job_title(job_data.get('title', ''))
        score += title_score * 0.3
        max_score += 0.3
        reasons.extend(title_reasons)
        
        # Skills matching (25% weight)
        skills_score, skills_reasons = self._score_skills_match(
            job_data.get('description', '') + ' ' + job_data.get('title', '')
        )
        score += skills_score * 0.25
        max_score += 0.25
        reasons.extend(skills_reasons)
        
        # Location matching (15% weight)
        location_score, location_reasons = self._score_location(job_data.get('location', ''))
        score += location_score * 0.15
        max_score += 0.15
        reasons.extend(location_reasons)
        
        # Experience matching (15% weight)
        exp_score, exp_reasons = self._score_experience(job_data.get('experience_required', ''))
        score += exp_score * 0.15
        max_score += 0.15
        reasons.extend(exp_reasons)
        
        # Salary matching (10% weight)
        salary_score, salary_reasons = self._score_salary(
            job_data.get('salary_min'), job_data.get('salary_max')
        )
        score += salary_score * 0.10
        max_score += 0.10
        reasons.extend(salary_reasons)
        
        # Negative keywords check (5% weight)
        negative_score, negative_reasons = self._check_negative_keywords(
            job_data.get('description', '') + ' ' + job_data.get('title', '')
        )
        score += negative_score * 0.05
        max_score += 0.05
        reasons.extend(negative_reasons)
        
        # Normalize score
        final_score = score / max_score if max_score > 0 else 0
        
        return {
            'score': final_score,
            'is_suitable': final_score >= self.min_score_threshold,
            'reasons': reasons,
            'details': {
                'title_score': title_score,
                'skills_score': skills_score,
                'location_score': location_score,
                'experience_score': exp_score,
                'salary_score': salary_score,
                'negative_score': negative_score
            }
        }
    
    def _score_job_title(self, job_title):
        """Score job title match"""
        if not job_title:
            return 0.0, ["No job title provided"]
        
        job_title_lower = job_title.lower()
        score = 0.0
        reasons = []
        
        # Check for exact matches with target roles
        for role in self.profile['target_roles']:
            if role.lower() in job_title_lower:
                score = 1.0
                reasons.append(f"Exact role match: {role}")
                break
        
        # Check for partial matches
        if score == 0.0:
            keywords = ['python', 'software', 'developer', 'engineer', 'backend', 'full stack']
            matches = [kw for kw in keywords if kw in job_title_lower]
            if matches:
                score = min(len(matches) * 0.3, 0.8)
                reasons.append(f"Partial matches: {', '.join(matches)}")
        
        return score, reasons
    
    def _score_skills_match(self, job_description):
        """Score skills matching"""
        if not job_description:
            return 0.0, ["No job description provided"]
        
        job_desc_lower = job_description.lower()
        matched_skills = []
        
        for skill in self.profile['skills']:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, job_desc_lower):
                matched_skills.append(skill)
        
        if not matched_skills:
            return 0.0, ["No skills matched"]
        
        # Calculate score based on percentage of skills matched
        skill_percentage = len(matched_skills) / len(self.profile['skills'])
        score = min(skill_percentage * 2, 1.0)  # Cap at 1.0
        
        reasons = [f"Skills matched ({len(matched_skills)}/{len(self.profile['skills'])}): {', '.join(matched_skills[:5])}"]
        if len(matched_skills) > 5:
            reasons[0] += "..."
        
        return score, reasons
    
    def _score_location(self, job_location):
        """Score location match"""
        if not job_location:
            return 0.5, ["No location specified"]
        
        job_location_lower = job_location.lower()
        
        # Check for preferred locations
        for location in self.profile['preferred_locations']:
            if location.lower() in job_location_lower:
                return 1.0, [f"Location match: {location}"]
        
        # Check for remote work
        remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere']
        for keyword in remote_keywords:
            if keyword in job_location_lower:
                return 1.0, [f"Remote work option: {keyword}"]
        
        return 0.2, [f"Location not preferred: {job_location}"]
    
    def _score_experience(self, experience_required):
        """Score experience match"""
        if not experience_required:
            return 0.7, ["No experience requirement specified"]
        
        exp_text = experience_required.lower()
        user_experience = self.profile['experience_years']
        
        # Extract years from experience text
        year_matches = re.findall(r'(\d+)[\s]*(?:years?|yrs?)', exp_text)
        
        if not year_matches:
            # Check for experience level keywords
            if any(word in exp_text for word in ['entry', 'junior', 'fresher', 'graduate']):
                if user_experience <= 3:
                    return 1.0, ["Experience level match: Entry/Junior"]
                else:
                    return 0.8, ["Overqualified for entry level"]
            elif any(word in exp_text for word in ['senior', 'lead', 'principal']):
                if user_experience >= 3:
                    return 1.0, ["Experience level match: Senior"]
                else:
                    return 0.3, ["Underqualified for senior level"]
            return 0.5, ["Experience requirement unclear"]
        
        # Get the minimum required years
        min_years = int(year_matches[0])
        max_years = int(year_matches[-1]) if len(year_matches) > 1 else min_years + 2
        
        if min_years <= user_experience <= max_years:
            return 1.0, [f"Experience perfect match: {user_experience} years fits {min_years}-{max_years} years"]
        elif user_experience >= min_years:
            return 0.8, [f"Experience good match: {user_experience} years exceeds minimum {min_years} years"]
        elif user_experience >= min_years - 1:
            return 0.6, [f"Experience close match: {user_experience} years, required {min_years} years"]
        else:
            return 0.2, [f"Experience mismatch: {user_experience} years, required {min_years}+ years"]
    
    def _score_salary(self, salary_min, salary_max):
        """Score salary match"""
        user_min = self.profile.get('min_salary_lpa', 0)
        user_max = self.profile.get('max_salary_lpa', float('inf'))
        
        if salary_min is None and salary_max is None:
            return 0.5, ["No salary information provided"]
        
        # Convert to comparable format (assume LPA)
        job_min = salary_min or 0
        job_max = salary_max or job_min
        
        if job_max < user_min:
            return 0.1, [f"Salary too low: {job_max} LPA < {user_min} LPA"]
        elif job_min > user_max:
            return 0.3, [f"Salary very high: {job_min} LPA > {user_max} LPA"]
        else:
            return 1.0, [f"Salary in range: {job_min}-{job_max} LPA"]
    
    def _check_negative_keywords(self, text):
        """Check for keywords to avoid"""
        if not text:
            return 1.0, []
        
        text_lower = text.lower()
        found_negative = []
        
        for keyword in self.profile.get('avoid_keywords', []):
            if keyword.lower() in text_lower:
                found_negative.append(keyword)
        
        if found_negative:
            return 0.0, [f"Contains negative keywords: {', '.join(found_negative)}"]
        
        return 1.0, ["No negative keywords found"]
    
    def is_job_recent(self, posted_date, max_days=7):
        """Check if job is recently posted"""
        if not posted_date:
            return True  # Assume recent if no date provided
        
        if isinstance(posted_date, str):
            # Try to parse common date formats
            for date_format in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    posted_date = datetime.strptime(posted_date, date_format)
                    break
                except ValueError:
                    continue
            else:
                return True  # If we can't parse, assume recent
        
        cutoff_date = datetime.now() - timedelta(days=max_days)
        return posted_date >= cutoff_date
    
    def filter_jobs(self, jobs_list):
        """Filter and score a list of jobs"""
        filtered_jobs = []
        
        for job in jobs_list:
            # Check if job is recent
            if not self.is_job_recent(job.get('posted_date')):
                logger.debug(f"Skipping old job: {job.get('title')} at {job.get('company')}")
                continue
            
            # Calculate suitability
            suitability = self.calculate_job_suitability(job)
            
            # Add suitability info to job data
            job['suitability_score'] = suitability['score']
            job['is_suitable'] = suitability['is_suitable']
            job['suitability_reasons'] = suitability['reasons']
            job['suitability_details'] = suitability['details']
            
            # Only include suitable jobs
            if suitability['is_suitable']:
                filtered_jobs.append(job)
                logger.info(f"Suitable job found: {job.get('title')} at {job.get('company')} (Score: {suitability['score']:.2f})")
            else:
                logger.debug(f"Job filtered out: {job.get('title')} at {job.get('company')} (Score: {suitability['score']:.2f})")
        
        # Sort by suitability score (highest first)
        filtered_jobs.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return filtered_jobs
    
    def get_job_summary(self, job):
        """Get a summary of why a job is suitable"""
        summary = {
            'title': job.get('title', 'Unknown'),
            'company': job.get('company', 'Unknown'),
            'score': job.get('suitability_score', 0),
            'top_reasons': job.get('suitability_reasons', [])[:3],
            'location': job.get('location', 'Not specified'),
            'experience': job.get('experience_required', 'Not specified')
        }
        return summary