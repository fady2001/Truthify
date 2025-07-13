import React, { useRef } from "react";
import PropTypes from "prop-types";
import YouTube from "react-youtube";
import { Box, Typography, Chip } from "@mui/material";
import FactItem from "./FactItem";

const VideoPlayer = ({ videoId, facts = [], onReady, onStateChange }) => {
  const playerRef = useRef(null);

  // Extract video ID from YouTube URL
  const extractVideoId = (url) => {
    const regex =
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : null;
  };

  const actualVideoId = videoId || extractVideoId(videoId);

  // YouTube player options
  const opts = {
    height: "400",
    width: "100%",
    playerVars: {
      autoplay: 0,
      controls: 1,
      rel: 0,
      showinfo: 0,
      mute: 0,
    },
  };

  // Handle player ready
  const handleReady = (event) => {
    playerRef.current = event.target;
    if (onReady) onReady(event);
  };

  // Handle player state change
  const handleStateChange = (event) => {
    if (onStateChange) onStateChange(event);
  };

  if (!actualVideoId) {
    return (
      <Box sx={{ textAlign: "center", py: 4 }}>
        <Typography variant="body1" color="error">
          Invalid YouTube URL. Please check the URL and try again.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ position: "relative", width: "100%" }}>
      {/* YouTube Player */}
      <Box sx={{ borderRadius: "10px", overflow: "hidden", mb: 2 }}>
        <YouTube
          videoId={actualVideoId}
          opts={opts}
          onReady={handleReady}
          onStateChange={handleStateChange}
          style={{ width: "100%" }}
        />
      </Box>

      {/* Facts display using FactItem components */}
      {facts.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" sx={{ mb: 2, color: "#2c3e50" }}>
            Fact Checks
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {facts.map((fact, index) => (
              <Box key={index}>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    mb: 1,
                    cursor: "pointer",
                    "&:hover .timestamp-chip": {
                      backgroundColor: "rgba(25, 118, 210, 0.1)",
                      borderColor: "#1976d2",
                    },
                  }}
                  onClick={() => {
                    if (
                      playerRef.current &&
                      playerRef.current.seekTo &&
                      fact.timestamp
                    ) {
                      playerRef.current.seekTo(fact.timestamp, true);
                    }
                  }}
                >
                  <Chip
                    className="timestamp-chip"
                    label={`${Math.floor(fact.timestamp / 60)}:${String(
                      Math.floor(fact.timestamp % 60)
                    ).padStart(2, "0")}`}
                    size="small"
                    variant="outlined"
                    sx={{
                      fontWeight: "bold",
                      transition: "all 0.2s ease",
                    }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    Click to jump to this moment
                  </Typography>
                </Box>
                <FactItem fact={fact} index={index} />
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
};

VideoPlayer.propTypes = {
  videoId: PropTypes.string.isRequired,
  facts: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.number.isRequired,
      duration: PropTypes.number,
      claim: PropTypes.string.isRequired,
      status: PropTypes.string.isRequired,
      explanation: PropTypes.string.isRequired,
      confidence: PropTypes.number,
    })
  ),
  onReady: PropTypes.func,
  onStateChange: PropTypes.func,
};

export default VideoPlayer;
