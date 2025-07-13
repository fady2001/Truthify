import {
  validateYouTubeInput,
  validateTextInput,
  validateFileInput,
  extractVideoId,
} from "../utils/validators.js";
import {
  generateYouTubeData,
  generateTextData,
  generateFileData,
} from "./dummyData.js";

// Processing service for different content types
export const processYouTube = async (url, setters) => {
  const {
    setVideoId,
    setShowVideoPlayer,
    setShowResults,
    setLoading,
    setResults,
  } = setters;

  const validation = validateYouTubeInput(url);
  if (!validation.isValid) {
    alert(validation.message);
    return;
  }

  const videoId = extractVideoId(url);
  setVideoId(videoId);
  setShowVideoPlayer(true);
  setShowResults(true);
  setLoading(true);

  // Simulate API delay
  setTimeout(() => {
    const dummyResult = generateYouTubeData();
    setResults(dummyResult);
    setLoading(false);
  }, 2000);
};

export const processText = async (text, setters) => {
  const { setShowResults, setLoading, setResults } = setters;

  const validation = validateTextInput(text);
  if (!validation.isValid) {
    alert(validation.message);
    return;
  }

  setShowResults(true);
  setLoading(true);

  // Simulate API delay
  setTimeout(() => {
    const dummyResult = generateTextData();
    setResults(dummyResult);
    setLoading(false);
  }, 1500);
};

export const processFile = async (file, setters) => {
  const { setShowResults, setLoading, setResults } = setters;

  const validation = validateFileInput(file);
  if (!validation.isValid) {
    alert(validation.message);
    return;
  }

  setShowResults(true);
  setLoading(true);

  // Simulate API delay
  setTimeout(() => {
    const dummyResult = generateFileData();
    setResults(dummyResult);
    setLoading(false);
  }, 2500);
};
