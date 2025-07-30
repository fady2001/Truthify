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
export const processYouTube = async (url, setters, openSnackbar) => {
  const {
    setVideoId,
    setShowVideoPlayer,
    setShowResults,
    setLoading,
    setResults,
  } = setters;

  const validation = validateYouTubeInput(url);
  if (!validation.isValid) {
    openSnackbar(validation.message, "error");
    return;
  }

  const videoId = extractVideoId(url);
  setVideoId(videoId);
  setShowVideoPlayer(true);
  setShowResults(true);
  setLoading(true);

  openSnackbar("Processing YouTube video...", "info");

  try {
    // Simulate API delay
    setTimeout(() => {
      const dummyResult = generateYouTubeData();
      setResults(dummyResult);
      setLoading(false);
      openSnackbar("YouTube video processed successfully!", "success");
    }, 2000);
  } catch (error) {
    console.error("YouTube processing error:", error);
    setLoading(false);
    openSnackbar("Failed to process YouTube video. Please try again.", "error");
  }
};

export const processText = async (text, setters, openSnackbar) => {
  const { setShowResults, setLoading, setResults } = setters;

  const validation = validateTextInput(text);
  if (!validation.isValid) {
    openSnackbar(validation.message, "error");
    return;
  }

  setShowResults(true);
  setLoading(true);

  openSnackbar("Analyzing text content...", "info");

  try {
    // Simulate API delay
    setTimeout(() => {
      const dummyResult = generateTextData();
      setResults(dummyResult);
      setLoading(false);
      openSnackbar("Text analysis completed successfully!", "success");
    }, 1500);
  } catch (error) {
    console.error("Text processing error:", error);
    setLoading(false);
    openSnackbar("Failed to analyze text. Please try again.", "error");
  }
};

export const processFile = async (file, setters, openSnackbar) => {
  const { setShowResults, setLoading, setResults } = setters;

  const validation = validateFileInput(file);
  if (!validation.isValid) {
    openSnackbar(validation.message, "error");
    return;
  }

  setShowResults(true);
  setLoading(true);

  openSnackbar(`Processing file: ${file.name}...`, "info");

  try {
    // Simulate API delay
    setTimeout(() => {
      const dummyResult = generateFileData();
      setResults(dummyResult);
      setLoading(false);
      openSnackbar("File processed successfully!", "success");
    }, 2500);
  } catch (error) {
    console.error("File processing error:", error);
    setLoading(false);
    openSnackbar("Failed to process file. Please try again.", "error");
  }
};
