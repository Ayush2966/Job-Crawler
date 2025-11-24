"""
Flask API Server for Job Crawler UI
"""
import sys
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.db_handler import init_db
from src.database.profile_manager import (
    init_user_profiles,
    create_default_profile,
    get_user_profile,
    update_user_profile,
    get_all_active_profiles
)
from config.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize database on startup
def initialize():
    init_db()
    if Config.ENABLE_USER_PROFILES:
        init_user_profiles()

# Initialize on app creation
initialize()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Job Crawler API is running'})

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        profiles = get_all_active_profiles()
        config_data = {
            'preferred_locations': Config.PREFERRED_LOCATIONS,
            'min_salary': Config.MIN_SALARY,
            'max_salary': Config.MAX_SALARY,
            'email_recipients': [Config.EMAIL_RECIPIENT] if Config.EMAIL_RECIPIENT else [],
            'profiles': [profile.to_dict() for profile in profiles]
        }
        return jsonify(config_data)
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update job search configuration"""
    try:
        data = request.get_json()
        
        # Extract form data
        receiver_emails = data.get('receiver_emails', [])
        locations = data.get('locations', [])
        salary_ranges = data.get('salary_ranges', [])  # [{min: 5, max: 10}, {min: 10, max: 20}]
        experience_min = data.get('experience_min')
        experience_max = data.get('experience_max')
        job_title = data.get('job_title', '')
        
        if not receiver_emails:
            return jsonify({'error': 'At least one receiver email is required'}), 400
        
        # Create or update profiles for each email
        updated_profiles = []
        for email in receiver_emails:
            if not email or not email.strip():
                continue
                
            email = email.strip()
            
            # Get or create profile
            profile = get_user_profile(email)
            if not profile:
                profile = create_default_profile(email, name=email.split('@')[0])
            
            if profile:
                # Update profile with new preferences
                update_data = {}
                
                # Update locations
                if locations:
                    update_data['preferred_locations'] = [loc.strip() for loc in locations if loc.strip()]
                
                # Update salary range (use first range or aggregate)
                if salary_ranges and len(salary_ranges) > 0:
                    # Use the minimum of all min salaries and maximum of all max salaries
                    all_mins = [r.get('min', 0) for r in salary_ranges if r.get('min')]
                    all_maxs = [r.get('max', 999999) for r in salary_ranges if r.get('max')]
                    if all_mins:
                        update_data['expected_salary_min'] = min(all_mins)
                    if all_maxs:
                        update_data['expected_salary_max'] = max(all_maxs)
                
                # Update experience
                if experience_min is not None:
                    update_data['experience_years'] = experience_min
                
                # Update job title/role
                if job_title:
                    update_data['current_role'] = job_title
                    # Also update primary skills based on job title
                    if 'python' in job_title.lower():
                        update_data['primary_skills'] = ['Python', 'JavaScript', 'React']
                    elif 'react' in job_title.lower() or 'frontend' in job_title.lower():
                        update_data['primary_skills'] = ['React', 'JavaScript', 'TypeScript']
                    elif 'backend' in job_title.lower():
                        update_data['primary_skills'] = ['Python', 'Java', 'Node.js']
                
                # Update the profile
                updated_profile = update_user_profile(email, **update_data)
                if updated_profile:
                    updated_profiles.append(updated_profile.to_dict())
        
        # Also update global config for locations and salary
        # Note: This would require updating .env file, which we'll handle differently
        # For now, we'll just update user profiles
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'profiles': updated_profiles,
            'updated_count': len(updated_profiles)
        })
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all user profiles"""
    try:
        profiles = get_all_active_profiles()
        return jsonify({
            'profiles': [profile.to_dict() for profile in profiles]
        })
    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<email>', methods=['GET'])
def get_profile(email):
    """Get a specific user profile"""
    try:
        profile = get_user_profile(email)
        if profile:
            return jsonify(profile.to_dict())
        else:
            return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    if Config.ENABLE_USER_PROFILES:
        init_user_profiles()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)

