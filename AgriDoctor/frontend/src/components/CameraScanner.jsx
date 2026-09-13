import { useEffect, useRef, useState } from 'react';

export default function CameraScanner({ onCapture }) {
  const videoRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamRef = useRef(null);
  const [error, setError] = useState('');
  const [streaming, setStreaming] = useState(false);

  useEffect(() => () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
  }, []);

  const startCamera = async () => {
    setError('');
    if (!navigator.mediaDevices?.getUserMedia) {
      setError('Camera access requires HTTPS and a supported browser. Choose an image file instead.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setStreaming(true);
      }
    } catch (err) {
      setStreaming(false);
      setError('Camera permission was denied or no camera is available. Choose an image file instead.');
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) onCapture(file);
  };

  const handleCapture = () => {
    const video = videoRef.current;
    if (!video || !video.videoWidth) {
      setError('Start the camera before capturing an image.');
      return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (blob) onCapture(new File([blob], 'leaf-capture.jpg', { type: 'image/jpeg' }));
    }, 'image/jpeg', 0.9);
  };

  return (
    <div className="camera-box">
      <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
      {error && <p className="error-box">{error}</p>}
      <div className="camera-actions">
        <button className="secondary-button" type="button" onClick={startCamera} disabled={streaming}>
          {streaming ? 'Camera ready' : 'Start camera'}
        </button>
        <button className="primary-button" type="button" onClick={handleCapture} disabled={!streaming}>
          Capture image
        </button>
        <button className="ghost-button" type="button" onClick={() => fileInputRef.current?.click()}>
          Choose image
        </button>
      </div>
      <input ref={fileInputRef} type="file" accept="image/*" capture="environment" onChange={handleFileChange} hidden />
    </div>
  );
}
