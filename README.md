# Vilcos Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Vilcos is a modern, Flask-based web framework designed for rapid development of web applications and APIs. It leverages the power of Supabase for backend services, providing a seamless authentication system out of the box.

## Features

- Built on Flask, a lightweight and flexible Python web framework
- Integrates Supabase for authentication and backend services
- Vue 3 and Vuetify 3 integration for responsive front-end development
- Simplified setup and configuration

## Prerequisites

- Python 3.7+
- Supabase account and project
- Node.js and npm (for front-end development)

## Quick Start

1. Clone the repository:
   ```
   git clone https://github.com/level09/vilcos.git
   cd vilcos
   ```

2. Set up a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Set up your Supabase environment variables:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file and add your Supabase URL and API key.

4. Run the development server:
   ```
   flask run
   ```

## Supabase Authentication

Vilcos uses Supabase for authentication. The integration allows for:

- User sign-up and sign-in
- Password reset functionality
- Session management

For more details on how to use Supabase auth in your Vilcos project, refer to the documentation.

## Contributing

Contributions to Vilcos are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.