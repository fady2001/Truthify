// SnackbarContext.jsx
import React, { createContext, useContext, useState, useMemo } from "react";
import PropTypes from "prop-types";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";

const SnackbarContext = createContext(undefined);

export const useSnackbar = () => {
  const context = useContext(SnackbarContext);
  if (!context) {
    throw new Error("useSnackbar must be used within a SnackbarProvider");
  }
  return context;
};

export const SnackbarProvider = ({ children }) => {
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  const openSnackbar = (message, severity = "success") => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  const value = useMemo(() => ({ openSnackbar }), [openSnackbar]);

  return (
    <SnackbarContext.Provider value={value}>
      {children}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert severity={snackbarSeverity} onClose={handleCloseSnackbar}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
};

SnackbarProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
