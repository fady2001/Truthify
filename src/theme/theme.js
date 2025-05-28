import { createTheme } from "@mui/material/styles";
import { styled } from "@mui/material";
import { Container, Paper, Box, Button, Card } from "@mui/material";

// Custom theme to match the original design
export const theme = createTheme({
  palette: {
    primary: {
      main: "#3498db",
    },
    secondary: {
      main: "#2980b9",
    },
    background: {
      default: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    },
  },
  typography: {
    fontFamily: "Segoe UI, Tahoma, Geneva, Verdana, sans-serif",
  },
});

// Styled components to match the original design
export const StyledContainer = styled(Container)(() => ({
  minHeight: "100vh",
  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  padding: "20px",
}));

export const HeaderPaper = styled(Paper)(() => ({
  textAlign: "center",
  marginBottom: "40px",
  background: "rgba(255, 255, 255, 0.95)",
  padding: "30px",
  borderRadius: "20px",
  boxShadow: "0 10px 30px rgba(0, 0, 0, 0.1)",
}));

export const LogoContainer = styled(Box)(() => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: "15px",
  marginBottom: "10px",
}));

export const LogoImage = styled("img")(() => ({
  height: "60px",
  width: "auto",
}));

export const LogoText = styled("img")(() => ({
  height: "50px",
  width: "auto",
}));

export const MainPaper = styled(Paper)(() => ({
  background: "rgba(255, 255, 255, 0.95)",
  borderRadius: "20px",
  padding: "40px",
  boxShadow: "0 10px 30px rgba(0, 0, 0, 0.1)",
}));

export const StyledButton = styled(Button)(() => ({
  background: "linear-gradient(135deg, #3498db, #2980b9)",
  borderRadius: "50px",
  padding: "15px 30px",
  fontSize: "1rem",
  boxShadow: "0 5px 15px rgba(52, 152, 219, 0.3)",
  "&:hover": {
    transform: "translateY(-2px)",
    boxShadow: "0 8px 25px rgba(52, 152, 219, 0.4)",
  },
}));

export const FileUploadArea = styled(Box)(() => ({
  border: "3px dashed #bdc3c7",
  borderRadius: "10px",
  padding: "40px",
  textAlign: "center",
  cursor: "pointer",
  transition: "all 0.3s ease",
  marginBottom: "15px",
  "&:hover": {
    borderColor: "#3498db",
    backgroundColor: "#f8f9fa",
  },
}));

export const FactItemCard = styled(Card)(({ status }) => ({
  marginBottom: "15px",
  borderLeft: `4px solid ${
    status === "verified"
      ? "#27ae60"
      : status === "false"
      ? "#e74c3c"
      : "#f39c12"
  }`,
  boxShadow: "0 2px 10px rgba(0, 0, 0, 0.1)",
}));
