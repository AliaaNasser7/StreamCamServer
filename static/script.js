document.addEventListener('DOMContentLoaded', () => {
    var host   = window.location.host;
    var socket = io(`wss://${host}`);
    
    window._socket = socket;
    
    var video  = document.getElementById('video');
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();

            video.addEventListener('loadedmetadata', function() {
                canvas.width  = video.videoWidth;
                canvas.height = video.videoHeight;
                console.log(`Canvas size: ${canvas.width}x${canvas.height}`);

                //frame capture every second
                setInterval(sendFrame, 1000);
            });
        })
        .catch(function(err) {
            console.error("Error accessing camera: " + err);
        });

    function sendFrame() {
        if (canvas.width === 0 || canvas.height === 0) return;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        var frame = canvas.toDataURL('image/jpeg', 0.7);
        socket.emit('video_frame', frame);
    }

    socket.on('connect',    () => console.log('WebSocket connected'));
    socket.on('disconnect', () => console.log('WebSocket disconnected'));
});





/*document.addEventListener('DOMContentLoaded', () => {
    var host = window.location.host;
    var socket = io(`wss://${host}`);
    var video = document.getElementById('video');

    // Request access to the camera
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();

            // Set up a canvas to capture frames from the video
            var canvas = document.createElement('canvas');
            var context = canvas.getContext('2d');
            canvas.width = video.width;
            canvas.height = video.height;

            // Function to capture a frame and send it to the server
            function sendFrame() {
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                var frame = canvas.toDataURL('image/jpeg');
                socket.emit('video_frame', frame);
            }

            // Send frames every 5 seconds
            setInterval(sendFrame, 5000);
        })
        .catch(function (err) {
            console.error("Error accessing camera: " + err);
        });

    socket.on('connect', function () {
        console.log("WebSocket connected");
    });

    socket.on('disconnect', function () {
        console.log("WebSocket disconnected");
    });
});*/
