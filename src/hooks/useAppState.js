import { useState } from "react";

export const useAppState = () => {
  const [tabValue, setTabValue] = useState(0);
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [textInput, setTextInput] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [showVideoPlayer, setShowVideoPlayer] = useState(false);
  const [videoId, setVideoId] = useState("");

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    // Reset video player when switching tabs
    setShowVideoPlayer(false);
    setVideoId("");
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
  };

  const resetState = () => {
    setResults(null);
    setLoading(false);
    setShowResults(false);
    setShowVideoPlayer(false);
    setVideoId("");
  };

  return {
    // State
    tabValue,
    youtubeUrl,
    textInput,
    selectedFile,
    results,
    loading,
    showResults,
    showVideoPlayer,
    videoId,
    // Setters
    setTabValue,
    setYoutubeUrl,
    setTextInput,
    setSelectedFile,
    setResults,
    setLoading,
    setShowResults,
    setShowVideoPlayer,
    setVideoId,
    // Handlers
    handleTabChange,
    handleFileSelect,
    resetState,
  };
};
