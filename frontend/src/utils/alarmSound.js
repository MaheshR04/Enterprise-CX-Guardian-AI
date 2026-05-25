export function playDangerAlarm() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;

    if (!AudioContext) {
      return;
    }

    const audioContext = new AudioContext();
    const gainNode = audioContext.createGain();
    gainNode.gain.setValueAtTime(0.001, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.18, audioContext.currentTime + 0.02);
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.75);
    gainNode.connect(audioContext.destination);

    [0, 0.22, 0.44].forEach((offset) => {
      const oscillator = audioContext.createOscillator();
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(880, audioContext.currentTime + offset);
      oscillator.connect(gainNode);
      oscillator.start(audioContext.currentTime + offset);
      oscillator.stop(audioContext.currentTime + offset + 0.14);
    });

    window.setTimeout(() => audioContext.close(), 1000);
  } catch {
    // Browsers may block audio until the user interacts with the page.
  }
}
