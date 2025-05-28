import React from "react";
import PropTypes from "prop-types";
import { Box, Typography, CardContent, Chip } from "@mui/material";
import { CheckCircle, Cancel, Help } from "@mui/icons-material";
import { FactItemCard } from "../theme/theme";

const FactItem = ({ fact, index }) => {
  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case "true":
      case "verified":
      case "correct":
        return <CheckCircle sx={{ color: "#27ae60" }} />;
      case "false":
      case "incorrect":
      case "misleading":
        return <Cancel sx={{ color: "#e74c3c" }} />;
      default:
        return <Help sx={{ color: "#f39c12" }} />;
    }
  };

  return (
    <FactItemCard key={index} status={fact.status?.toLowerCase()}>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          {getStatusIcon(fact.status)}
          <Typography variant="h6" component="div">
            {fact.claim || "Claim"}
          </Typography>
        </Box>
        <Typography variant="body1" sx={{ mb: 2, color: "#555" }}>
          {fact.explanation || "No explanation provided."}
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          <Chip
            label={`Confidence: ${fact.confidence || "N/A"}%`}
            size="small"
            variant="outlined"
          />
          {fact.sources && fact.sources.length > 0 && (
            <Chip
              label={`Sources: ${fact.sources.join(", ")}`}
              size="small"
              variant="outlined"
            />
          )}
        </Box>
      </CardContent>
    </FactItemCard>
  );
};
FactItem.propTypes = {
  fact: PropTypes.shape({
    status: PropTypes.string,
    claim: PropTypes.string,
    explanation: PropTypes.string,
    confidence: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    sources: PropTypes.arrayOf(PropTypes.string),
  }),
  index: PropTypes.number.isRequired,
};

export default FactItem;
