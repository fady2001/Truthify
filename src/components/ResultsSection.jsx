import React from "react";
import PropTypes from "prop-types";
import { Box, Typography, CircularProgress, Alert } from "@mui/material";
import FactItem from "./FactItem";

const ResultsSection = ({ showResults, loading, results }) => {
  if (!showResults) return null;

  return (
    <Box sx={{ mt: 5, pt: 4, borderTop: "2px solid #ecf0f1" }}>
      <Typography variant="h5" sx={{ color: "#2c3e50", mb: 3 }}>
        Fact-Check Results
      </Typography>

      {loading && (
        <Box sx={{ textAlign: "center", py: 5, color: "#7f8c8d" }}>
          <CircularProgress size={40} sx={{ mb: 2 }} />
          <Typography variant="body1">Analyzing content...</Typography>
        </Box>
      )}

      {!loading && results && (
        <Box
          sx={{
            background: "#f8f9fa",
            borderRadius: "10px",
            padding: "20px",
            minHeight: "200px",
          }}
        >
          {results.error ? (
            <Alert severity="error" sx={{ borderRadius: "8px" }}>
              {results.error}
            </Alert>
          ) : results.facts && results.facts.length > 0 ? (
            results.facts.map((fact, index) => (
              <FactItem key={index} fact={fact} index={index} />
            ))
          ) : (
            <Typography variant="body1">
              No fact-checking results found.
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};
ResultsSection.propTypes = {
  showResults: PropTypes.bool.isRequired,
  loading: PropTypes.bool.isRequired,
  results: PropTypes.shape({
    error: PropTypes.string,
    facts: PropTypes.arrayOf(PropTypes.object),
  }),
};

export default ResultsSection;
