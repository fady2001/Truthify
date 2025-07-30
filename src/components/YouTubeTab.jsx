import React from "react";
import PropTypes from "prop-types";
import { Box, Typography, TextField } from "@mui/material";
import { PlayArrow } from "@mui/icons-material";
import { StyledButton } from "../theme/theme";
import { useSnackbar } from "../contexts/snackbar";

const YouTubeTab = ({ youtubeUrl, setYoutubeUrl, onAnalyze }) => {
  const { openSnackbar } = useSnackbar();

  const handleUrlChange = (e) => {
    const url = e.target.value;
    setYoutubeUrl(url);

    // Basic URL validation feedback
    if (url && !url.includes("youtube.com") && !url.includes("youtu.be")) {
      openSnackbar("Please enter a valid YouTube URL", "warning");
    }
  };

  const handleAnalyze = () => {
    if (!youtubeUrl.trim()) {
      openSnackbar("Please enter a YouTube URL", "warning");
      return;
    }
    onAnalyze();
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, color: "#2c3e50" }}>
        Enter YouTube URL:
      </Typography>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="https://www.youtube.com/watch?v=..."
        value={youtubeUrl}
        onChange={handleUrlChange}
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: "10px",
            fontSize: "1rem",
          },
        }}
      />
      <StyledButton
        variant="contained"
        startIcon={<PlayArrow />}
        onClick={handleAnalyze}
        disabled={!youtubeUrl}
        sx={{ alignSelf: "flex-start" }}
      >
        Analyze Video
      </StyledButton>
    </Box>
  );
};

YouTubeTab.propTypes = {
  youtubeUrl: PropTypes.string.isRequired,
  setYoutubeUrl: PropTypes.func.isRequired,
  onAnalyze: PropTypes.func.isRequired,
};

export default YouTubeTab;
