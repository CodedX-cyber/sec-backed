import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import traceback
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, static_folder='images', static_url_path='/images')
CORS(app, resources={r"/*": {"origins": ["https://agroperfectsolutions.com"], "allow_headers": ["Content-Type", "Authorization"], "expose_headers": ["Content-Type"], "supports_credentials": True}})

# Ensure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def index():
    return send_file('index.html')

def init_db():
    """Initialize the SQLite database"""
    db_path = Path('companies.db')
    
    # Always create a new connection
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Try to create table (will fail if it exists)
        c.execute('''CREATE TABLE IF NOT EXISTS companies
                     (name TEXT, ticker TEXT, industry TEXT, 
                      details TEXT, market_cap REAL, 
                      headquarters TEXT, ceo TEXT, 
                      founded INTEGER, employees INTEGER)''')
        
        # Check if there's any data in the table
        c.execute('SELECT COUNT(*) FROM companies')
        count = c.fetchone()[0]
        
        if count == 0:
            logging.info("Initializing database with sample data...")
            sample_data = [
                ('Apple Inc.', 'AAPL', 'Technology', 
                 'Multinational tech company specializing in consumer electronics, software, and online services.',
                 2.5e12, 'Cupertino, California', 'Tim Cook', 1976, 154000),
                ('Tesla Inc.', 'TSLA', 'Automotive', 
                 'Electric vehicle manufacturer and clean energy company.',
                 8.5e11, 'Austin, Texas', 'Elon Musk', 2003, 100000),
                ('Walmart Inc.', 'WMT', 'Retail', 
                 'Global retail corporation operating a chain of hypermarkets, discount department stores, and grocery stores.',
                 4.2e11, 'Bentonville, Arkansas', 'Doug McMillon', 1962, 2300000),
                ('Pfizer Inc.', 'PFE', 'Pharmaceuticals', 
                 'Biotech and pharmaceutical company developing treatments and vaccines.',
                 3.1e11, 'New York City, NY', 'Albert Bourla', 1849, 83000),
                ('JPMorgan Chase', 'JPM', 'Finance', 
                 'Investment banking and financial services company.',
                 5.1e11, 'New York City, NY', 'Jamie Dimon', 1799, 275000),
                ('Microsoft Corporation', 'MSFT', 'Technology', 
                 'Technology company developing software, hardware, and cloud services.',
                 2.8e12, 'Redmond, Washington', 'Satya Nadella', 1975, 221000),
                ('Pro-Returns', 'PRO',
                 'Real Estate Investment Trust cryptocurrency Marijuana',
                 'Florida-based real estate investment trust focused on cryptocurrency and marijuana sectors.',
                 None, 'Florida', 'Nicolas Thomas', 2016, 195000),
                ('Amazon.com, Inc.', 'AMZN', 'E-commerce', 
                 'Global e-commerce and cloud computing company.',
                 1.3e12, 'Seattle, Washington', 'Andy Jassy', 1994, 1600000),
                ('NVIDIA Corporation', 'NVDA', 'Technology', 
                 'Specializes in graphics processing units and AI computing.',
                 1.2e12, 'Santa Clara, California', 'Jensen Huang', 1993, 35000),
                ('Meta Platforms, Inc.', 'META', 'Technology', 
                 'Social media and technology company.',
                 7.5e11, 'Menlo Park, California', 'Mark Zuckerberg', 2004, 87000),
                ('Alphabet Inc.', 'GOOGL', 'Technology', 
                 'Parent company of Google and other technology companies.',
                 1.8e12, 'Mountain View, California', 'Sundar Pichai', 1998, 186779)
            ]
            
            c.executemany('''INSERT INTO companies (name, ticker, industry, details, market_cap, 
                        headquarters, ceo, founded, employees) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_data)
            conn.commit()
            logging.info("Database initialized with sample data")
        
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/search', methods=['GET', 'POST'])
def search():
    try:
        # Get query parameter
        query = request.args.get('q') if request.method == 'GET' else request.json.get('query', '')
        if not query:
            return jsonify([])

        # Log the query for debugging
        logging.info(f"Search query received: {query}")

        # Initialize database connection
        conn = init_db()
        c = conn.cursor()
        
        # Search across multiple fields
        c.execute('''SELECT * FROM companies 
                    WHERE LOWER(name) LIKE ? 
                       OR LOWER(ticker) LIKE ? 
                       OR LOWER(industry) LIKE ?''', 
                  ('%' + query.lower() + '%', '%' + query.lower() + '%', '%' + query.lower() + '%'))
        
        results = c.fetchall()
        
        # Convert results to list of dictionaries
        companies = []
        for row in results:
            companies.append({
                'name': row[0],
                'ticker': row[1],
                'industry': row[2],
                'details': row[3],
                'market_cap': row[4],
                'headquarters': row[5],
                'ceo': row[6],
                'founded': row[7],
                'employees': row[8]
            })
        
        logging.info(f"Found {len(companies)} results")
        return jsonify(companies)
    except Exception as e:
        logging.error(f"Error in search endpoint: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the connection after use
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    # Initialize database at startup
    try:
        conn = init_db()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        exit(1)
    
    app.run(host='0.0.0.0', port=8080, debug=True)