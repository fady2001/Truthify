import React from "react";
import PropTypes from "prop-types";
import { Box, Typography, Alert } from "@mui/material";
import { CloudUpload, Upload } from "@mui/icons-material";
import { StyledButton, FileUploadArea } from "../theme/theme";
import { useSnackbar } from "../contexts/snackbar";

const FileTab = ({ selectedFile, onFileSelect, onAnalyze }) => {
  const { openSnackbar } = useSnackbar();

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Check file size (limit to 10MB)
      if (file.size > 10 * 1024 * 1024) {
        openSnackbar("File size must be less than 10MB", "warning");
        return;
      }

      // Check file type
      const allowedTypes = [".pdf", ".docx", ".txt"];
      const fileExtension = "." + file.name.split(".").pop().toLowerCase();
      if (!allowedTypes.includes(fileExtension)) {
        openSnackbar("Please select a PDF, DOCX, or TXT file", "warning");
        return;
      }

      onFileSelect(event);
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, color: "#2c3e50" }}>
        Upload a file:
      </Typography>
      <FileUploadArea
        onClick={() => document.getElementById("file-input").click()}
      >
        <CloudUpload sx={{ fontSize: "3rem", color: "#bdc3c7", mb: 2 }} />
        <Typography variant="body1" sx={{ mb: 1 }}>
          Click to upload or drag and drop
        </Typography>
        <Typography variant="body2" sx={{ color: "#7f8c8d" }}>
          Supports: PDF, DOCX, TXT files
        </Typography>
      </FileUploadArea>
      <input
        type="file"
        id="file-input"
        accept=".pdf,.docx,.txt"
        style={{ display: "none" }}
        onChange={handleFileSelect}
      />
      {selectedFile && (
        <Alert severity="success" sx={{ borderRadius: "5px" }}>
          <strong>Selected:</strong> {selectedFile.name} (
          {formatFileSize(selectedFile.size)})
        </Alert>
      )}
      <StyledButton
        variant="contained"
        startIcon={<Upload />}
        onClick={onAnalyze}
        disabled={!selectedFile}
        sx={{ alignSelf: "flex-start" }}
      >
        Upload & Analyze
      </StyledButton>
    </Box>
  );
};
FileTab.propTypes = {
  selectedFile: PropTypes.object,
  onFileSelect: PropTypes.func.isRequired,
  onAnalyze: PropTypes.func.isRequired,
};

export default FileTab;
