#!/usr/bin/env python3

from flask import Flask, send_file, abort, request
import os
import logging
from pathlib import Path

app = Flask(__name__)

# Base directory for serving files (current directory)
BASE_DIR = Path(__file__).parent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve files from the images directory"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    logger.info(f"Request for image: {filename} from IP: {client_ip}")
    
    file_path = BASE_DIR / 'images' / filename
    
    # Check if file exists and is within the images directory
    if file_path.exists() and file_path.is_file():
        try:
            # Verify the path is actually within the images directory (security check)
            file_path.resolve().relative_to((BASE_DIR / 'images').resolve())
            logger.info(f"Successfully serving image: {filename}")
            return send_file(file_path)
        except ValueError:
            # Path traversal attempt detected
            logger.warning(f"Path traversal attempt detected for image: {filename} from IP: {client_ip}")
            abort(403)
    else:
        logger.warning(f"Image not found: {filename} from IP: {client_ip}")
        abort(404)

@app.route('/fw/<path:filename>')
def serve_firmware(filename):
    """Serve files from the fw directory"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    logger.info(f"Request for firmware: {filename} from IP: {client_ip}")
    
    file_path = BASE_DIR / 'fw' / filename
    
    # Check if file exists and is within the fw directory
    if file_path.exists() and file_path.is_file():
        try:
            # Verify the path is actually within the fw directory (security check)
            file_path.resolve().relative_to((BASE_DIR / 'fw').resolve())
            logger.info(f"Successfully serving firmware: {filename}")
            return send_file(file_path)
        except ValueError:
            # Path traversal attempt detected
            logger.warning(f"Path traversal attempt detected for firmware: {filename} from IP: {client_ip}")
            abort(403)
    else:
        logger.warning(f"Firmware not found: {filename} from IP: {client_ip}")
        abort(404)

@app.route('/')
def index():
    """Basic index page"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    logger.info(f"Index page accessed from IP: {client_ip}")
    
    return """
    <h1>Flask File Server</h1>
    <p>Available endpoints:</p>
    <ul>
        <li><code>/images/&lt;path&gt;</code> - Serves files from the images directory</li>
        <li><code>/fw/&lt;path&gt;</code> - Serves files from the fw directory</li>
    </ul>
    """

@app.errorhandler(404)
def not_found(error):
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    logger.error(f"404 - File not found for request from IP: {client_ip} - Path: {request.path}")
    return "File not found", 404

@app.errorhandler(403)
def forbidden(error):
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    logger.error(f"403 - Access forbidden for request from IP: {client_ip} - Path: {request.path}")
    return "Access forbidden", 403

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(BASE_DIR / 'images', exist_ok=True)
    os.makedirs(BASE_DIR / 'fw', exist_ok=True)
    
    logger.info(f"Starting Flask file server")
    logger.info(f"Serving files from: {BASE_DIR}")
    logger.info(f"Images directory: {BASE_DIR / 'images'}")
    logger.info(f"Firmware directory: {BASE_DIR / 'fw'}")
    
    # Run the server  
    app.run(host='localhost', port=5000, debug=False)
