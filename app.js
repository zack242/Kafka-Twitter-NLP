const ejs = require('ejs');
const express = require('express')
const app = require('express')();
const server = require('http').createServer(app);
const io = require('socket.io')(server);
const kafka = require('kafka-node');
const fs = require('fs');
const path = require('path');
var NBR_TWEETS = 0;

app.set('view engine', 'ejs');
app.use(express.static(__dirname+'/public'))
app.get('/', (req, res) => {
  res.render('home');
});

app.get('/v1', (req, res) => {
  res.render('test');
});

io.on('connection', (socket) => {
  console.log('a user connected');
  socket.on('chat message', (msg) => {
    console.log(`message: ${msg}`);
  });
});

// Set the directory path
const directory = 'python/tmp';

// Set the image file name
const fileName = 'wordcloud.svg';

// Set the image file path
const filePath = path.join(directory, fileName);

app.get('/image', (req, res) => {
  // Read the image file
  fs.readFile(filePath, (err, data) => {
    if (err) {
      console.error(err);
      res.sendStatus(500);
      return;
    }
    // Set the content type and send the image data as a response
    res.setHeader('Content-Type', 'image/svg+xml');
    res.send(data);
  });
});

app.get('/NBRTWEETS', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.send({ nbrTweets: NBR_TWEETS });
});

const client = new kafka.KafkaClient('localhost:9092');
const consumer = new kafka.Consumer(
  client,
  [{ topic: 'rawTwitter', partition: 0, offset: 0 }],
  { fromOffset: false, autoCommit: true }
);

consumer.on('message', (message) => {
  io.emit('message', message.value);
  NBR_TWEETS++;
});

consumer.on('error', (err) => {
  console.log(`ERROR: ${err.toString()}`);
});

fs.watch(directory, (eventType, filename) => {
  if (eventType === 'change') {
    io.emit('message', 'go');
  }
});


app.get('/keyword', function(req, res) {
  const data = req.query.key;
  updaterule(data)
  res.json({ message: 'Data received' });
});

const { exec } = require('child_process');
updaterule("COVID")
exec(`python3 python/treadingword.py`, (error, stdout, stderr) => {
  if (error) {
    console.error(`exec error: ${error}`);
    return;
  }
  console.log(`stdout: ${stdout}`);
  console.error(`stderr: ${stderr}`);
});

function updaterule(argument){
  exec(`python3 python/twitter-api.py ${argument}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
  });
}

server.listen(process.env.PORT || 3000, () => {
  console.log('app running');
});


