import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import font from "../assets/amiri";

export const exportResultsToPDF = (results) => {
  const doc = new jsPDF("landscape");
  const pageHeight = doc.internal.pageSize.height;
  const pageWidth = doc.internal.pageSize.width;
  const margin = 14;
  const bottomMargin = 20;

  // Add title
  doc.setFontSize(20);
  doc.text("Fact-Check Results", margin, 22);
  doc.addFileToVFS("Amiri-Regular-normal.ttf", font);
  doc.addFont("Amiri-Regular-normal.ttf", "Amiri-Regular", "normal");
  doc.setFont("Amiri-Regular");
  
  // Prepare table data with properly formatted sources
  const tableData = [];

  results.facts.forEach((fact) => {
    // Format sources as a single string with line breaks
    let sourcesText = "";
    if (fact.sources && fact.sources.length > 0) {
      sourcesText = fact.sources
        .map((source, idx) => {
          return `${idx + 1}. ${source.title || source}`;
        })
        .join("\n");
    } else {
      sourcesText = "No sources available";
    }

    // Add main fact row with all information
    tableData.push([
      fact.claim,
      fact.status.toUpperCase(),
      fact.explanation,
      sourcesText,
    ]);
  });

  // Add table of results
  autoTable(doc, {
    head: [["Claim", "Status", "Explanation", "Sources"]],
    body: tableData,
    startY: 30,
showHead: "everyPage", // Show header on every page
    margin: { top: 30, right: margin, bottom: bottomMargin, left: margin },
    styles: {
      cellPadding: 4,
      fontSize: 8,
      overflow: "linebreak",
      cellWidth: "wrap",
      valign: "top",
      lineColor: [220, 220, 220],
      lineWidth: 0.5,
        font: "Amiri-Regular",
          textColor: "black",
    },

    headStyles: {
      fillColor: [22, 160, 133],
      textColor: [255, 255, 255],
      fontStyle: "bold",
      fontSize: 9,
    },
    alternateRowStyles: { fillColor: [248, 248, 248] },
    columnStyles: {
      0: { cellWidth: 60 }, // Claim - increased width for landscape
      1: { cellWidth: 30, halign: "center" }, // Status
      2: { cellWidth: 80 }, // Explanation - increased width
      3: { cellWidth: 60 }, // Sources - fixed index from 4 to 3
    },
    didDrawCell: function (data) {
      // Add clickable links for sources column
      if (data.column.index === 4 && data.section === "body") {
        const fact = results.facts[data.row.index];
        if (fact.sources && fact.sources.length > 0) {
          let yOffset = 2;
          fact.sources.forEach((source, sourceIndex) => {
            const sourceUrl = source.url || source;
            if (sourceUrl && sourceUrl.startsWith("http")) {
                      // Calculate position for each source line
              const lineHeight = 3;
              const linkY = data.cell.y + yOffset + sourceIndex * lineHeight;

              doc.link(
                data.cell.x + 2,
                linkY,
                data.cell.width - 4,
                lineHeight,
                { url: sourceUrl }
              );
            }
          });
        }
      }
    },
  });

  // Check if we need a new page for sources section
  let currentY = doc.lastAutoTable.finalY + 15;

  // Function to check if we need a new page
  const checkPageBreak = (additionalHeight = 20) => {
    if (currentY + additionalHeight > pageHeight - bottomMargin) {
      doc.addPage();
      currentY = 30; // Reset Y position with top margin
      return true;
    }
    return false;
  };

  // Add sources section with proper pagination
  checkPageBreak(20);
  doc.setFontSize(14);
  doc.setTextColor(22, 160, 133);
  doc.text("Source Links", margin, currentY);
  currentY += 10;

  doc.setFontSize(9);
  doc.setTextColor(0, 0, 0);

  results.facts.forEach((fact, factIndex) => {
    if (fact.sources && fact.sources.length > 0) {
// Calculate space needed for this fact section
      const spaceNeeded = 5 + fact.sources.length * 4 + 3;
      checkPageBreak(spaceNeeded);

      // Add fact claim as header
      doc.setFontSize(10);
      doc.setTextColor(52, 73, 94);
      doc.text(
        `Fact ${factIndex + 1}: ${fact.claim.substring(0, 80)}${
          fact.claim.length > 80 ? "..." : ""
        }`,
        margin,
        currentY
      );
      currentY += 5;

      doc.setFontSize(9);
      doc.setTextColor(0, 100, 200); // Blue for links

      fact.sources.forEach((source, sourceIndex) => {
        checkPageBreak(6);
        const sourceUrl = source.url || source;
        const sourceTitle = source.title || source;

        if (sourceUrl && sourceUrl.startsWith("http")) {
                    const linkText = `${sourceIndex + 1}. ${sourceTitle}`;
          doc.link(
            margin,
            currentY - 2,
            pageWidth - margin * 2,
            4,
{ url: sourceUrl }
);
          doc.text(linkText, margin, currentY);
        } else {
          doc.setTextColor(0, 0, 0);
          doc.text(`${sourceIndex + 1}. ${sourceTitle}`, margin, currentY);
          doc.setTextColor(0, 100, 200);
        }
        currentY += 4;
      });

      currentY += 3; // Space between facts
    }
  });

  // Add note about clickable links
checkPageBreak(10);
  doc.setFontSize(8);
  doc.setTextColor(100, 100, 100);
  doc.text(
    "Note: Blue source links are clickable in PDF viewers that support interactive content.",
    margin,
    currentY + 5
  );

  // Save the PDF
  doc.save("fact_check_results.pdf");
};
