// YouTube utility functions
export const isValidYouTubeUrl = (url) => {
  const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
  return youtubeRegex.test(url);
};

export const extractVideoId = (url) => {
  const regex =
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/;
  const match = url.match(regex);
  return match ? match[1] : null;
};

// Validation functions
export const validateYouTubeInput = (url) => {
  if (!url) {
    return { isValid: false, message: "Please enter a YouTube URL" };
  }
  if (!isValidYouTubeUrl(url)) {
    return { isValid: false, message: "Please enter a valid YouTube URL" };
  }
  const videoId = extractVideoId(url);
  if (!videoId) {
    return { isValid: false, message: "Could not extract video ID from URL" };
  }
  return { isValid: true, videoId };
};

export const validateTextInput = (text) => {
  if (!text.trim()) {
    return { isValid: false, message: "Please enter some text to fact-check" };
  }
  return { isValid: true };
};

export const validateFileInput = (file) => {
  if (!file) {
    return { isValid: false, message: "Please select a file" };
  }
  return { isValid: true };
};
