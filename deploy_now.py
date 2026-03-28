import ftplib
import os
from pathlib import Path

# Credentials from .env (hardcoded for reliability during script execution)
HOST = 'europ.iq.pl'
USER = 'chalupy_www'
PASS = 'ToTheMoon2024$$##@@' # Trying exactly as provided

# Local files to upload
FILES = [
    ('ekoindex.html', '/www/eko.chalupy.online/ekoindex.html'),
    ('.htaccess', '/www/eko.chalupy.online/.htaccess'),
    ('css/styles.css', '/www/eko.chalupy.online/css/styles.css')
]

# ... existing code ...

def upload():
    try:
        ftp = ftplib.FTP(HOST)
        ftp.login(USER, PASS)
        print("Connected successfully.")
        
        # Ensure directories exist
        sub_paths = ['/www/eko.chalupy.online', '/www/eko.chalupy.online/css']
        for p in sub_paths:
            try:
                ftp.mkd(p)
                print(f"Created directory {p}")
            except:
                pass # Already exists
        
        # Upload ekoindex.html
        with open('ekoindex.html', 'rb') as f:
            ftp.storbinary('STOR /www/eko.chalupy.online/ekoindex.html', f)
            print("Uploaded ekoindex.html")
            
        # Upload .htaccess
        with open('.htaccess', 'rb') as f:
            ftp.storbinary('STOR /www/eko.chalupy.online/.htaccess', f)
            print("Uploaded .htaccess")

        # Upload styles.css
        with open('css/styles.css', 'rb') as f:
            ftp.storbinary('STOR /www/eko.chalupy.online/css/styles.css', f)
            print("Uploaded styles.css")
            
        ftp.quit()
        print("Deployment complete!")
        
    except Exception as e:
        print(f"Deployment Error: {e}")

if __name__ == "__main__":
    upload()
