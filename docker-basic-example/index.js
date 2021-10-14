//We use these to serve our app and access the local API, respectively
var restify = require('restify');
var axios = require('axios');

var app = restify.createServer();

app.use(restify.plugins.bodyParser());
app.use(restify.plugins.queryParser());

const LISTENING_PORT = process.env.LISTENING_PORT;

var videon_ip = process.env.HOST_IP_ADDRESS;
var videon_baseurl = "http://" + videon_ip +":2020";

//This endpoint will simply respond with a static message to confirm this server is running
app.get('/docker-test', function(req, res, next) {
    res.send(200, "The call is coming from inside your Docker container!");
    next();
    return;
});

//We'll call the LiveEdge Compute API to find out whether we have inputs and outputs enabled
app.get('/input-detected', async function(req, res, next){
    let audio = 'No audio input channel detected';
    let video = 'No video input channel detected';

    let in_channels = await axios.get(videon_baseurl + '/v2/in_channels');

    for(n=0; n < in_channels.data.in_channels.length; n++) {
        let channel = await axios.get(videon_baseurl + "/v2/in_channels/" + in_channels.data.in_channels[n].in_channel_id);

        if(channel.data.audio_input.detected === true) {
            audio = 'Found an audio input channel - type: ' + channel.data.audio_input.value;
        }

        if(!(channel.data.video_input.detected_format.value == 'FORMAT_UNDEFINED')) {
            video = 'Found a video input channel - type: ' + channel.data.video_input.value;
        }
    }

    res.send(200, "Video Input: " + video + "; Audio Input: " + audio);

});

app.listen(LISTENING_PORT, function() {
    console.log("Listening on port " + LISTENING_PORT);
});