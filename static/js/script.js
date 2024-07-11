function resizeTextarea(textarea) {
    console.log('Resizing textarea');
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

function sendData() {
    console.log('sendData function called');
    var songs = document.getElementById('songs').value;
    var album = document.getElementById('album').value;

    var data = {
        songs: songs,
        album: album
    };

    var jsonData = JSON.stringify(data);

    console.log('Data to be sent:', jsonData);

    return false;  // Prevent form submission