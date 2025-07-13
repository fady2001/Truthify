import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

export const exportResultsToPDF = (results) => {
  const doc = new jsPDF();

  // Add title
  doc.setFontSize(18);
  doc.text("Fact-Check Results", 14, 22);

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
      `${fact.confidence}%`,
      sourcesText,
    ]);
  });

  // Add table of results
  autoTable(doc, {
    head: [["Claim", "Status", "Explanation", "Confidence", "Sources"]],
    body: tableData,
    startY: 30,
    styles: {
      cellPadding: 4,
      fontSize: 8,
      overflow: "linebreak",
      cellWidth: "wrap",
      valign: "top",
      lineColor: [220, 220, 220],
      lineWidth: 0.5,
    },
    headStyles: {
      fillColor: [22, 160, 133],
      textColor: [255, 255, 255],
      fontStyle: "bold",
      fontSize: 9,
    },
    alternateRowStyles: { fillColor: [248, 248, 248] },
    columnStyles: {
      0: { cellWidth: 40 }, // Claim
      1: { cellWidth: 18, halign: "center" }, // Status
      2: { cellWidth: 60 }, // Explanation
      3: { cellWidth: 15, halign: "center" }, // Confidence
      4: { cellWidth: 45 }, // Sources
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

  // Add sources section with clickable links
  const finalY = doc.lastAutoTable.finalY + 15;

  doc.setFontSize(14);
  doc.setTextColor(22, 160, 133);
  doc.text("Source Links", 14, finalY);

  let currentY = finalY + 10;
  doc.setFontSize(9);
  doc.setTextColor(0, 0, 0);

  results.facts.forEach((fact, factIndex) => {
    if (fact.sources && fact.sources.length > 0) {
      // Add fact claim as header
      doc.setFontSize(10);
      doc.setTextColor(52, 73, 94);
      doc.text(
        `Fact ${factIndex + 1}: ${fact.claim.substring(0, 60)}${
          fact.claim.length > 60 ? "..." : ""
        }`,
        14,
        currentY
      );
      currentY += 5;

      doc.setFontSize(9);
      doc.setTextColor(0, 100, 200); // Blue for links

      fact.sources.forEach((source, sourceIndex) => {
        const sourceUrl = source.url || source;
        const sourceTitle = source.title || source;

        if (sourceUrl && sourceUrl.startsWith("http")) {
          // Add clickable link
          const linkText = `${sourceIndex + 1}. ${sourceTitle}`;
          doc.link(14, currentY - 2, 180, 4, { url: sourceUrl });
          doc.text(linkText, 14, currentY);
        } else {
          doc.setTextColor(0, 0, 0);
          doc.text(`${sourceIndex + 1}. ${sourceTitle}`, 14, currentY);
          doc.setTextColor(0, 100, 200);
        }
        currentY += 4;
      });

      currentY += 3; // Space between facts
    }
  });

  // Add note about clickable links
  doc.setFontSize(8);
  doc.setTextColor(100, 100, 100);
  doc.text(
    "Note: Blue source links are clickable in PDF viewers that support interactive content.",
    14,
    currentY + 5
  );

  // Save the PDF
  doc.save("fact_check_results.pdf");
};
