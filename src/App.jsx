import React from "react";
import { Box, Tabs, Tab, Button, Tooltip } from "@mui/material";
import {
  YouTube,
  Keyboard,
  CloudUpload,
  PictureAsPdf,
} from "@mui/icons-material";
import { ThemeProvider } from "@mui/material/styles";

import Header from "./components/Header";
import TabPanel from "./components/TabPanel";
import YouTubeTab from "./components/YouTubeTab";
import TextTab from "./components/TextTab";
import FileTab from "./components/FileTab";
import ResultsSection from "./components/ResultsSection";
import VideoPlayer from "./components/VideoPlayer";

import { theme, StyledContainer, MainPaper } from "./theme/theme";
import { useAppState } from "./hooks/useAppState";
import {
  processYouTube,
  processText,
  processFile,
} from "./services/processingService";
import { exportResultsToPDF } from "./utils/pdfExport";

function App() {
  const {
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
    setYoutubeUrl,
    setTextInput,
    setResults,
    setLoading,
    setShowResults,
    setShowVideoPlayer,
    setVideoId,
    // Handlers
    handleTabChange,
    handleFileSelect,
  } = useAppState();

  // Create setters object for processing services
  const setters = {
    setVideoId,
    setShowVideoPlayer,
    setShowResults,
    setLoading,
    setResults,
  };

  // Processing handlers using the modular services
  const handleProcessYouTube = () => processYouTube(youtubeUrl, setters);
  const handleProcessText = () => processText(textInput, setters);
  const handleProcessFile = () => processFile(selectedFile, setters);

  // PDF export handler
  const handleExportToPDF = () => exportResultsToPDF(results);

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}
      >
        <StyledContainer maxWidth="lg">
          <Header />
          {/* Main Content */}
          <MainPaper elevation={3}>
            {/* Input Tabs */}
            <Box borderBottom={2} borderColor={"#ecf0f1"} display={"flex"}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                variant="scrollable"
                sx={{
                  "& .MuiTab-root": {
                    fontSize: "1rem",
                    textTransform: "none",
                    color: "#7f8c8d",
                    minWidth: "fit-content",
                    paddingTop: "0px",
                    paddingBottom: "0px",
                  },
                  "& .Mui-selected": {
                    color: "#3498db !important",
                  },
                  "& .MuiTabs-indicator": {
                    backgroundColor: "#3498db",
                    height: "3px",
                  },
                }}
              >
                <Tab
                  icon={<YouTube />}
                  label="YouTube Link"
                  iconPosition="start"
                  disableRipple
                />
                <Tab
                  icon={<Keyboard />}
                  label="Text Input"
                  iconPosition="start"
                  disableRipple
                />
                <Tab
                  icon={<CloudUpload />}
                  label="Upload File"
                  iconPosition="start"
                  disableRipple
                />
              </Tabs>
            </Box>

            {/* Tab Panels */}
            <TabPanel value={tabValue} index={0}>
              <YouTubeTab
                youtubeUrl={youtubeUrl}
                setYoutubeUrl={setYoutubeUrl}
                onAnalyze={handleProcessYouTube}
              />

              {/* Video Player with timestamp-based facts */}
              {showVideoPlayer && videoId && (
                <Box sx={{ mt: 4 }}>
                  <VideoPlayer
                    videoId={videoId}
                    facts={results?.facts || []}
                    onReady={(event) => {
                      console.log("YouTube player ready:", event);
                    }}
                    onStateChange={(event) => {
                      console.log("YouTube player state changed:", event);
                    }}
                  />
                </Box>
              )}
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <TextTab
                textInput={textInput}
                setTextInput={setTextInput}
                onAnalyze={handleProcessText}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <FileTab
                selectedFile={selectedFile}
                onFileSelect={handleFileSelect}
                onAnalyze={handleProcessFile}
              />
            </TabPanel>

            {/* Results Section - Only show for non-YouTube tabs or when no video player */}
            {(tabValue !== 0 || !showVideoPlayer) && (
              <ResultsSection
                showResults={showResults}
                loading={loading}
                results={results}
              />
            )}

            {/* Export Button - Only show when results are available */}
            {results && (
              <Box sx={{ mt: 2, display: "flex", justifyContent: "flex-end" }}>
                <Tooltip title="Export results to PDF" arrow>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleExportToPDF}
                    startIcon={<PictureAsPdf />}
                    sx={{ borderRadius: 2 }}
                  >
                    Export to PDF
                  </Button>
                </Tooltip>
              </Box>
            )}
          </MainPaper>
        </StyledContainer>
      </Box>
    </ThemeProvider>
  );
}

export default App;
