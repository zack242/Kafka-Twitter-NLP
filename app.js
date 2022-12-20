const ejs = require('ejs');
var kafka = require('kafka-node')
var express     = require('express');
var app         = require('express')();
var server      = require('http').createServer(app);
var io          = require('socket.io')(server);


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


Consumer = kafka.Consumer,
client = new kafka.KafkaClient("localhost:9092"),
consumer = new Consumer(client,[{ topic: 'rawTwitter', partition: 0, offset: 0 }],{ fromOffset: false });

consumer.on('message', function (message){
        console.log("send")
        io.emit('message', message.value);});
        
consumer.on('error', function (err) {
        console.log('ERROR: ' + err.toString());});

server.listen(process.env.PORT || 3000, function(){
    console.log('app running');
});


