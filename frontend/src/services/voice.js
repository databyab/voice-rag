export class VoiceSession {
  constructor(onStatusChange, onTranscript, onAnswer, onError) {
    this.onStatusChange = onStatusChange;
    this.onTranscript = onTranscript;
    this.onAnswer = onAnswer;
    this.onError = onError;
    this.ws = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.currentAudio = null;
  }

  start() {
    this.stopAudio();
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/voice/ws`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      this.onStatusChange('Listening...');
      this.startMicrophone();
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.state === 'listening') {
          this.onStatusChange('Listening...');
        } else if (data.state === 'thinking') {
          this.onStatusChange('Thinking...');
          if (data.transcript) {
            this.onTranscript(data.transcript);
          }
        } else if (data.state === 'speaking') {
          this.onStatusChange('Speaking...');
          if (data.answer) {
            this.onAnswer(data.answer, data.sources);
          }
        } else if (data.state === 'completed') {
          if (data.audio) {
            this.playAudio(data.audio);
          } else {
            this.onStatusChange('Idle');
            this.closeWebSocket();
          }
        } else if (data.state === 'error') {
          this.onError(data.message || 'Voice pipeline error');
          this.closeWebSocket();
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
        this.closeWebSocket();
      }
    };

    this.ws.onerror = (err) => {
      this.onError('WebSocket connection error');
      this.closeWebSocket();
    };

    this.ws.onclose = () => {
      this.onStatusChange('Idle');
    };
  }

  async startMicrophone() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.audioChunks = [];
      this.mediaRecorder = new MediaRecorder(stream);
      this.isRecording = true;

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        const mimeType = this.mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
          const base64Audio = reader.result.split(',')[1];
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(
              JSON.stringify({
                type: 'audio_input',
                audio: base64Audio,
              })
            );
          }
        };
      };

      this.mediaRecorder.start();
    } catch (err) {
      this.onError('Microphone access denied or unsupported browser.');
      this.closeWebSocket();
    }
  }

  stopAudio() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
  }

  stop() {
    this.stopAudio();
    if (this.mediaRecorder && this.isRecording) {
      this.isRecording = false;
      this.onStatusChange('Processing speech...');
      this.mediaRecorder.stop();
      this.mediaRecorder.stream.getTracks().forEach((track) => track.stop());
    } else {
      this.closeWebSocket();
    }
  }

  closeWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (!this.currentAudio) {
      this.onStatusChange('Idle');
    }
  }

  playAudio(base64Audio) {
    try {
      this.stopAudio();
      this.onStatusChange('Speaking...');
      
      const byteCharacters = atob(base64Audio);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'audio/mp3' });
      const audioUrl = URL.createObjectURL(blob);

      this.currentAudio = new Audio(audioUrl);
      
      this.currentAudio.onended = () => {
        this.currentAudio = null;
        this.onStatusChange('Idle');
        this.closeWebSocket();
      };

      this.currentAudio.onerror = (err) => {
        console.error('Audio playback error:', err);
        this.currentAudio = null;
        this.onStatusChange('Idle');
        this.closeWebSocket();
      };

      const playPromise = this.currentAudio.play();
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          console.error('Audio play failed (browser policy or decoding):', err);
          this.onStatusChange('Idle');
          this.closeWebSocket();
        });
      }
    } catch (err) {
      console.error('Failed to instantiate Audio response:', err);
      this.onStatusChange('Idle');
      this.closeWebSocket();
    }
  }
}

