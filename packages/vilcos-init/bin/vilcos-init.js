#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Configure interactive prompt
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// ANSI color codes
const colors = {
  blue: '\x1b[34m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  reset: '\x1b[0m'
};

// Print banner
console.log(`${colors.blue}
╔═════════════════════════════════════════════════════════════╗
║                 VILCOS WEBSITE BUILDER                      ║
║         AI-Powered Website Template Management              ║
╚═════════════════════════════════════════════════════════════╝
${colors.reset}`);

// Main function
async function init() {
  const projectName = process.argv[2] || '.';
  const targetDir = projectName === '.' ? process.cwd() : path.join(process.cwd(), projectName);
  
  try {
    // Create directory if it doesn't exist
    if (projectName !== '.') {
      if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
        console.log(`${colors.green}Created directory: ${targetDir}${colors.reset}`);
      }
      process.chdir(targetDir);
    }
    
    // Clone the repository
    console.log(`${colors.yellow}Cloning Vilcos repository...${colors.reset}`);
    execSync('git clone https://github.com/level09/vilcos.git .', { stdio: 'inherit' });
    
    // Ask for OpenAI API key
    rl.question(`${colors.yellow}Enter your OpenAI API key (press Enter to skip): ${colors.reset}`, (apiKey) => {
      if (apiKey) {
        fs.writeFileSync('.env', `OPENAI_API_KEY=${apiKey}`);
        console.log(`${colors.green}API key saved to .env file${colors.reset}`);
      } else {
        console.log(`${colors.yellow}No API key provided. You'll be prompted for it when starting Vilcos.${colors.reset}`);
      }
      
      // Install dependencies
      console.log(`${colors.yellow}Installing dependencies...${colors.reset}`);
      execSync('./vilcos install', { stdio: 'inherit' });
      
      console.log(`
${colors.green}✅ Vilcos has been successfully installed!${colors.reset}

To start Vilcos, run:
  ${colors.blue}cd ${projectName === '.' ? '.' : projectName}
  ./vilcos start${colors.reset}

This will start:
  - AI Management: http://localhost:8000 (login: admin/password)
  - Website Preview: http://localhost:3000
      `);
      
      rl.close();
    });
  } catch (error) {
    console.error(`${colors.red}Error: ${error.message}${colors.reset}`);
    process.exit(1);
  }
}

init(); 