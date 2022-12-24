from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/nbrTweets', methods=['GET'])
def get_nbr_tweets():
  nbr_tweets = 10
  return jsonify({'nbrTweets': nbr_tweets})

@app.route('/form', methods=['POST'])
def submit_form():
  print("jjj")
  data = request.form
  message = "Form submitted successfully"
  return jsonify({'message': message})

if __name__ == '__main__':
  app.run(debug=True, host='localhost',port=5055)