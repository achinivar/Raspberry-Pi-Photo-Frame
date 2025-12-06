from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_photo_info(filename):
    """Get photo information including size and creation date"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        stat = os.stat(filepath)
        return {
            'filename': filename,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        }
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/gallery')
def gallery():
    photos = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                photo_info = get_photo_info(filename)
                if photo_info:
                    photos.append(photo_info)
    
    # Sort by creation date (newest first)
    photos.sort(key=lambda x: x['created'], reverse=True)
    return render_template('gallery.html', photos=photos)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'photos' not in request.files:
        flash('No file selected')
        return redirect(url_for('upload_page'))
    
    files = request.files.getlist('photos')
    uploaded_count = 0
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            # Generate unique filename
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            try:
                # Save file
                file.save(filepath)
                
                # Validate and optimize image
                with Image.open(filepath) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Resize if too large (max 1920x1080)
                    if img.width > 1920 or img.height > 1080:
                        img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                        img.save(filepath, 'JPEG', quality=85)
                
                uploaded_count += 1
                
            except Exception as e:
                flash(f'Error processing {file.filename}: {str(e)}')
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            flash(f'Invalid file: {file.filename if file else "Unknown"}')
    
    if uploaded_count > 0:
        flash(f'Successfully uploaded {uploaded_count} photo(s)!')
    else:
        flash('No valid photos were uploaded')
    
    return redirect(url_for('gallery'))

@app.route('/delete_photo', methods=['POST'])
def delete_photo():
    data = request.get_json()
    filename = data.get('filename')
    
    if filename and allowed_file(filename):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return jsonify({'success': True, 'message': 'Photo deleted successfully'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error deleting photo: {str(e)}'})
    
    return jsonify({'success': False, 'message': 'Invalid filename'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)