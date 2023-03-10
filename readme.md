# Real-time Twitter Stream Visualization and classification

<p align="center">
  <img height="300px" width="300px" src="./python/tmp/logo.png">
</p>



This project is a real-time Twitter stream visualization that uses the following technologies:
- Node.js
- Express
- EJS
- Socket.IO
- kafka-node
- Python


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have the following installed on your machine:
- Node.js
- Python3
- Kafka
- kafka-python
- wordcloud

## Modeling
1. Usage of Kafka in order to stream tweets via the twitter api
2. Feature extraction ( preprocessing, embedding)
3. Topic classification using online KNN available on the river api
4. Summarizing the class using the TF-IDF model available on the scikit-learn api
5. Topic modelling using the Minibatch kmeans available on the scikit-learn api (Extension)

### Installing

1. Clone the repository to your local machine
git clone https://github.com/zack242/Kafka-Twitter-NLP.git

2. Install the necessary Node.js packages

3. Install the necessary Python packages (pip install -r requirements.txt)

4. Make sure Kafka is running on your local machine

5. Setup your api key in .env

6. Start the Node.js server

7. Visit [http://localhost:3000](http://localhost:3000) to view the visualization in your browser.



## Usage

1. Connect to the server by visiting [http://localhost:3000](http://localhost:3000) in your browser.

<p align="center">
  <img src="./python/tmp/webpage.png">
</p>

## Built With

* [Node.js](https://nodejs.org/) - JavaScript runtime
* [Express](https://expressjs.com/) - Node.js web framework
* [EJS](https://ejs.co/) - Embedded JavaScript templating
* [Socket.IO](https://socket.io/) - Real-time, bidirectional and event-based communication
* [kafka-node](https://github.com/SOHU-Co/kafka-node) - A Node.js client for Apache Kafka
* [Python](https://www.python.org/) - Programming language
* [wordcloud](https://github.com/amueller/word_cloud) - A little word cloud generator in Python

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
