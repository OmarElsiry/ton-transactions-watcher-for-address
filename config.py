import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # TON Configuration
    MONITORED_WALLET = os.getenv('MONITORED_WALLET', 'UQDrY5iulWs_MyWTP9JSGedWBzlbeRmhCBoqsSaNiSLOs315')
    
    # API Configuration (no keys required)
    API_TYPE = os.getenv('API_TYPE', 'toncenter')  # toncenter or tonapi
    POLLING_INTERVAL = int(os.getenv('POLLING_INTERVAL', 10))  # seconds
    
    # Flask Configuration
    FLASK_PORT = int(os.getenv('FLASK_PORT', 8080))
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    SECRET_KEY = os.getenv('SECRET_KEY', 'ton-monitor-secret-2024')
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', './transactions.db')
    
    # Transaction Filtering
    MIN_AMOUNT_TON = float(os.getenv('MIN_AMOUNT_TON', 0.01))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        required_fields = ['MONITORED_WALLET']
        missing_fields = []
        
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        return True
