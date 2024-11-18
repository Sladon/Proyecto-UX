const MP3_DIR = "/static/sounds/";

const audios = {
  dropdown: {
    audio: new Audio(MP3_DIR + "dropdown.mp3"),
    volume: 1,
  },
  error: {
    audio: new Audio(MP3_DIR + "error.mp3"),
    volume: 1,
  },
  success: {
    audio: new Audio(MP3_DIR + "success.mp3"),
    volume: 1,
  },
  hover: {
    audio: new Audio(MP3_DIR + "hover.wav"),
    volume: 1,
  },
  interact: {
    audio: new Audio(MP3_DIR + "interact.wav"),
    volume: 1,
  },
  search: {
    audio: new Audio(MP3_DIR + "search.wav"),
    volume: 1,
  },
  switchPage: {
    audio: new Audio(MP3_DIR + "switch-page.mp3"),
    volume: 1,
  },
  inicio: {
    audio: new Audio(MP3_DIR + "Inicio.mp3"),
    volume: 1,
  },
};

Object.values(audios).forEach(({ audio, volume }) => {
  audio.load();
  audio.volume = volume;
});

const playSound = (soundName) => {
  const sound = audios[soundName];
  if (sound?.audio) {
    sound.audio.currentTime = 0;
    sound.audio.volume = sound.volume;
    sound.audio.play().catch((error) => {
      console.warn(`Failed to play sound: ${soundName}`, error);
    });
  }
};
