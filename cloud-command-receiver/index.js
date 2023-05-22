//We use these to serve our app and access the local API, respectively
var restify = require('restify');
var axios = require('axios');

var app = restify.createServer();

app.use(restify.plugins.bodyParser());
app.use(restify.plugins.queryParser());

const LISTENING_PORT = process.env.LISTENING_PORT;

var videon_ip = process.env.HOST_IP_ADDRESS;

// Sample list of objects
let messages = [
    { "id": 1, "message": 'First message' }
  ];

//This endpoint will respond with all messages stored in the container
app.get('/cloud-command', function(req, res, next) {
    res.send(200, { messages });
    next();
    return;
});

//This endpoint will create our example object and store the included information, returning that information
app.post('/cloud-command', function(req, res, next) {
    let id = messages[messages.length - 1].id + 1;
    let newMessage = { "id": id, "message": '(New) Message #' + id };
    messages.push(newMessage);
    res.send(200, newMessage);
    next();
    return;
});

//This endpoint will update the specified message with a new message and return that updated message
app.put('/cloud-command', function(req, res, next) {
    let id = req.body.id;
    let updatedMessage = req.body.message; // Assuming the request body contains the updated message data

    // Find the message with the specified ID
    let index = messages.findIndex(message => message.id === id);

    if (index !== -1) {
        // Update the message with the new data
        messages[index].message = updatedMessage;
        res.send(200, messages[index]);
    } else {
        res.send(500, "Id #" + id + " not found \n" + JSON.stringify(req.body));
    }
    next();
    return;
});

// This endpoint will simply respond with a static message to confirm this the message was deleted
app.del('/cloud-command/:id', function(req, res, next) {
    let id = req.params.id.toString();
    // Find the message with the specified ID
    let index = messages.findIndex(message => message.id.toString() === id);

    if (index !== -1) {
        // Update the message with the new data
        messages.splice(index, 1);
        res.send(200, "Message with id of " + id + " deleted");
    } else {
        res.send(500, "Id #" + id + " not found. Index = " + index);
    }
    next();
    return;
});

app.listen(LISTENING_PORT, function() {
    console.log("Listening on port " + LISTENING_PORT);
});