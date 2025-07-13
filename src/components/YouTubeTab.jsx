import React from "react";
import PropTypes from "prop-types";
import { Box, Typography, TextField } from "@mui/material";
import { PlayArrow } from "@mui/icons-material";
import { StyledButton } from "../theme/theme";

const YouTubeTab = ({ youtubeUrl, setYoutubeUrl, onAnalyze }) => {
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
        onChange={(e) => setYoutubeUrl(e.target.value)}
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
        onClick={onAnalyze}
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
