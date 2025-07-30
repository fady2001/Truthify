// Dummy data generators for different content types
export const generateYouTubeData = () => ({
  facts: [
    // make one in arabic
    {
      timestamp: 0, // 0:00
      claim: "التغير المناخي ناتج عن الأنشطة البشرية",
      status: "verified",
      explanation:
        "هذا الادعاء مدعوم بأدلة علمية قوية. تؤكد الهيئ الدولية للتغير المناخي والعديد من الدراسات التي تمت مراجعتها من قبل الأقران أن الأنشطة البشرية هي المحرك الرئيسي للتغير المناخي الحديث.",
      sources: [
        {
          title: "تقرير الهيئة الدولية للتغير المناخي السادس",
          url: "https://www.ipcc.ch/report/ar6/wg1/",
        },
      ],
    },
    {
      timestamp: 30, // 0:30
      claim: "Climate change is caused by human activities",
      status: "verified",
      explanation:
        "This claim is supported by overwhelming scientific evidence. The IPCC and numerous peer-reviewed studies confirm that human activities are the primary driver of recent climate change.",
      sources: [
        {
          title: "IPCC Sixth Assessment Report",
          url: "https://www.ipcc.ch/report/ar6/wg1/",
        },
      ],
    },
    {
      timestamp: 120, // 2:00
      claim: "Electric vehicles produce zero emissions",
      status: "false",
      explanation:
        "While EVs produce no direct emissions, they may have indirect emissions from electricity generation and battery manufacturing. However, they are still significantly cleaner overall.",
      sources: [
        {
          title: "EPA Electric Vehicle Analysis",
          url: "https://www.epa.gov/greenvehicles/electric-vehicle-myths",
        },
      ],
    },
    {
      timestamp: 200, // 3:20
      claim: "Renewable energy costs are decreasing rapidly",
      status: "verified",
      explanation:
        "Multiple studies show that renewable energy costs have decreased significantly over the past decade. Solar and wind are now among the cheapest electricity sources.",
      sources: [
        {
          title: "IRENA Global Energy Report",
          url: "https://www.irena.org/publications/2023/Jun/Global-Energy-Transformation",
        },
      ],
    },
    {
      timestamp: 300, // 5:00
      claim: "AI will replace all human jobs",
      status: "unknown",
      explanation:
        "While AI is advancing rapidly, the extent to which it will replace human jobs is debated. Many experts suggest AI will transform rather than completely replace most jobs.",
      sources: [
        {
          title: "MIT Technology Review: AI and Jobs",
          url: "https://www.technologyreview.com/topic/artificial-intelligence/",
        },
      ],
    },
  ],
});

export const generateTextData = () => ({
  facts: [
    {
      claim: "The Great Wall of China is visible from space",
      status: "false",
      explanation:
        "This is a common myth. The Great Wall of China is not visible from space with the naked eye. This misconception has been debunked by astronauts and space agencies multiple times.",
      sources: [
        {
          title: "NASA Space Myths Debunked",
          url: "https://www.nasa.gov/audience/forstudents/k-4/stories/nasa-knows/what-is-the-great-wall-of-china-k4.html",
        },
        {
          title: "ESA Astronaut Reports",
          url: "https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Research/Great_Wall_of_China",
        },
        {
          title: "Snopes Great Wall Fact Check",
          url: "https://www.snopes.com/fact-check/great-wall-of-china-visible-from-space/",
        },
      ],
    },
    {
      claim: "Drinking 8 glasses of water daily is necessary for health",
      status: "unknown",
      explanation:
        "While staying hydrated is important, the '8 glasses per day' rule lacks strong scientific backing. Water needs vary based on individual factors like activity level, climate, and overall health.",
      sources: [
        {
          title: "Mayo Clinic: Water Intake Recommendations",
          url: "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256",
        },
        {
          title: "Harvard Health: How Much Water Should You Drink?",
          url: "https://www.health.harvard.edu/staying-healthy/how-much-water-should-you-drink",
        },
      ],
    },
    {
      claim: "Artificial intelligence is advancing rapidly",
      status: "verified",
      explanation:
        "This statement is accurate. AI technology has shown exponential growth in recent years, with significant breakthroughs in machine learning, natural language processing, and computer vision.",
      sources: [
        {
          title: "MIT Technology Review: AI Progress",
          url: "https://www.technologyreview.com/topic/artificial-intelligence/",
        },
        {
          title: "Nature AI Research",
          url: "https://www.nature.com/natmachintell/",
        },
        {
          title: "Stanford AI Index Report 2024",
          url: "https://aiindex.stanford.edu/report/",
        },
      ],
    },
  ],
});

export const generateFileData = () => ({
  facts: [
    {
      claim: "Electric vehicles have zero emissions",
      status: "false",
      explanation:
        "While electric vehicles produce no direct emissions, they may have indirect emissions from electricity generation and battery manufacturing. However, they are still significantly cleaner than conventional vehicles overall.",
      sources: [
        {
          title: "EPA Electric Vehicle Emissions Report",
          url: "https://www.epa.gov/greenvehicles/electric-vehicle-myths",
        },
        {
          title: "Union of Concerned Scientists EV Analysis",
          url: "https://www.ucsusa.org/clean-vehicles/electric-vehicles",
        },
        {
          title: "Carbon Brief: Electric Car Life Cycle",
          url: "https://www.carbonbrief.org/factcheck-how-electric-vehicles-help-to-tackle-climate-change/",
        },
      ],
    },
    {
      claim: "Exercise improves mental health",
      status: "verified",
      explanation:
        "Numerous scientific studies have demonstrated that regular physical exercise has positive effects on mental health, including reducing symptoms of depression and anxiety while improving mood and cognitive function.",
      sources: [
        {
          title: "American Psychological Association: Exercise & Mental Health",
          url: "https://www.apa.org/topics/exercise-fitness/mental-health",
        },
        {
          title: "Journal of Clinical Psychiatry Study",
          url: "https://www.psychiatrist.com/jcp/exercise-depression-anxiety/",
        },
        {
          title: "Harvard Medical School: Exercise & Depression",
          url: "https://www.health.harvard.edu/mind-and-mood/exercise-is-an-all-natural-treatment-to-fight-depression",
        },
      ],
    },
    {
      claim: "Quantum computers will replace all traditional computers",
      status: "unknown",
      explanation:
        "While quantum computers show promise for specific applications, it's unclear if or when they might replace traditional computers entirely. Current quantum computers are specialized tools rather than general-purpose replacements.",
      sources: [
        {
          title: "IBM Quantum Computing Overview",
          url: "https://www.ibm.com/quantum-computing/",
        },
        {
          title: "MIT Technology Review: Quantum Computing Reality",
          url: "https://www.technologyreview.com/topic/computing/quantum-computing/",
        },
        {
          title: "Nature Quantum Information",
          url: "https://www.nature.com/npjqi/",
        },
      ],
    },
    {
      claim: "Social media usage is linked to mental health issues",
      status: "verified",
      explanation:
        "Research has shown correlations between excessive social media use and various mental health concerns, including increased rates of anxiety, depression, and body image issues, particularly among adolescents.",
      sources: [
        {
          title: "American Academy of Pediatrics: Social Media Guidelines",
          url: "https://www.aap.org/en/patient-care/media-and-children/social-media/",
        },
        {
          title: "Journal of Social Media Research",
          url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6214874/",
        },
        {
          title: "Pew Research: Social Media & Mental Health",
          url: "https://www.pewresearch.org/internet/2022/08/10/teens-social-media-and-technology-2022/",
        },
      ],
    },
  ],
});
