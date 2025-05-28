import React from "react";
import { Typography } from "@mui/material";
import {
  HeaderPaper,
  LogoContainer,
  LogoImage,
  LogoText,
} from "../theme/theme";
import truthifyLogo from "../assets/Icon removed bg.svg";
import truthifyText from "../assets/Truthify removed bg.svg";

const Header = () => {
  return (
    <HeaderPaper elevation={3}>
      <LogoContainer>
        <LogoImage src={truthifyLogo} alt="Truthify Logo" />
        <LogoText src={truthifyText} alt="Truthify Text" />
      </LogoContainer>
      <Typography variant="h6" sx={{ color: "#7f8c8d", fontSize: "1.1rem" }}>
        AI-Powered Fact Checking
      </Typography>
    </HeaderPaper>
  );
};

export default Header;
