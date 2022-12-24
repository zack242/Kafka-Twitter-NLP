const ejs = require('ejs');
var kafka = require('kafka-node')
var express     = require('express');
var app         = require('express')();
var server      = require('http').createServer(app);
var io          = require('socket.io')(server);
const multer = require('multer');

app.set('view engine', 'ejs');
app.get('/', function(req, res) {
    res.render('home');
});

io.on('connection', function(socket) {
    console.log('a user connected');
    socket.on('chat message', function(msg){
        console.log('message: ' + msg);
      });
});

// Set up multer to handle the file upload
const upload = multer({ dest: 'uploads/' });

// Set up the route to handle the file upload
app.post('/upload', upload.single('image'), (req, res) => {
  // The file is saved to the `uploads` directory
  console.log(req.file);
  res.sendStatus(200);
});


Consumer = kafka.Consumer,
client = new kafka.KafkaClient("localhost:9092"),
consumer = new Consumer(client,[{ topic: 'rawTwitter', partition: 0, offset: 0 }],{ fromOffset: false });

consumer.on('message', function (message){
       // io.emit('message', message.value);
    });

             
consumer.on('error', function (err) {
        console.log('ERROR: ' + err.toString());});

server.listen(process.env.PORT || 3000, function(){
    console.log('app running');
});


