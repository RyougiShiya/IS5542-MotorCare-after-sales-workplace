"""MotorCare local or authenticated hosted entry point."""
from motorcare.ui import build
from motorcare.security import launch_options

if __name__ == '__main__':
    build().queue(default_concurrency_limit=1,max_size=8,api_open=False).launch(**launch_options())
