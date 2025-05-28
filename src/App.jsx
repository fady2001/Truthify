import React, { useState } from "react";
import { Box, Tabs, Tab } from "@mui/material";
import { YouTube, Keyboard, CloudUpload } from "@mui/icons-material";
import { ThemeProvider } from "@mui/material/styles";

// Import components
import Header from "./components/Header";
import TabPanel from "./components/TabPanel";
import YouTubeTab from "./components/YouTubeTab";
import TextTab from "./components/TextTab";
import FileTab from "./components/FileTab";
import ResultsSection from "./components/ResultsSection";

// Import theme and styled components
import { theme, StyledContainer, MainPaper } from "./theme/theme";

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [textInput, setTextInput] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
  };

  const isValidYouTubeUrl = (url) => {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    return youtubeRegex.test(url);
  };

  const processYouTube = async () => {
    if (!youtubeUrl) {
      alert("Please enter a YouTube URL");
      return;
    }

    if (!isValidYouTubeUrl(youtubeUrl)) {
      alert("Please enter a valid YouTube URL");
      return;
    }

    setShowResults(true);
    setLoading(true);

    try {
      // Replace with your actual API endpoint
      const response = await fetch("/api/fact-check/youtube", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: youtubeUrl }),
      });

      const result = await response.json();
      setResults(result);
    } catch (error) {
      setResults({ error: "Error processing YouTube video: " + error.message });
    } finally {
      setLoading(false);
    }
  };

  const processText = async () => {
    if (!textInput.trim()) {
      alert("Please enter some text to fact-check");
      return;
    }

    setShowResults(true);
    setLoading(true);

    try {
      // Replace with your actual API endpoint
      const response = await fetch("/api/fact-check/text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: textInput }),
      });

      const result = await response.json();
      setResults(result);
    } catch (error) {
      setResults({ error: "Error processing text: " + error.message });
    } finally {
      setLoading(false);
    }
  };

  const processFile = async () => {
    if (!selectedFile) {
      alert("Please select a file");
      return;
    }

    setShowResults(true);
    setLoading(true);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      // Replace with your actual API endpoint
      const response = await fetch("/api/fact-check/file", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      setResults(result);
    } catch (error) {
      setResults({ error: "Error processing file: " + error.message });
    } finally {
      setLoading(false);
    }
  };

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
            <Box sx={{ borderBottom: 2, borderColor: "#ecf0f1" }}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                variant="fullWidth"
                sx={{
                  "& .MuiTab-root": {
                    fontSize: "1rem",
                    textTransform: "none",
                    color: "#7f8c8d",
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
                <Tab icon={<YouTube />} label="YouTube Link" />
                <Tab icon={<Keyboard />} label="Text Input" />
                <Tab icon={<CloudUpload />} label="Upload File" />
              </Tabs>
            </Box>

            {/* Tab Panels */}
            <TabPanel value={tabValue} index={0}>
              <YouTubeTab
                youtubeUrl={youtubeUrl}
                setYoutubeUrl={setYoutubeUrl}
                onAnalyze={processYouTube}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <TextTab
                textInput={textInput}
                setTextInput={setTextInput}
                onAnalyze={processText}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <FileTab
                selectedFile={selectedFile}
                onFileSelect={handleFileSelect}
                onAnalyze={processFile}
              />
            </TabPanel>

            {/* Results Section */}
            <ResultsSection
              showResults={showResults}
              loading={loading}
              results={results}
            />
          </MainPaper>
        </StyledContainer>
      </Box>
    </ThemeProvider>
  );
}

export default App;
