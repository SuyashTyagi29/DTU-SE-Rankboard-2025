# DTU Software Engineering Class of 2025 Rank Analyser
Felt quite bored and hence wanted to check where I stand in my branch, so built this basic web app that can help me in knowing so. 
Scraped all semester marksheets available on the [**DTU Examination**](https://exam.dtu.ac.in/result.htm) portal and combined them into a searchable, interactive rankboard.

##Scraping
Scraping was done using Python's pdfplumber library. It had to be done separately for semesters 1-2, 3-6 and 7-8, because of different pdf structures.

Scraping for semesters 1 and 2 had to be done in phases, simply because the first year roll numbers were differing, with most of the students being in different sections (for us, they were split across A13, A14, A15 and A1. Besides, there were some students who joined SE in their second year from different branches, hence they needed to be accounted for as well. I used a reference list of all SE students, available to us in a separate pdf, after all movements and merging had taken place. Additionally , certain students either dropped out or their results were not present in the pdf's, hence their data might not be available for necessary analysis (tough luck!).

##Building the App 
The app was built using Streamlit for the frontend component and Pandas for basic data handling.
**Key features:**

- Search by roll number to instantly view SGPA, credits, and semester-wise results.

- Branch-wide rank calculation based on total cumulative performance.

- Visual ranking chart using Plotly for quick position insight.

- Handles ties in ranks properly (same marks → same rank).
- Hosted via Streamlit Cloud.

##3Note 
Data is current up to the last marksheets published on DTU’s portal as of 26 June, 2025.

Ranks are purely based on available PDF data and any missing entries will obviously affect final standings. (Certain student's sgpa data might not be correct as well , as there were changes in their grade points after result re-evaluations, which were not taken into account for in this system) 

This app has been built entirely for fun and curiosity — not an official ranking system by any means. Contact DTU Admin/ SE HOD for the official data. 

Rest assured , this app can easily be scaled for other branches as well, which will allow us to derive further insights like overall university rankings, university leadarbords and average performance of other branches. 


Checkout the app : [*Link*](https://se-ranks-2025.streamlit.app/)
