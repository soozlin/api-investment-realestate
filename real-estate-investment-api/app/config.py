from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    realtor_ddf_api_key: Optional[str] = None
    realtor_ddf_base_url: str = "https://api.ddf.ca/v1"
    
    bc_assessment_api_key: Optional[str] = None
    
    ltsa_api_key: Optional[str] = None
    ltsa_base_url: str = "https://ltsa.ca/api"
    
    vancouver_open_data_url: str = "https://opendata.vancouver.ca/api/v2"
    burnaby_open_data_url: str = "https://data.burnaby.ca/api"
    surrey_open_data_url: str = "https://data.surrey.ca/api"
    
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
