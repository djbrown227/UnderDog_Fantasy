### Underdog Fantasy Positive Expected Value (EV) Betting Analyzer

#### Overview
This project aims to provide a tool for identifying Positive Expected Value (EV) bets on Underdog Fantasy, specifically focusing on Pickem games including Rivals and Higher Lower. By comparing the odds offered by Underdog Fantasy against those from sportsbook APIs such as Pinnacle, Draftkings, and Fanduel, users can identify potentially profitable betting opportunities.

#### Features
1. **Data Scraping:** The application scrapes available bets from Underdog Fantasy for both Rivals and Higher Lower games.
2. **Sportsbook Odds Comparison:** Accesses the-odds-api.com to retrieve player props odds from various sportsbooks, including Pinnacle, Draftkings, and Fanduel.
3. **EV Calculation:** Compares the odds offered by Underdog Fantasy with those from sportsbooks to calculate the Expected Value (EV) of each bet. Bets with positive EV indicate potentially profitable opportunities.
4. **Analysis for Different Game Types:** Provides EV analysis for both Higher/Lower and Rivals games on Underdog Fantasy.
5. **Visualization of +EV Bets:** Highlights which bets have a positive Expected Value, making it easier for users to identify potentially profitable wagers.
6. **Betting Slip Results Scraping:** Scrapes Underdog Fantasy for betting slip results, allowing users to track the outcomes of placed bets.
7. **Performance Tracking:** Calculates the percentage of correct bets for each sport in both Higher/Lower and Rivals over time, providing insights into the performance of the betting strategy.

#### Technologies Used
- Python for backend development and data processing.
- Beautiful Soup and Selenium for web scraping Underdog Fantasy.
- Flask for creating a web application interface.
- the-odds-api.com for accessing sportsbook odds.
- SQLite for data storage and management.
- Chart.js for data visualization.

#### How to Use
1. Clone the repository to your local machine.
2. Install the necessary dependencies listed in the requirements.txt file.
3. Run the application.
4. Access the web interface to view +EV bets, track betting performance, and analyze results.

#### Future Improvements
- Integration with more sportsbooks and additional betting markets.
- Improved user interface for easier navigation and analysis.
- Real-time updates on betting odds and game results.
- Incorporation of machine learning algorithms for enhanced bet selection strategies.

#### Acknowledgments
Special thanks to Underdog Fantasy and the-odds-api.com for providing the data and APIs necessary for this project.
