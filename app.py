from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/practice')
@app.route('/interview')
@app.route('/results')
def home():
    html_content = '<h1>CareerMantra AI</h1><p>Pandey Rupesh | Lucknow, UP</p>'
    return html_content

if __name__ == '__main__':
    print("🚀 CareerMantra AI starting...")
    app.run(debug=True, host='0.0.0.0', port=5000)
