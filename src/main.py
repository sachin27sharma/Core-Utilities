import uvicorn
from src.core.app import BaseApp
from src.config.settings import Settings
import os

if __name__ == "__main__":
    # Load settings from config.yaml in the root folder
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    settings = Settings.load(config_path)
    app_instance = BaseApp(config_path)
    app_instance.settings = settings  # Ensure BaseApp uses the already loaded settings
    app = app_instance.create_app()
    uvicorn.run(app, host=settings.app.host, port=settings.app.port,
                reload=settings.app.reload,
                workers=settings.app.workers
                )

