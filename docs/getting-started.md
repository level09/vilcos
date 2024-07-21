# Setting up Vilcos

## Clone the repo

```
$ git clone https://github.com/level09/vilcos.git
$ cd vilcos
```

## Initialize a virtualenv

```
$ python3 -m venv env
$ source env/bin/activate
```

## Add Environment Variables

Copy `.env.example` to `.env` and modify the settings to your needs.

You'll need to set up your Supabase project and add the following environment variables:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase project API key

You can generate a secret key for Flask using the following command:

```python
import secrets
secrets.token_urlsafe(16)
```

Add this generated key to your `.env` file as `SECRET_KEY`.

**Note: Do not include the `.env` file in any commits. This should remain private.**

## Install the dependencies

```
$ pip install -r requirements.txt
```

## Frontend setup (if using Vue)

If you're using Vue for the frontend:

```
$ cd frontend
$ npm install
```

## Running the app

```
$ source env/bin/activate
$ flask run
```

This will start the Flask development server. By default, you can access the application at `http://localhost:5000`.

## Running the frontend (if using Vue)

In a separate terminal:

```
$ cd frontend
$ npm run serve
```

This will start the Vue development server. You can access the frontend at the URL provided in the console output.

## Supabase Setup

1. Create a new project in your Supabase dashboard.
2. In the "Authentication" section, enable the authentication methods you want to use (e.g., email/password, social logins).
3. Copy your project's URL and API key from the Supabase dashboard and add them to your `.env` file.

For more detailed instructions on setting up and using Supabase, refer to the [Supabase documentation](https://supabase.io/docs).

## Deployment

Deployment instructions will vary depending on your hosting provider. Make sure to set up your environment variables (including Supabase credentials) on your production server.

Remember to use a production-ready server like Gunicorn instead of the Flask development server when deploying to production.

## Troubleshooting

If you encounter any issues during setup, please check the following:

1. Ensure all environment variables are correctly set in your `.env` file.
2. Make sure you're using the correct versions of Python and Node.js as specified in the project requirements.
3. Check that your Supabase project is correctly set up and the API credentials are valid.

If problems persist, please open an issue on the GitHub repository.