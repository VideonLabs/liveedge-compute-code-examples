const express = require('express');
const cors = require('cors');
const serveStatic = require('serve-static')
const axios = require('axios');
const sharp = require('sharp'); // Simple and fast image processing library
const { RekognitionClient, DetectLabelsCommand } = require("@aws-sdk/client-rekognition"); // AWS SDK

// Grab these values from the ENV vars
const region = process.env.AWS_REGION;
const port = process.env.SERVER_PORT;

// This is the location of the JPEG preview images LiveEdge Compute creates when streaming.
// We're accessing them via HTTP, though we could just as easily map the volume to the 
// location of these images on the box.
const imgLoc = 'http://172.17.0.1/live/CurrentThumb.jpg';

const app = express()
app.use(cors());

const client = new RekognitionClient({ region: region });

// Handles the flow of the application
async function processImage(image_name) {
    try {
        
        //1. Grab the most recent image
        let response = await axios.get(image_name,  { responseType: 'arraybuffer' })
        let bitmap = Buffer.from(response.data, "utf-8")
        
        //2. Send it to AWS Rekognition
        var res = await getImageLabels(bitmap);

        //3. Pass the image into sharp and add the bounding boxes
        return drawBoundingBoxes(bitmap, res);

    } catch(e) {
        console.log("ERROR: " + e.message);
        return false;
    }
}

// Calls AWS Rekognition with the given image as a buffer and returns the results.
async function getImageLabels(bitmap) {
    var params = {
        "Image": { 
           "Bytes": bitmap
        },
        "MaxLabels": 50,
        "MinConfidence": 60
    }

    var command = new DetectLabelsCommand(params);
    try {
        var response = await client.send(command);
    } catch(e) {
        console.log("ERROR: " + e.message);
    }

    return response;
}

// Creates bounding boxes with labels using SVG and overlays on the original image
async function drawBoundingBoxes(bitmap, rek) {
    let svgRectangles =[];
    let svgElementBuffer = '';

    let resImg = sharp(bitmap);
    let metadata = await resImg.metadata();
      
    //Read the response data from AWS Rekognition and create bounding boxes on the image using SVG
    for(n = 0; n < rek.Labels.length; n++) {
        // Generate a new random hex color for each label
        let boxColor = '#' + Math.floor(Math.random()*16777215).toString(16);
        
        // For each bounding box, create an SVG rect and corresponding text field
        for(i = 0; i < rek.Labels[n].Instances.length; i++) {    
            svgRectangles.push (' <rect height="' + (rek.Labels[n].Instances[i].BoundingBox.Height * metadata.height) + '" width="' + (rek.Labels[n].Instances[i].BoundingBox.Width * metadata.width) + '" x="' + (rek.Labels[n].Instances[i].BoundingBox.Left * metadata.width) + '" y="' + (rek.Labels[n].Instances[i].BoundingBox.Top * metadata.height) + '" style="fill: none; stroke: ' + boxColor + '; stroke-width: 2"/>');
            svgRectangles.push (' <text x="' + ((rek.Labels[n].Instances[i].BoundingBox.Left * metadata.width) + 5) + '" y="' + ((rek.Labels[n].Instances[i].BoundingBox.Top * metadata.height) + 15) + '" style="font: italic 13px sans-serif; fill: #FFFFFF">' + rek.Labels[n].Name + ' (' + rek.Labels[n].Instances[i].Confidence.toFixed(2) + '%)</text>');
        }
    }

    //Set up the SVG wrapper
    let svgElement = '<svg height="'+ metadata.height +'" width="'+ metadata.width +'" viewbox="0 0 '+ metadata.width +' '+ metadata.height +'" xmlns="http://www.w3.org/2000/svg">';
    svgElement += svgRectangles.join('');
    svgElement += '</svg>';

    // Convert to a buffer for sharp and composite on top of the bitmap
    svgElementBuffer = new Buffer.from(svgElement);
    let overlayImg = await resImg.composite([{input: svgElementBuffer, top:0, left:0}]).jpeg().toBuffer();

    return overlayImg;
}

/////////////////////
// Express Routing
////////////////////

app.use(serveStatic('./web', {
    setHeaders: setStaticCORS
}));

//We need to handle CORS differently for static files
function setStaticCORS(res, path) {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
}

app.get('/bounded', async function(req, res, next) {
    res.append('Content-Type', 'image/jpeg');
    res.send(await processImage(imgLoc));
});

app.listen(port, function() {
    console.log("Listening on port " + port);
});


