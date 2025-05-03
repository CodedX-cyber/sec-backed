import sqlite3
import json

def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('''CREATE TABLE companies
                 (name TEXT, ticker TEXT, industry TEXT, 
                  details TEXT, market_cap REAL, 
                  headquarters TEXT, ceo TEXT, 
                  founded INTEGER, employees INTEGER)''')
    
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
         0.4e52, 'Florida', 'Nicolas Thomas', 2016, 195000),
        ('Amazon.com, Inc.', 'AMZN', 'E-commerce', 
         'E-commerce and cloud computing company.',
         1.3e12, 'Seattle, Washington', 'Andy Jassy', 1994, 1300000)
    ]
    c.executemany('''INSERT INTO companies (name, ticker, industry, details, market_cap, headquarters, ceo, founded, employees) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_data)
    return conn

def handler(request):
    try:
        conn = init_db()
        c = conn.cursor()
        
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return {'error': 'Invalid request data'}, 400
            
        query = data.get('query', '').lower()
        is_subscribed = data.get('isSubscribed', False)
        
        if not query:
            return [], 200
            
        c.execute('''SELECT * FROM companies 
                    WHERE lower(name) LIKE ? 
                    OR lower(ticker) LIKE ? 
                    OR lower(industry) LIKE ?''',
                  (f'%{query}%', f'%{query}%', f'%{query}%'))
        results = c.fetchall()
        
        response = []
        for row in results:
            company = {
                'name': row[0], 
                'ticker': row[1],
                'market_cap': f"${row[4]:,.0f}B" if row[4] else None,
                'headquarters': row[5]
            }
            if is_subscribed:
                company.update({
                    'industry': row[2],
                    'details': row[3],
                    'ceo': row[6],
                    'founded': row[7],
                    'employees': f"{row[8]:,}" if row[8] else None
                })
            response.append(company)
        
        conn.close()
        return response, 200
    except Exception as e:
        return {'error': str(e)}, 500