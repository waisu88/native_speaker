let mediaRecorder;
let audioChunks = [];

navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = event => {
      audioChunks.push(event.data);
    };
  });

function startRecording() {
  audioChunks = [];
  mediaRecorder.start();
}

function stopRecording() {
  mediaRecorder.stop();
  const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
  // Prześlij audioBlob na serwer
}