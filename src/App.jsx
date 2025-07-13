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
import VideoPlayer from "./components/VideoPlayer";

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

  const isValidYouTubeUrl = (url) => {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    return youtubeRegex.test(url);
  };

  // Extract video ID from YouTube URL
  const extractVideoId = (url) => {
    const regex =
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : null;
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

    const extractedVideoId = extractVideoId(youtubeUrl);
    if (!extractedVideoId) {
      alert("Could not extract video ID from URL");
      return;
    }

    setVideoId(extractedVideoId);
    setShowVideoPlayer(true);
    setShowResults(true);
    setLoading(true);

    // Simulate API delay
    setTimeout(() => {
      // Dummy data for YouTube analysis with timestamps
      const dummyResult = {
        facts: [
          {
            timestamp: 30, // 0:30
            duration: 8,
            claim: "Climate change is caused by human activities",
            status: "verified",
            explanation:
              "This claim is supported by overwhelming scientific evidence. The IPCC and numerous peer-reviewed studies confirm that human activities are the primary driver of recent climate change.",
            confidence: 95,
            sources: [
              {
                title: "IPCC Sixth Assessment Report",
                url: "https://www.ipcc.ch/report/ar6/wg1/",
              },
            ],
          },
          {
            timestamp: 120, // 2:00
            duration: 10,
            claim: "Electric vehicles produce zero emissions",
            status: "false",
            explanation:
              "While EVs produce no direct emissions, they may have indirect emissions from electricity generation and battery manufacturing. However, they are still significantly cleaner overall.",
            confidence: 82,
            sources: [
              {
                title: "EPA Electric Vehicle Analysis",
                url: "https://www.epa.gov/greenvehicles/electric-vehicle-myths",
              },
            ],
          },
          {
            timestamp: 200, // 3:20
            duration: 12,
            claim: "Renewable energy costs are decreasing rapidly",
            status: "verified",
            explanation:
              "Multiple studies show that renewable energy costs have decreased significantly over the past decade. Solar and wind are now among the cheapest electricity sources.",
            confidence: 91,
            sources: [
              {
                title: "IRENA Global Energy Report",
                url: "https://www.irena.org/publications/2023/Jun/Global-Energy-Transformation",
              },
            ],
          },
          {
            timestamp: 300, // 5:00
            duration: 15,
            claim: "AI will replace all human jobs",
            status: "unknown",
            explanation:
              "While AI is advancing rapidly, the extent to which it will replace human jobs is debated. Many experts suggest AI will transform rather than completely replace most jobs.",
            confidence: 45,
            sources: [
              {
                title: "MIT Technology Review: AI and Jobs",
                url: "https://www.technologyreview.com/topic/artificial-intelligence/",
              },
            ],
          },
        ],
      };

      setResults(dummyResult);
      setLoading(false);
    }, 2000);
  };

  const processText = async () => {
    if (!textInput.trim()) {
      alert("Please enter some text to fact-check");
      return;
    }

    setShowResults(true);
    setLoading(true);

    // Simulate API delay
    setTimeout(() => {
      // Dummy data for text analysis
      const dummyResult = {
        facts: [
          {
            claim: "The Great Wall of China is visible from space",
            status: "false",
            explanation:
              "This is a common myth. The Great Wall of China is not visible from space with the naked eye. This misconception has been debunked by astronauts and space agencies multiple times.",
            confidence: 92,
            sources: [
              {
                title: "NASA Space Myths Debunked",
                url: "https://www.nasa.gov/audience/forstudents/k-4/stories/nasa-knows/what-is-the-great-wall-of-china-k4.html",
              },
              {
                title: "ESA Astronaut Reports",
                url: "https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Research/Great_Wall_of_China",
              },
              {
                title: "Snopes Great Wall Fact Check",
                url: "https://www.snopes.com/fact-check/great-wall-of-china-visible-from-space/",
              },
            ],
          },
          {
            claim: "Drinking 8 glasses of water daily is necessary for health",
            status: "unknown",
            explanation:
              "While staying hydrated is important, the '8 glasses per day' rule lacks strong scientific backing. Water needs vary based on individual factors like activity level, climate, and overall health.",
            confidence: 65,
            sources: [
              {
                title: "Mayo Clinic: Water Intake Recommendations",
                url: "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256",
              },
              {
                title: "Harvard Health: How Much Water Should You Drink?",
                url: "https://www.health.harvard.edu/staying-healthy/how-much-water-should-you-drink",
              },
            ],
          },
          {
            claim: "Artificial intelligence is advancing rapidly",
            status: "verified",
            explanation:
              "This statement is accurate. AI technology has shown exponential growth in recent years, with significant breakthroughs in machine learning, natural language processing, and computer vision.",
            confidence: 94,
            sources: [
              {
                title: "MIT Technology Review: AI Progress",
                url: "https://www.technologyreview.com/topic/artificial-intelligence/",
              },
              {
                title: "Nature AI Research",
                url: "https://www.nature.com/natmachintell/",
              },
              {
                title: "Stanford AI Index Report 2024",
                url: "https://aiindex.stanford.edu/report/",
              },
            ],
          },
        ],
      };

      setResults(dummyResult);
      setLoading(false);
    }, 1500);
  };

  const processFile = async () => {
    if (!selectedFile) {
      alert("Please select a file");
      return;
    }

    setShowResults(true);
    setLoading(true);

    // Simulate API delay
    setTimeout(() => {
      // Dummy data for file analysis
      const dummyResult = {
        facts: [
          {
            claim: "Electric vehicles have zero emissions",
            status: "false",
            explanation:
              "While electric vehicles produce no direct emissions, they may have indirect emissions from electricity generation and battery manufacturing. However, they are still significantly cleaner than conventional vehicles overall.",
            confidence: 78,
            sources: [
              {
                title: "EPA Electric Vehicle Emissions Report",
                url: "https://www.epa.gov/greenvehicles/electric-vehicle-myths",
              },
              {
                title: "Union of Concerned Scientists EV Analysis",
                url: "https://www.ucsusa.org/clean-vehicles/electric-vehicles",
              },
              {
                title: "Carbon Brief: Electric Car Life Cycle",
                url: "https://www.carbonbrief.org/factcheck-how-electric-vehicles-help-to-tackle-climate-change/",
              },
            ],
          },
          {
            claim: "Exercise improves mental health",
            status: "verified",
            explanation:
              "Numerous scientific studies have demonstrated that regular physical exercise has positive effects on mental health, including reducing symptoms of depression and anxiety while improving mood and cognitive function.",
            confidence: 91,
            sources: [
              {
                title:
                  "American Psychological Association: Exercise & Mental Health",
                url: "https://www.apa.org/topics/exercise-fitness/mental-health",
              },
              {
                title: "Journal of Clinical Psychiatry Study",
                url: "https://www.psychiatrist.com/jcp/exercise-depression-anxiety/",
              },
              {
                title: "Harvard Medical School: Exercise & Depression",
                url: "https://www.health.harvard.edu/mind-and-mood/exercise-is-an-all-natural-treatment-to-fight-depression",
              },
            ],
          },
          {
            claim: "Quantum computers will replace all traditional computers",
            status: "unknown",
            explanation:
              "While quantum computers show promise for specific applications, it's unclear if or when they might replace traditional computers entirely. Current quantum computers are specialized tools rather than general-purpose replacements.",
            confidence: 45,
            sources: [
              {
                title: "IBM Quantum Computing Overview",
                url: "https://www.ibm.com/quantum-computing/",
              },
              {
                title: "MIT Technology Review: Quantum Computing Reality",
                url: "https://www.technologyreview.com/topic/computing/quantum-computing/",
              },
              {
                title: "Nature Quantum Information",
                url: "https://www.nature.com/npjqi/",
              },
            ],
          },
          {
            claim: "Social media usage is linked to mental health issues",
            status: "verified",
            explanation:
              "Research has shown correlations between excessive social media use and various mental health concerns, including increased rates of anxiety, depression, and body image issues, particularly among adolescents.",
            confidence: 82,
            sources: [
              {
                title:
                  "American Academy of Pediatrics: Social Media Guidelines",
                url: "https://www.aap.org/en/patient-care/media-and-children/social-media/",
              },
              {
                title: "Journal of Social Media Research",
                url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6214874/",
              },
              {
                title: "Pew Research: Social Media & Mental Health",
                url: "https://www.pewresearch.org/internet/2022/08/10/teens-social-media-and-technology-2022/",
              },
            ],
          },
        ],
      };

      setResults(dummyResult);
      setLoading(false);
    }, 2500);
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
                onAnalyze={processYouTube}
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

            {/* Results Section - Only show for non-YouTube tabs or when no video player */}
            {(tabValue !== 0 || !showVideoPlayer) && (
              <ResultsSection
                showResults={showResults}
                loading={loading}
                results={results}
              />
            )}
          </MainPaper>
        </StyledContainer>
      </Box>
    </ThemeProvider>
  );
}

export default App;
