from flask import Flask, render_template
from BME280 import read_data

app = Flask(__name__)

@app.route('/')
def index():
	stats = read_data()
	return render_template("index.html", stats=stats)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)
