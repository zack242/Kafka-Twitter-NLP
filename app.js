const ejs = require("ejs");
const express = require("express");
const app = require("express")();
const server = require("http").createServer(app);
const io = require("socket.io")(server);
const kafka = require("kafka-node");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");
var actualclass = "class0";

var NBR_TWEETS = 0;

// Set the directory path
const directory = "python/tmp";

// Set the image file name
const fileName = "wordcloud.svg";

// Set the image file path
const filePath = path.join(directory, fileName);

app.set("view engine", "ejs");
app.use(express.static(__dirname + "/public"));

app.get("/", (req, res) => {
  res.render("index");
});

app.get("/image", (req, res) => {
  // Read the image file
  fs.readFile(filePath, (err, data) => {
    if (err) {
      console.error(err);
      res.sendStatus(500);
      return;
    }
    // Set the content type and send the image data as a response
    res.setHeader("Content-Type", "image/svg+xml");
    res.send(data);
  });
});

app.get("/hbar", (req, res) => {
  // Read the image file
  path_class = path.join(directory, actualclass)
  fs.readFile(path_class+".svg", (err, data) => {
    if (err) {
      console.error(err);
      res.sendStatus(500);
      return;
    }
    // Set the content type and send the image data as a response
    res.setHeader("Content-Type", "image/svg+xml");
    res.send(data);
  });
});

app.get("/NBRTWEETS", (req, res) => {
  res.setHeader("Content-Type", "application/json");
  res.send({ nbrTweets: NBR_TWEETS });
});

app.get("/keyword", function (req, res) {
  const data = req.query.key;
  updaterule(data);
  res.json({ message: "Data received" });
});

io.on("connection", (socket) => {
  console.log("a user connected");
  socket.on("chat message", (msg) => {
    console.log(`message: ${msg}`);
  });
});

const client = new kafka.KafkaClient("localhost:9092");
const consumer = new kafka.Consumer(
  client,
  [{ topic: "rawTwitter", partition: 0, offset: 0 }],
  { fromOffset: false, autoCommit: true }
);

const client2 = new kafka.KafkaClient("localhost:9092");
const consumer_class = new kafka.Consumer(
  client2,
  [{ topic:actualclass, partition: 0, offset: 0 }],
  { fromOffset: false, autoCommit: true }
);

consumer.on("message", (message) => {
  io.emit("message", message.value);
  NBR_TWEETS++;
});

consumer.on("error", (err) => {
  console.log(`ERROR: ${err.toString()}`);
});

consumer_class.on("message", (message) => {
  io.emit("message1", message.value);
});

app.get("/class", function (req, res) {
  const data = req.query.key;
  consumer_class.removeTopics([actualclass], function (err, removed) {});
  actualclass = "class" + data;
  consumer_class.addTopics([actualclass], function (err, added) {});
  res.json({ message: "Data received" });
});

fs.watch(directory, (eventType, filename) => {
  if (eventType === "change") {
    io.emit("message", "go");
  }
});
updaterule("")
function updaterule(argument) {
  exec(`python3 python/twitter-api.py ${argument}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec1 error: ${error}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
  });
}

exec(`python3 python/treadingword.py`, (error, stdout, stderr) => {
  if (error) {
    console.error(`exec3 error: ${error}`);
    return;
  }
  console.log(`stdout: ${stdout}`);
  console.error(`stderr: ${stderr}`);
});

exec(`python3 python/TFIDF_online.py`, (error, stdout, stderr) => {
  if (error) {
    console.error(`exec4 error: ${error}`);
    return;
  }
  console.log(`stdout: ${stdout}`);
  console.error(`stderr: ${stderr}`);
});

exec(`python3 python/model_enligne.py`, (error, stdout, stderr) => {
  if (error) {
    console.error(`exec2 error: ${error}`);
    return;
  }
  console.log(`stdout: ${stdout}`);
  console.error(`stderr: ${stderr}`);
});

server.listen(process.env.PORT || 3000, () => {
  console.log("app running");
});
