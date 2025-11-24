
# GitHub Agent (Auto-Collector)

An intelligent Python agent designed to automate the search, collection, and archiving of GitHub repositories based on specific keywords and popularity.

This tool is perfect for creating code datasets, researching specific implementations (e.g., "trading bots", "react portfolios"), or mass-downloading resources for offline analysis.

##  Features

* **Smart Search**: Uses the GitHub API to find the most relevant repositories (sorted by stars).
* **High-Speed Cloning**: Utilizes multi-threading to clone multiple repositories in parallel.
* **Auto-Cleaning**: Automatically removes \`.git\` history folders to significantly reduce file size.
* **Zip Archiving**: Compresses all downloaded projects into a single, clean \`.zip\` file.
* **Detailed Reporting**: Generates a text report listing all sources and statistics.

## Installation

1. Clone this repository:
   \`\`\`bash
   git clone https://github.com/Anwarito-lbd/Github-agent.git
   cd Github-agent
   \`\`\`

2. Install the required dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

##  Usage

Simply run the script using Python:

\`\`\`bash
python github_agent.py
\`\`\`

The agent is **interactive** and will guide you through the process:

1. **GitHub Token**: (Optional) Enter your Personal Access Token to avoid API rate limits.
2. **Search Query**: Enter what you are looking for (e.g., \`xauusd trading strategy\`, \`django ecommerce\`, \`machine learning\`).
3. **Quantity**: Enter the number of repositories you wish to download.

📂 **Output**: You will find a timestamped \`.zip\` file containing all the source code in the \`github_agent_downloads\` directory.

##  How to get a Token (Recommended)

To download more than a few repositories without hitting GitHub's API limits:
1. Go to [GitHub Developer Settings](https://github.com/settings/tokens).
2. Click **"Generate new token (classic)"**.
3. Select the \`public_repo\` scope.
4. Copy the token and paste it when the script asks.

##  Disclaimer

This tool is intended for educational and research purposes only. Please respect the licenses of the repositories you download. Do not use this tool to spam the GitHub API.

