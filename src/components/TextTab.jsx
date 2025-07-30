import React from "react";
import PropTypes from "prop-types";
import { Box, Typography, TextField } from "@mui/material";
import { Check } from "@mui/icons-material";
import { StyledButton } from "../theme/theme";
import { useSnackbar } from "../contexts/snackbar";

const TextTab = ({ textInput, setTextInput, onAnalyze }) => {
  const { openSnackbar } = useSnackbar();

  const handleTextChange = (e) => {
    const text = e.target.value;
    setTextInput(text);

    // Provide feedback on text length
    if (text.length > 5000) {
      openSnackbar(
        "Text is quite long. Consider breaking it into smaller sections for better analysis.",
        "info"
      );
    }
  };

  const handleAnalyze = () => {
    if (!textInput.trim()) {
      openSnackbar("Please enter some text to analyze", "warning");
      return;
    }

    if (textInput.trim().length < 10) {
      openSnackbar("Please enter more text for meaningful analysis", "warning");
      return;
    }

    onAnalyze();
  };

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
        onChange={handleTextChange}
        sx={{
          "& .MuiOutlinedInput-root": {
            borderRadius: "10px",
            fontSize: "1rem",
          },
        }}
        helperText={`${textInput.length} characters`}
      />
      <StyledButton
        variant="contained"
        startIcon={<Check />}
        onClick={handleAnalyze}
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
