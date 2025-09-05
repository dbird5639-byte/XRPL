@echo off
echo ========================================
echo XRP AI IDE Demo - Setup Script
echo ========================================
echo.

echo Installing dependencies...
npm install

echo.
echo Creating environment file...
if not exist .env (
    echo REACT_APP_OPENAI_API_KEY=your_openai_api_key_here > .env
    echo REACT_APP_XRP_NETWORK=testnet >> .env
    echo REACT_APP_XRP_TESTNET_URL=wss://s.altnet.rippletest.net:51233 >> .env
    echo Environment file created! Please edit .env with your actual API keys.
) else (
    echo Environment file already exists.
)

echo.
echo Setting up Tailwind CSS...
npx tailwindcss init -p

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your OpenAI API key
echo 2. Get XRP testnet account from: https://xrpl.org/xrp-testnet-faucet.html
echo 3. Run: npm start
echo.
echo Happy coding! 🚀
pause
