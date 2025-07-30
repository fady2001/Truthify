import React from "react";
import PropTypes from "prop-types";
import { Box, Typography, CardContent, Chip, Link } from "@mui/material";
import { CheckCircle, Cancel, Help, OpenInNew } from "@mui/icons-material";
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
        <Box
          sx={{
            display: "flex",
            flexWrap: "wrap",
            gap: 1,
            alignItems: "center",
          }}
        >
          {fact.sources && fact.sources.length > 0 && (
            <>
              <Typography
                variant="body2"
                sx={{ color: "#7f8c8d", fontWeight: 600 }}
              >
                Sources:
              </Typography>
              {fact.sources.map((source, sourceIndex) => (
                <Link
                  key={sourceIndex}
                  href={source.url || source}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    textDecoration: "none",
                    "&:hover": {
                      textDecoration: "underline",
                    },
                  }}
                >
                  <Chip
                    label={source.title || source}
                    size="small"
                    variant="outlined"
                    clickable
                    icon={<OpenInNew sx={{ fontSize: "0.8rem" }} />}
                    sx={{
                      color: "#3498db",
                      borderColor: "#3498db",
                      cursor: "pointer",
                      "&:hover": {
                        backgroundColor: "rgba(52, 152, 219, 0.1)",
                        transform: "translateY(-1px)",
                        boxShadow: "0 2px 8px rgba(52, 152, 219, 0.2)",
                      },
                      transition: "all 0.2s ease",
                    }}
                  />
                </Link>
              ))}
            </>
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
    sources: PropTypes.arrayOf(
      PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.shape({
          title: PropTypes.string.isRequired,
          url: PropTypes.string.isRequired,
        }),
      ])
    ),
  }),
  index: PropTypes.number.isRequired,
};

export default FactItem;
