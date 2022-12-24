const ejs = require('ejs');
const app = require('express')();
const server = require('http').createServer(app);
const io = require('socket.io')(server);
const kafka = require('kafka-node');
const fs = require('fs');
const path = require('path');

app.set('view engine', 'ejs');
app.get('/', (req, res) => {
  res.render('home');
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
const fileName = 'cloudnuage.jpg';

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
    res.setHeader('Content-Type', 'image/jpeg');
    res.send(data);
  });
});

const client = new kafka.KafkaClient('localhost:9092');
const consumer = new kafka.Consumer(
  client,
  [{ topic: 'rawTwitter', partition: 0, offset: 0 }],
  { fromOffset: false }
);

consumer.on('message', (message) => {
  // io.emit('message', message.value);
});

consumer.on('error', (err) => {
  console.log(`ERROR: ${err.toString()}`);
});

fs.watch(directory, (eventType, filename) => {
  if (eventType === 'change') {
    console.log('Event emit on tmp');
    io.emit('message', 'go');
  }
});

server.listen(process.env.PORT || 3000, () => {
  console.log('app running');
});
