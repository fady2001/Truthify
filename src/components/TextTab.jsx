import React from "react";
import PropTypes from "prop-types";
import { Box, Typography, TextField } from "@mui/material";
import { Check } from "@mui/icons-material";
import { StyledButton } from "../theme/theme";

const TextTab = ({ textInput, setTextInput, onAnalyze }) => {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, color: "#2c3e50" }}>
        Enter text to fact-check:
      </Typography>
      <TextField
        fullWidth
        multiline
        rows={6}
        variant="outlined"
        placeholder="Paste your text here..."
        value={textInput}
        onChange={(e) => setTextInput(e.target.value)}
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: "10px",
            fontSize: "1rem",
          },
        }}
      />
      <StyledButton
        variant="contained"
        startIcon={<Check />}
        onClick={onAnalyze}
        sx={{ alignSelf: "flex-start" }}
      >
        Check Facts
      </StyledButton>
    </Box>
  );
};
TextTab.propTypes = {
  textInput: PropTypes.string.isRequired,
  setTextInput: PropTypes.func.isRequired,
  onAnalyze: PropTypes.func.isRequired,
};

export default TextTab;
